using MapAssist.MyBot;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace MapAssist.Tests
{
    internal class Program
    {
        private static void Debug(string data)
        {
            var res = JsonConvert.DeserializeObject<JObject>(data);
            var m = res.GetValue("monsters");
            //Console.WriteLine($"Monsters: {m}");
        }

        static async Task Main(string[] args)
        {
            var task = Task.Run(() => ApiHost.Run(new Dictionary<string, Dictionary<string, object>>(), Debug));
            Console.ReadKey(true);
            ApiHost.Stop();
            await task;
            task = Task.Run(() => ApiHost.Run(new Dictionary<string, Dictionary<string, object>>(), Debug));
            Console.ReadKey(true);
            ApiHost.Stop();
            await task;
        }
    }
}
