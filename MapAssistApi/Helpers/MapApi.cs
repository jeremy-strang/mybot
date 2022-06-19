using MapAssist.Settings;
using MapAssist.Types;
using Microsoft.Win32;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using System;
using System.Collections.Concurrent;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Runtime.InteropServices;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using System.Windows.Forms;
using Path = System.IO.Path;

#pragma warning disable 649

namespace MapAssist.Helpers
{
    public class MapApi
    {
        private static readonly NLog.Logger _log = NLog.LogManager.GetCurrentClassLogger();
        private static Process _pipeClient;
        private static readonly object _pipeRequestLock = new object();
        private const string _procName = "MAServer.exe";

        private readonly ConcurrentDictionary<Area, AreaData> _cache;
        private GameData _gameData;

        private static int trailingSlash = -1; // -1 = Still trying to figure out, 0 = remove trailing slash, 1 = required trailing slash
        private static int trailingSlashTry = 0; // Which trailing slash preference to try

        private static readonly Dictionary<string, uint> GameCRC32 = new Dictionary<string, uint> {
            {"1.11a", 0xf44cd0cf },
            {"1.11b", 0x8fd3f392 },
            {"1.12a", 0xab566eaa },
            {"1.13c", 0xea2f0e6e },
            {"1.13d", 0xb3d69c47 },
        };

        private static readonly Dictionary<string, uint> StormCRC32 = new Dictionary<string, uint> {
            {"1.11a", 0x9f06891d },
            {"1.11b", 0xb6390775 },
            {"1.12a", 0xe5b0f351 },
            {"1.13c", 0x5711a8b4 },
            {"1.13d", 0xbdb6784e }
        };

        public static bool StartPipedChild()
        {
            // We have an exclusive lock on the MA process.
            // So we can kill off any previously lingering map servers
            // in case we had a weird shutdown that didn't clean up appropriately.
            StopPipeServers();

            var procFile = Path.Combine(Environment.CurrentDirectory, _procName);
            if (!File.Exists(procFile))
            {
                throw new Exception("Unable to start map server. Check Anti Virus settings.");
            }

            var path = FindD2LoD();

            if (trailingSlash == 0 || trailingSlashTry == 0) // Remove trailing slash
            {
                path = path.TrimEnd('\\');
            }
            else if (trailingSlash == 1 || trailingSlashTry == 1) // Require trailing slash
            {
                path = path.TrimEnd('\\') + "\\";
            }

            _pipeClient = new Process();
            _pipeClient.StartInfo.FileName = procFile;
            _pipeClient.StartInfo.Arguments = "\"" + path + "\"";
            _pipeClient.StartInfo.UseShellExecute = false;
            _pipeClient.StartInfo.RedirectStandardOutput = true;
            _pipeClient.StartInfo.RedirectStandardInput = true;
            _pipeClient.StartInfo.RedirectStandardError = true;
            _pipeClient.Start();

            var (startupLength, _) = MapApiRequest().Result;
            _log.Info($"{_procName} has started");

            return startupLength == 0;
        }

        private static string FindD2LoD()
        {
            while (true)
            {
                var providedPath = MapAssistConfiguration.Loaded.D2LoDPath;
                if (!string.IsNullOrEmpty(providedPath))
                {
                    if (IsValidD2LoDPath(providedPath))
                    {
                        _log.Info("User provided D2 LoD path is valid");
                        return providedPath;
                    }
                    else
                    {
                        _log.Info("User provided D2 LoD path not found or invalid");
                        var diabloResult = MessageBox.Show("Provided D2 LoD path is not valid." + Environment.NewLine + Environment.NewLine + "Please provide a path to a D2 LoD 1.13c installation.", "MapAssist", MessageBoxButtons.OKCancel);

                        if (diabloResult == DialogResult.Cancel)
                        {
                            Environment.Exit(0);
                        }

                        //var config = new ConfigEditor();
                        //config.ShowDialog();

                        continue;
                    }
                }

                var installPath = Registry.GetValue("HKEY_CURRENT_USER\\SOFTWARE\\Blizzard Entertainment\\Diablo II", "InstallPath", "INVALID") as string;
                if (installPath == "INVALID" || !IsValidD2LoDPath(installPath))
                {
                    _log.Info("Registry provided D2 LoD path not found or invalid");
                    MessageBox.Show("Unable to automatically locate D2 LoD installation." + Environment.NewLine + Environment.NewLine + "Please provide a path to a D2 LoD 1.13c installation.", "MapAssist");

                    //var config = new ConfigEditor();
                    //config.ShowDialog();

                    continue;
                }

                _log.Info("Registry provided D2 LoD path is valid");
                return installPath;
            }
        }

        private static bool IsValidD2LoDPath(string path)
        {
            try
            {
                if (string.IsNullOrEmpty(path)) return false;
                if (!File.GetAttributes(path).HasFlag(FileAttributes.Directory)) return false;

                var gamePath = Path.Combine(path, "game.exe");
                if (File.Exists(gamePath))
                {
                    var fileChecksum = Files.Checksum.FileChecksum(gamePath);
                    var versionInfo = FileVersionInfo.GetVersionInfo(gamePath);

                    _log.Info($"Found Game.exe (CRC 0x{fileChecksum:X}, Version {versionInfo.FileVersion.Replace(", ", ".")})");

                    foreach (KeyValuePair<string, uint> kvp in GameCRC32)
                    {
                        var allowedChecksum = kvp.Value;
                        if (fileChecksum == allowedChecksum)
                        {
                            _log.Info($"Valid D2 LoD version identified by Game.exe - v{kvp.Key}");
                            return true;
                        }
                    }
                }
                else
                {
                    gamePath = Path.Combine(path, "storm.dll");
                    if (File.Exists(gamePath))
                    {
                        var fileChecksum = Files.Checksum.FileChecksum(gamePath);
                        var versionInfo = FileVersionInfo.GetVersionInfo(gamePath);

                        _log.Info($"Found Storm.dll (CRC 0x{fileChecksum:X}, Version {versionInfo.FileVersion.Replace(", ", ".")})");

                        foreach (KeyValuePair<string, uint> kvp in StormCRC32)
                        {
                            var allowedChecksum = kvp.Value;
                            if (fileChecksum == allowedChecksum)
                            {
                                _log.Info($"Valid D2 LoD version identified by Storm.dll - v{kvp.Key}");
                                return true;
                            }
                        }
                    }
                }
                return false;
            }
            catch (Exception)
            {
                return false;
            }
        }

        private static async Task<(uint, string)> MapApiRequest(byte[] writeBytes = null, int timeout = 1000)
        {
            if (_pipeClient.HasExited)
            {
                _log.Warn($"{_procName} has exited unexpectedly with exit code {_pipeClient.ExitCode} (0x{_pipeClient.ExitCode.ToString("x")})");
            }

            if (disposed || _pipeClient.HasExited)
            {
                return (0, null);
            }

            var pipeInput = _pipeClient.StandardInput;
            var pipeOutput = _pipeClient.StandardOutput;

            Func<int, Task<byte[]>> ReadBytes = async (readBytesLength) =>
            {
                var data = new byte[0];
                var cts = new CancellationTokenSource(timeout);

                while (!disposed && !_pipeClient.HasExited && !cts.IsCancellationRequested && data.Length < readBytesLength)
                {
                    var tryReadLength = readBytesLength - data.Length;
                    var chunk = new byte[tryReadLength];
                    var dataReadLength = await pipeOutput.BaseStream.ReadAsync(chunk, 0, tryReadLength, cts.Token);

                    data = Combine(data, chunk.Take(dataReadLength).ToArray());
                }

                if (disposed) _log.Warn($"{_procName} has been disposed");
                else if (_pipeClient.HasExited) _log.Warn($"{_procName} has exited unexpectedly with exit code {_pipeClient.ExitCode} (0x{_pipeClient.ExitCode.ToString("x")})");
                else if (cts.IsCancellationRequested) _log.Warn($"{_procName} request has been cancelled");

                var response = !disposed && !_pipeClient.HasExited && !cts.IsCancellationRequested ? data : null;
                cts.Dispose();
                return response;
            };

            Func<int, Task<byte[]>> TryReadBytes = async (readBytesLength) =>
            {
                var task = ReadBytes(readBytesLength);
                var result = await Task.WhenAny(task, Task.Delay(timeout));
                if (result == task)
                {
                    return await task;
                }
                else
                {
                    _log.Warn($"Request timed out after {timeout} ms");
                    return null;
                }
            };

            if (writeBytes != null)
            {
                pipeInput.BaseStream.Write(writeBytes, 0, writeBytes.Length);
                pipeInput.BaseStream.Flush();
            }

            var readLength = await TryReadBytes(4);
            if (readLength == null) return (0, null);
            var length = BitConverter.ToUInt32(readLength, 0);

            if (length == 0)
            {
                return (0, null);
            }

            if (length == uint.MaxValue) // Try a different trailing slash logic
            {
                trailingSlashTry++;
            }
            else if (length > 0) // Trailing slash attempt worked and keep that logic for future requests
            {
                trailingSlash = trailingSlashTry;
            }

            string json = null;
            JObject jsonObj;
            try
            {
                //_log.Info($"Reading {length} bytes from {_procName}");
                var readJson = await TryReadBytes((int)length);
                if (readJson == null) return (0, null);
                json = Encoding.UTF8.GetString(readJson);
                if (string.IsNullOrWhiteSpace(json))
                {
                    return (length, null);
                }
                jsonObj = JObject.Parse(json);
            }
            catch (Exception e)
            {
                _log.Error(e);
                _log.Error(e, "Unable to parse JSON data from map server.");
                if (!string.IsNullOrWhiteSpace(json))
                {
                    _log.Error(json);
                }

                return (length, null);
            }

            if (jsonObj.ContainsKey("error"))
            {
                _log.Error(jsonObj["error"].ToString());
                return (length, null);
            }

            return (length, json);
        }

        public MapApi(GameData gameData)
        {
            _gameData = gameData;

            // Cache for pre-fetching maps for the surrounding areas.
            _cache = new ConcurrentDictionary<Area, AreaData>();
        }

        public AreaData GetMapData(Area area)
        {
            if (!_cache.TryGetValue(area, out AreaData areaData))
            {
                areaData = GetMapDataInternal(area);
            }
            else
            {
                //_log.Info($"Cache found for {area}");
            }

            if (areaData != null)
            {
                var adjacentAreas = areaData.AdjacentLevels.Keys.ToArray();
                var stitchedAreas = areaData.Area.StitchedAreas()?.Where(x => !adjacentAreas.Contains(x)).ToArray() ?? new Area[] { };

                foreach (var adjacentArea in adjacentAreas.Concat(stitchedAreas).ToArray())
                {
                    if (!_cache.TryGetValue(adjacentArea, out AreaData adjAreaData))
                    {
                        areaData.AdjacentAreas[adjacentArea] = GetMapDataInternal(adjacentArea);
                    }
                    else
                    {
                        //_log.Info($"Cache found for {adjacentArea}");
                        areaData.AdjacentAreas[adjacentArea] = adjAreaData;
                    }
                }

                //_log.Info($"{adjacentAreas.Length} adjacent and {stitchedAreas.Length} stitched areas to {area} found");
            }
            else
            {
                //_log.Info($"Area data was null for {area}");
            }

            return areaData;
        }

        private AreaData GetMapDataInternal(Area area)
        {
            //_log.Info($"Requesting map data for {area} ({_gameData.MapSeed} seed, {_gameData.Difficulty} difficulty)");

            var req = new Req();
            req.seed = _gameData.MapSeed;
            req.difficulty = (uint)_gameData.Difficulty;
            req.levelId = (uint)area;

            lock (_pipeRequestLock)
            {
                uint length = 0;
                string json = null;
                var retriesLeft = 5;

                do
                {
                    (length, json) = MapApiRequest(ToBytes(req)).Result;

                    if (json == null)
                    {
                        _log.Error($"Unable to load data for {area} from {_procName}, retrying after restarting {_procName}");
                        StartPipedChild();
                        retriesLeft--;
                    }
                } while (json == null && retriesLeft > 0);

                if (json == null) return null;

                var rawAreaData = JsonConvert.DeserializeObject<RawAreaData>(json);
                var areaData = rawAreaData.ToInternal(area);
                _cache[area] = areaData;
                //_log.Info($"Loaded data for {areaData.Area}");

                areaData.PointsOfInterest = PointOfInterestHandler.Get(this, areaData, _gameData);
                //_log.Info($"Found {areaData.PointsOfInterest.Count} points of interest in {areaData.Area}");

                return areaData;
            }
        }

        public static byte[] Combine(byte[] first, byte[] second)
        {
            var ret = new byte[first.Length + second.Length];
            Buffer.BlockCopy(first, 0, ret, 0, first.Length);
            Buffer.BlockCopy(second, 0, ret, first.Length, second.Length);
            return ret;
        }

        private static byte[] ToBytes(Req req)
        {
            var size = Marshal.SizeOf(req);
            var arr = new byte[size];

            IntPtr ptr = Marshal.AllocHGlobal(size);
            Marshal.StructureToPtr(req, ptr, true);
            Marshal.Copy(ptr, arr, 0, size);
            Marshal.FreeHGlobal(ptr);
            return arr;
        }

        [StructLayout(LayoutKind.Sequential, Pack = 1)]
        private struct Req
        {
            public uint seed;
            public uint difficulty;
            public uint levelId;
        }

        private static bool disposed = false;

        public static void Dispose()
        {
            if (!disposed)
            {
                disposed = true;
                DisposePipe();
            }
        }

        private static void DisposePipe()
        {
            if (_pipeClient == null)
            {
                return;
            }

            _log.Info("Closing map server");
            if (!_pipeClient.HasExited)
            {
                try { _pipeClient.Kill(); } catch (Exception) { }
                try { _pipeClient.Close(); } catch (Exception) { }
            }
            try { _pipeClient.Dispose(); } catch (Exception) { }

            _pipeClient = null;
        }

        private static void StopPipeServers()
        {
            DisposePipe();

            // Shutdown old running versions of the map server
            var id = Process.GetCurrentProcess().SessionId;
            var procs = Process.GetProcessesByName(_procName);
            foreach (var proc in procs)
            {
                if (proc.SessionId == id)
                {
                    try { proc.Kill(); } catch (Exception) { }
                }
            }
        }
    }
}
