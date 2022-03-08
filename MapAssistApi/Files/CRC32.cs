
using System;
using System.IO;

namespace MapAssist.Files
{
    public static class Checksum
    {
        private static Crc32 _crc32;

        public static uint FileChecksum(string filePath)
        {
            if (_crc32 == null)
            {
                _crc32 = new Crc32();
            }
            var fileBytes = File.ReadAllBytes(filePath);
            var checksum = _crc32.ComputeChecksum(fileBytes);
            return checksum;
        }
    }
    public class Crc32
    {
        private uint[] _table;

        public uint ComputeChecksum(byte[] bytes)
        {
            var crc = 0xffffffff;
            for (var i = 0; i < bytes.Length; ++i)
            {
                var index = (byte)(((crc) & 0xff) ^ bytes[i]);
                crc = (uint)((crc >> 8) ^ _table[index]);
            }
            return ~crc;
        }

        public byte[] ComputeChecksumBytes(byte[] bytes)
        {
            return BitConverter.GetBytes(ComputeChecksum(bytes));
        }

        public Crc32()
        {
            var poly = 0xedb88320;
            _table = new uint[256];
            uint temp = 0;
            for (uint i = 0; i < _table.Length; ++i)
            {
                temp = i;
                for (var j = 8; j > 0; --j)
                {
                    if ((temp & 1) == 1)
                    {
                        temp = (uint)((temp >> 1) ^ poly);
                    }
                    else
                    {
                        temp >>= 1;
                    }
                }
                _table[i] = temp;
            }
        }
    }
}
