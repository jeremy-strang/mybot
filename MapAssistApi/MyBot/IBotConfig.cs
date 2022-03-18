using System;
using System.Collections.Generic;
using MapAssist.Settings;
using MapAssist.Types;

namespace MapAssist.MyBot
{
    public interface IBotConfig
    {
        T GetValue<T>(string section, string key, T defaultValue = default);
    }

    public class BotConfig : IBotConfig
    {
        private static readonly object mutex = new object();

        private readonly Dictionary<string, Dictionary<string, object>> _rawConfiguration;

        public BotConfig(Dictionary<string, Dictionary<string, object>> rawConfiguration)
        {
            _rawConfiguration = rawConfiguration;
        }

        public static IBotConfig Current { get; private set; } =
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

        public static Dictionary<Item, List<ItemFilter>> ConvertMyBotPickit()
        {
            var result = new Dictionary<Item, List<ItemFilter>>();

            return result;
        }
    }
}
