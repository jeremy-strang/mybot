using MapAssist.Helpers;
using MapAssist.Settings;
using Newtonsoft.Json;
using NLog;
using NLog.Config;
using NLog.Targets;
using System;
using System.Collections.Generic;
using System.IO;
using System.Threading;
using System.Threading.Tasks;
using YamlDotNet.Core;

namespace MapAssist.Botty
{
    public class ApiHost
    {
        private const string LoggerLayout = "${longdate} ${message} ${exception:format=tostring}";
        private static CancellationTokenSource TokenSource = new CancellationTokenSource();
        private static Task _runningTask;
        private static readonly Logger _log = LogManager.GetCurrentClassLogger();

        private static readonly Lazy<bool> lazyConfig = new Lazy<bool>(() =>
            LoadMainConfiguration() && LoadLootLogConfiguration());

        static ApiHost()
        {
            LoadLoggingConfiguration();
        }

        private static async Task RunInternalAsync(Action<string> onDataHandler, CancellationToken token, bool forceMap = true)
        {
            try
            {
                var interval = BottyConfiguration.Current.GetValue("map_assist", "polling_interval", 10);
                var chicken = BottyConfiguration.Current.GetValue("char", "chicken", 0.5);
                using (var api = new Api(chicken))
                {
                    while (!token.IsCancellationRequested)
                    {
                        onDataHandler(api.RetrieveDataFromMemory(forceMap));
                        forceMap = false;
                        await Task.Delay(interval, token);
                    }
                }
            }
            catch (TaskCanceledException)
            {
                // _log.Info("Stopped API host");
            }
            catch (Exception e)
            {
                _log.Fatal(e);
            }
        }


        public static void Run(
            Dictionary<string, Dictionary<string, object>> rawConfiguration,
            Action<string> onDataHandler,
            bool forceMap = true)
        {
            // _log.Info($"Initializing ApiHost with configuration: \n{JsonConvert.SerializeObject(rawConfiguration, Formatting.Indented)}");
            BottyConfiguration.InitializeConfiguration(rawConfiguration);
            if (BootstrapMapAssist())
            {
                _runningTask = Task.Run(() => RunInternalAsync(onDataHandler, TokenSource.Token, forceMap));
                _runningTask.GetAwaiter().GetResult();
            }
        }

        public static bool BootstrapMapAssist()
        {
            if (lazyConfig.Value)
            {
                if (StartMapApi())
                {
                    GameManager.OnGameAccessDenied += (_, __) =>
                    {
                        _log.Fatal(
                            $"MapAssist could not read {GameManager.ProcessName} memory. Please reopen MapAssist as an administrator. Error opening handle to {GameManager.ProcessName}");
                        Environment.Exit(0);
                    };

                    GameManager.MonitorForegroundWindow();
                    return true;
                }
            }

            return false;
        }

        private static bool StartMapApi()
        {
            try
            {
                if (MapApi.StartPipedChild())
                {
                    return true;
                }

                _log.Fatal("Unable to start d2mapapi pipe");
            }
            catch (Exception e)
            {
                _log.Fatal(e);
                _log.Fatal(e, "Unable to start d2mapapi pipe.");
            }

            return false;
        }


        private static bool LoadMainConfiguration()
        {
            try
            {
                MapAssistConfiguration.Load();
                MapAssistConfiguration.Loaded.RenderingConfiguration.InitialSize =
                    MapAssistConfiguration.Loaded.RenderingConfiguration.Size;
                return true;
            }
            catch (YamlException e)
            {
                _log.Fatal(e);
                _log.Fatal(e, "Invalid yaml for configuration file");
            }
            catch (Exception e)
            {
                _log.Fatal(e, "Unknown error loading main configuration");
            }

            return false;
        }

        private static bool LoadLootLogConfiguration()
        {
            try
            {
                LootLogConfiguration.Load();
                return true;
            }
            catch (YamlException e)
            {
                _log.Fatal(e, "Invalid item log yaml file");
            }
            catch (Exception e)
            {
                _log.Fatal(e, "Unable to initialize Loot Log configuration");
            }

            return false;
        }

        private static void LoadLoggingConfiguration()
        {
            var config = new LoggingConfiguration();

            var logfile = new FileTarget("logfile")
            {
                FileName = Path.Combine(BottyConfiguration.Current.GetValue("general", "log_file_dir", Environment.CurrentDirectory), "map_assist_api.log"),
                CreateDirs = true,
                ArchiveNumbering = ArchiveNumberingMode.DateAndSequence,
                ArchiveOldFileOnStartup = true,
                MaxArchiveFiles = 5,
                Layout = LoggerLayout
            };
            var logconsole = new ConsoleTarget("logconsole") { Layout = LoggerLayout };

            // Rules for mapping loggers to targets
            config.AddRule(LogLevel.Debug, LogLevel.Fatal, logconsole);
            config.AddRule(LogLevel.Info, LogLevel.Fatal, logfile);

            // Apply config
            LogManager.Configuration = config;
        }

        public static void Stop()
        {
            TokenSource.Cancel();
            TokenSource = new CancellationTokenSource();
        }
    }
}
