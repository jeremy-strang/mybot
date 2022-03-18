using System;
using System.Collections.Generic;
using System.Globalization;
using MapAssist.Settings;
using MapAssist.Types;
using NLog;

namespace MapAssist.MyBot
{
    //public interface IBotConfig
    //{
    //    T GetValue<T>(string section, string key, T defaultValue = default);
    //}

    public class BotConfig //: IBotConfig
    {
        private static readonly Logger _log = LogManager.GetCurrentClassLogger();

        private static readonly object mutex = new object();

        private readonly Dictionary<string, Dictionary<string, object>> _rawConfiguration;

        public BotConfig(Dictionary<string, Dictionary<string, object>> rawConfiguration)
        {
            _rawConfiguration = rawConfiguration;
        }

        public static BotConfig Current { get; private set; } =
            new BotConfig(new Dictionary<string, Dictionary<string, object>>());

        public T GetValue<T>(string section, string key, T defaultValue = default)
        {
            if (_rawConfiguration.ContainsKey(section) && _rawConfiguration[section].ContainsKey(key))
            {
                return (T)Convert.ChangeType(_rawConfiguration[section][key], typeof(T));
            }
            return defaultValue;
        }

        public static void InitializeConfiguration(Dictionary<string, Dictionary<string, object>> rawData)
        {
            lock (mutex)
            {
                Current = new BotConfig(rawData);
            }
        }

        public Dictionary<Item, List<ItemFilter>> ConvertMyBotPickit()
        {
            var result = new Dictionary<Item, List<ItemFilter>>();
            var success = 0;
            var fail = 0;
            if (_rawConfiguration.ContainsKey("items"))
            {
                var pickit = _rawConfiguration["items"];
                foreach (var key in pickit.Keys)
                {
                    if (ParsePickitLine(key, (string)pickit[key], result))
                    {
                        success++;
                    }
                    else
                    {
                        fail++;
                    }
                }
            }
            _log.Debug("Successfully parsed " + success + " lines, failed to parse " + fail);
            return result;
        }

        private bool ParsePickitLine(string key, string value, Dictionary<Item, List<ItemFilter>> dict)
        {
            var success = false;
            int.TryParse(value.Substring(0, 1), out var pickitType);
            //if (pickitType > 0 && key != "misc_gold" && key.Contains("_"))

            if (key != "misc_gold" && key.Contains("_"))
            {
                TextInfo info = CultureInfo.CurrentCulture.TextInfo;
                var start = key.Substring(0, key.IndexOf("_"));
                var itemSnake = key.Substring(key.IndexOf("_") + 1, key.Length - key.IndexOf("_") - 1).Replace("_", " ");
                var itemPascal = "";
                var filter = new ItemFilter();
                if (start == "misc")
                {
                    itemPascal = info.ToTitleCase(itemSnake).Replace(" ", string.Empty);
                }
                else if (start == "rune")
                {
                    var lastIndex = key.LastIndexOf("_");
                    itemSnake = key.Substring(lastIndex + 1, key.Length - lastIndex - 1) + " rune";
                    itemPascal = info.ToTitleCase(itemSnake).Replace(" ", string.Empty);
                }
                else if (start == "gray" || start == "white" || start == "magic" || start == "rare" || start == "set" || start == "uniq")
                {

                    switch (start)
                    {
                        case "gray":
                            filter.Qualities = new ItemQuality[1] { key.StartsWith("gray_superior") ? ItemQuality.SUPERIOR : ItemQuality.NORMAL };
                            break;
                        case "white":
                            filter.Qualities = new ItemQuality[1] { key.StartsWith("white_superior") ? ItemQuality.SUPERIOR : ItemQuality.NORMAL };
                            break;
                        case "magic":
                            filter.Qualities = new ItemQuality[1] { ItemQuality.MAGIC };
                            break;
                        case "rare":
                            filter.Qualities = new ItemQuality[1] { ItemQuality.RARE };
                            break;
                        case "set":
                            filter.Qualities = new ItemQuality[1] { ItemQuality.SET };
                            break;
                        case "uniq":
                            filter.Qualities = new ItemQuality[1] { ItemQuality.UNIQUE };
                            break;
                    }
                    itemPascal = info.ToTitleCase(itemSnake.Replace(" superior", string.Empty)).Replace(" ", string.Empty);

                    if (start == "uniq") start = "unique";
                    if (Enum.TryParse<ItemQuality>(start.ToUpper(), out var quality))
                    {

                    }
                }
                if (Enum.TryParse<Item>(itemPascal, out var item))
                {
                    success = true;
                    var qualStr = filter.Qualities != null ? string.Join(", ", filter.Qualities) : "none";
                    _log.Debug("    Parsed item " + key + " as " + item + " with qualities: " + qualStr);
                }
                else
                {
                    _log.Debug("    Couldn't parse item " + key + " (" + itemPascal + ")");
                }
            }

            return success;
        }
    }
}
