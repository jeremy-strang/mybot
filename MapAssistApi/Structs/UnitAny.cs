﻿using MapAssist.Types;
using System;
using System.Runtime.InteropServices;

namespace MapAssist.Structs
{
    [StructLayout(LayoutKind.Explicit)]
    public struct UnitAny
    {
        [FieldOffset(0x00)] public UnitType UnitType;
        [FieldOffset(0x04)] public uint TxtFileNo;
        [FieldOffset(0x08)] public uint UnitId;
        [FieldOffset(0x0C)] public uint Mode;
        [FieldOffset(0x10)] public IntPtr pUnitData;
        [FieldOffset(0x20)] public IntPtr pAct;
        [FieldOffset(0x38)] public IntPtr pPath;
        [FieldOffset(0x88)] public IntPtr pStatsListEx;
        [FieldOffset(0x90)] public IntPtr pInventory;

        //[MarshalAs(UnmanagedType.U1)]
        //[FieldOffset(0xB9)] public bool isAlive1; // ?
        [FieldOffset(0xC4)] public ushort X;

        [FieldOffset(0xC6)] public ushort Y;
        [FieldOffset(0xD8)] public readonly uint UnkSortStashesBy;
        [FieldOffset(0x100)] public IntPtr pSkills;
        [FieldOffset(0x150)] public IntPtr pListNext;
        [FieldOffset(0x158)] public IntPtr pRoomNext;
        [FieldOffset(0x174)] public PlayerClass playerClass;

        //[FieldOffset(0x194)] public ushort unk1;
        //[FieldOffset(0x19D)] public byte isAlive2; //could be = 16 for alive players
        [MarshalAs(UnmanagedType.U1)]
        [FieldOffset(0x1A6)] public bool isCorpse;

        //[FieldOffset(0x1B8)] public uint unk2;
        //[FieldOffset(0x1BC)] public uint unk3;
        //[FieldOffset(0x1C0)] public uint unk4;

        public override bool Equals(object obj) => obj is UnitAny other && Equals(other);

        public bool Equals(UnitAny unit) => UnitId == unit.UnitId;

        public override int GetHashCode() => UnitId.GetHashCode();

        public static bool operator ==(UnitAny unit1, UnitAny unit2) => unit1.Equals(unit2);

        public static bool operator !=(UnitAny unit1, UnitAny unit2) => !(unit1 == unit2);
    }

    [StructLayout(LayoutKind.Explicit)]
    public readonly struct StatValue
    {
        [FieldOffset(0x0)] public readonly ushort Layer;
        [FieldOffset(0x2)] public readonly Stats.Stat Stat;
        [FieldOffset(0x4)] public readonly int Value;
    }

    [StructLayout(LayoutKind.Explicit)]
    public readonly struct StatListStruct
    {
        [FieldOffset(0x1C)] public readonly uint Flags;
        [FieldOffset(0x30)] public readonly StatArrayStruct Stats;
    }

    [StructLayout(LayoutKind.Explicit)]
    public readonly struct StatArrayStruct
    {
        [FieldOffset(0x0)] public readonly IntPtr pFirstStat;
        [FieldOffset(0x8)] public readonly ulong Size;
    }

    [StructLayout(LayoutKind.Explicit)]
    public readonly struct StatListExStruct
    {
        [FieldOffset(0x0)] public readonly StatListStruct BaseStats;
        [FieldOffset(0x48)] public readonly IntPtr pPrevLink;
        [FieldOffset(0x68)] public readonly IntPtr pLastList;
        [FieldOffset(0x70)] public readonly IntPtr pMyStats;
        [FieldOffset(0x80)] public readonly StatArrayStruct Stats;

        [MarshalAs(UnmanagedType.ByValArray, SizeConst = 6)]
        [FieldOffset(0xAC8)] public readonly uint[] StateFlags;
    }
}
