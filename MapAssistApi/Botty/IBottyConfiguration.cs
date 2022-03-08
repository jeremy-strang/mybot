using System;
using System.Collections.Generic;

namespace MapAssist.Botty
{
    public interface IBottyConfiguration
    {
        T GetValue<T>(string section, string key, T defaultValue = default);
    }

    public class BottyConfiguration : IBottyConfiguration
    {
        private static readonly object mutex = new object();

        private readonly Dictionary<string, Dictionary<string, object>> _rawConfiguration;

        public BottyConfiguration(Dictionary<string, Dictionary<string, object>> rawConfiguration)
        {
            _rawConfiguration = rawConfiguration;
        }

        public static IBottyConfiguration Current { get; private set; } =
            new BottyConfiguration(new Dictionary<string, Dictionary<string, object>>());

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
                Current = new BottyConfiguration(rawData);
            }
        }
    }
}
