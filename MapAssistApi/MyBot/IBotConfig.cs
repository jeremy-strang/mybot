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
            if (_rawConfiguration.ContainsKey("items"))
            {
                var pickit = _rawConfiguration["items"];
                foreach (var key in pickit.Keys)
                {
                    int.TryParse((string)pickit[key], out var pickitType);
                    if (pickitType > 0 && key != "misc_gold" && key.Contains("_"))
                    {
                        TextInfo info = CultureInfo.CurrentCulture.TextInfo;
                        var start = key.Substring(0, key.IndexOf("_"));
                        var itemSnake = key.Substring(key.IndexOf("_") + 1, key.Length - key.IndexOf("_") - 1).Replace("_", " ");
                        var itemPascal = "";
                        var filter = new ItemFilter();
                        //_log.Debug("Parsing " + key + ", start: " + start);
                        if (start == "misc")
                        {
                            itemPascal = info.ToTitleCase(itemSnake).Replace(" ", string.Empty);
                        }
                        else if (start == "rune")
                        {
                            var lastIndex = key.LastIndexOf("_");
                            itemPascal = info.ToTitleCase(itemSnake + " rune").Replace(" ", string.Empty);
                        }
                        else if (start == "magic" || start == "rare" || start == "set" || start == "unique")
                        {
                            itemPascal = info.ToTitleCase(itemSnake).Replace(" ", string.Empty);
                            if (Enum.TryParse<ItemQuality>(start.ToUpper(), out var quality))
                            {
                                filter.Qualities = new ItemQuality[1] { quality };
                            }
                        }
                        if (Enum.TryParse<Item>(itemPascal, out var item))
                        {
                            _log.Debug("    Parsed item " + itemPascal + " as " + item);
                        }
                    }
                }
            }
            return result;
        }
    }
}
