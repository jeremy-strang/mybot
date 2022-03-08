﻿/**
 *   Copyright (C) 2021 okaygo
 *
 *   https://github.com/misterokaygo/MapAssist/
 *
 *  This program is free software: you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation, either version 3 of the License, or
 *  (at your option) any later version.
 *
 *  This program is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License
 *  along with this program.  If not, see <https://www.gnu.org/licenses/>.
 **/

using System;
using System.Runtime.InteropServices;

namespace MapAssist.Structs
{
    [StructLayout(LayoutKind.Explicit)]
    public struct Inventory
    {
        [FieldOffset(0x0)] public uint dwSignature;
        [FieldOffset(0x8)] public IntPtr pOwnerUnit;
        [FieldOffset(0x20)] public IntPtr pGrid;

        // Used to see if the current player is the correct player
        // Should not be 0x0 for local player
        [FieldOffset(0x70)] public IntPtr pUnk1;
    }
    [StructLayout(LayoutKind.Explicit)]
    public struct InventoryGrid
    {
        [FieldOffset(0x50)] public byte Width;
        [FieldOffset(0x51)] public byte Height;
        [FieldOffset(0xD0)] public byte StashWidth;
        [FieldOffset(0xD1)] public byte StashHeight;
    }
}
