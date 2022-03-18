using MapAssist.Botty;
using Newtonsoft.Json;
using NUnit.Framework;
using System;

namespace MapAssist.Tests
{
    [TestFixture]
    public class IntegrationTests
    {
        [Test]
        public void CheckMemoryData()
        {
            if (ApiHost.BootstrapMapAssist())
            {
                using (var api = new Api())
                {
                    api.RetrieveDataFromMemory(true, Formatting.Indented);
                }
            }
        }
    }
}
