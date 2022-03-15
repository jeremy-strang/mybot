/**
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

using MapAssist.Settings;
using MapAssist.Types;
using System;
using System.Collections.Generic;
using System.Linq;

namespace MapAssist.Helpers
{
    public static class GameMemory
    {
        private static readonly NLog.Logger _log = NLog.LogManager.GetCurrentClassLogger();
        private static Dictionary<int, uint> _lastMapSeeds = new Dictionary<int, uint>();
        private static Dictionary<int, bool> _playerMapChanged = new Dictionary<int, bool>();
        private static Dictionary<int, uint> _playerCubeOwnerID = new Dictionary<int, uint>();
        private static int _currentProcessId;

        public static Dictionary<int, UnitPlayer> PlayerUnits = new Dictionary<int, UnitPlayer>();
        public static Dictionary<int, Dictionary<string, UnitPlayer>> Corpses = new Dictionary<int, Dictionary<string, UnitPlayer>>();
        public static Dictionary<object, object> cache = new Dictionary<object, object>();

        private static bool _firstMemoryRead = true;
        private static bool _errorThrown = false;

        public static GameData GetGameData()
        {
            if (!MapAssistConfiguration.Loaded.RenderingConfiguration.StickToLastGameWindow && !GameManager.IsGameInForeground)
            {
                return null;
            }

            var processContext = GameManager.GetProcessContext();

            if (processContext == null)
            {
                return null;
            }

            using (processContext)
            {
                _currentProcessId = processContext.ProcessId;

                var menuOpen = processContext.Read<byte>(GameManager.MenuOpenOffset);
                var menuData = processContext.Read<Structs.MenuData>(GameManager.MenuDataOffset);
                var lastHoverData = processContext.Read<Structs.HoverData>(GameManager.LastHoverDataOffset);
                var lastNpcInteracted = (Npc)processContext.Read<ushort>(GameManager.InteractedNpcOffset);
                var rosterData = new Roster(GameManager.RosterDataOffset);

                if (!menuData.InGame)
                {
                    if (Corpses.ContainsKey(_currentProcessId))
                    {
                        Corpses[_currentProcessId].Clear();
                    }

                    return null;
                }

                var rawPlayerUnits = GetUnits<UnitPlayer>(UnitType.Player).Select(x => x.Update()).Where(x => x != null).ToArray();
                var playerUnit = rawPlayerUnits.FirstOrDefault(x => x.IsPlayer && x.IsPlayerUnit);

                while( playerUnit == null)
                {
                    rawPlayerUnits = GetUnits<UnitPlayer>(UnitType.Player).Select(x => x.Update()).Where(x => x != null).ToArray();
                    playerUnit = rawPlayerUnits.FirstOrDefault(x => x.IsPlayer && x.IsPlayerUnit);
                }

                if (playerUnit == null)
                {
                    if (_lastMapSeeds.ContainsKey(_currentProcessId))
                    {
                        _lastMapSeeds[_currentProcessId] = 0;
                    }

                    if (_errorThrown) return null;

                    _errorThrown = true;
                    throw new Exception("Player unit not found.");
                }
                _errorThrown = false;

                if (!PlayerUnits.ContainsKey(_currentProcessId))
                {
                    PlayerUnits.Add(_currentProcessId, playerUnit);
                }
                else
                {
                    PlayerUnits[_currentProcessId] = playerUnit;
                }

                // Check for map seed
                var mapSeed = playerUnit.Act.MapSeed;

                if (mapSeed <= 0 || mapSeed > 0xFFFFFFFF)
                {
                    if (_errorThrown) return null;

                    _errorThrown = true;
                    throw new Exception("Map seed is out of bounds.");
                }

                // Check if exited the game
                if (!_lastMapSeeds.ContainsKey(_currentProcessId))
                {
                    _lastMapSeeds.Add(_currentProcessId, 0);
                }

                if (!_playerMapChanged.ContainsKey(_currentProcessId))
                {
                    _playerMapChanged.Add(_currentProcessId, false);
                }

                if (!_playerCubeOwnerID.ContainsKey(_currentProcessId))
                {
                    _playerCubeOwnerID.Add(_currentProcessId, uint.MaxValue);
                }

                // Check if new game
                if (mapSeed == _lastMapSeeds[_currentProcessId])
                {
                    _playerMapChanged[_currentProcessId] = false;
                }
                else
                {
                    UpdateMemoryData();
                    _lastMapSeeds[_currentProcessId] = mapSeed;
                    _playerMapChanged[_currentProcessId] = true;
                }

                // Extra checks on game details
                var gameDifficulty = playerUnit.Act.ActMisc.GameDifficulty;

                if (!gameDifficulty.IsValid())
                {
                    if (_errorThrown) return null;

                    _errorThrown = true;
                    throw new Exception("Game difficulty out of bounds.");
                }

                var levelId = playerUnit.Area;

                if (!levelId.IsValid())
                {
                    if (_errorThrown) return null;

                    _errorThrown = true;
                    throw new Exception("Level id out of bounds.");
                }

                // Players
                var playerList = rawPlayerUnits.Where(x => x.UnitType == UnitType.Player && x.IsPlayer)
                    .Select(x => x.UpdateRosterEntry(rosterData)).ToArray()
                    .Select(x => x.UpdateParties(playerUnit.RosterEntry)).ToArray()
                    .Where(x => x != null && x.UnitId < uint.MaxValue).ToDictionary(x => x.UnitId, x => x);

                // Corpses
                var corpseList = rawPlayerUnits.Where(x => x.UnitType == UnitType.Player && x.IsCorpse).Concat(Corpses[_currentProcessId].Values).Distinct().ToArray();
                foreach (var corpse in corpseList)
                {
                    var containsKey = Corpses[_currentProcessId].ContainsKey(corpse.HashString);

                    if (!containsKey)
                    {
                        Corpses[_currentProcessId].Add(corpse.HashString, corpse);
                    }
                    else if (containsKey && corpse.DistanceTo(playerUnit) <= 40)
                    {
                        Corpses[_currentProcessId].Remove(corpse.HashString);
                    }
                }

                // Monsters
                var rawMonsterUnits = GetUnits<UnitMonster>(UnitType.Monster)
                    .Select(x => x.Update()).ToArray()
                    .Where(x => x != null && x.UnitId < uint.MaxValue).ToArray();

                var monsterList = rawMonsterUnits.Where(x => x.UnitType == UnitType.Monster && x.IsMonster).ToArray();
                var mercList = rawMonsterUnits.Where(x => x.UnitType == UnitType.Monster && x.IsMerc).ToArray();

                //var necroSkel = 0;
                //var necroGol = 0;
                //var necroMage = 0;
                /*
                foreach (var obj in rawMonsterUnits)
                {
                    if (obj.TxtFileNo == 363)
                    {
                        necroSkel += 1;
                    }
                    if (obj.TxtFileNo == 364)
                    {
                        necroMage += 1;
                    }
                    if (obj.TxtFileNo == 289)
                    {
                        necroGol += 1;
                    }

                    //Console.WriteLine(obj.TxtFileNo);
                }
                */

                // Objects
                var rawObjectUnits = GetUnits<UnitObject>(UnitType.Object, true);
                foreach (var obj in rawObjectUnits)
                {
                    obj.Update();
                }
                var objectList = rawObjectUnits.Where(x => x != null && x.UnitType == UnitType.Object && x.UnitId < uint.MaxValue).ToArray();

                // Items
                var rawItemUnits = new List<UnitItem>();
                foreach (var item in GetUnits<UnitItem>(UnitType.Item, true).Where(x => x.UnitId < uint.MaxValue).ToArray())
                {
                    if (Items.ItemUnitIdsToSkip[_currentProcessId].Contains(item.UnitId)) continue;

                    if (_playerMapChanged[_currentProcessId] && item.IsAnyPlayerHolding && item.Item != Item.HoradricCube && !Items.ItemUnitIdsToSkip[_currentProcessId].Contains(item.UnitId))
                    {
                        Items.ItemUnitIdsToSkip[_currentProcessId].Add(item.UnitId);
                        continue;
                    }

                    if (item.IsPlayerOwned && item.IsIdentified && !Items.InventoryItemUnitIdsToSkip[_currentProcessId].Contains(item.UnitId))
                    {
                        item.IsCached = false;

                    }

                    var enableInventoryFilterCheck = item.IsIdentified && item.IsPlayerOwned && !item.IsInSocket;

                    item.Update();

                    cache[item.UnitId] = item;

                    if (item.ItemModeMapped == ItemModeMapped.Ground) {
                        cache[item.HashString] = item;
                    }
                    //Console.WriteLine(item.ItemBaseName);
                    if (item.UnitId == uint.MaxValue) continue;

                    item.IsPlayerOwned = _playerCubeOwnerID[_currentProcessId] != uint.MaxValue &&
                        item.ItemData.dwOwnerID == _playerCubeOwnerID[_currentProcessId];

                    if (item.IsInStore)
                    {
                        if (Items.ItemVendors[_currentProcessId].TryGetValue(item.UnitId, out var vendor))
                        {
                            item.VendorOwner = vendor;
                        }
                        else
                        {
                            item.VendorOwner = !_firstMemoryRead ? lastNpcInteracted : Npc.Unknown; // This prevents marking the VendorOwner for all store items when restarting MapAssist in the middle of the game
                            Items.ItemVendors[_currentProcessId].Add(item.UnitId, item.VendorOwner);
                        }
                    }

                    if (item.IsValidItem && ((item.IsDropped && !item.IsIdentified) || (item.IsIdentified && item.IsInStore) || enableInventoryFilterCheck))
                    {
                        Items.LogItem(item, _currentProcessId);
                    }

                    if (item.Item == Item.HoradricCube)
                    {
                        Items.ItemUnitIdsToSkip[_currentProcessId].Add(item.UnitId);
                    }

                    rawItemUnits.Add(item);
                }

                var itemList = Items.ItemLog[_currentProcessId].Select(item =>
                {
                    if (cache.TryGetValue(item.ItemHashString, out var cachedItem) && ((UnitItem)cachedItem).HashString == item.ItemHashString)
                    {
                        item.UnitItem = (UnitItem)cachedItem;
                    }

                    if (item.UnitItem.DistanceTo(playerUnit) <= 40 && !rawItemUnits.Contains(item.UnitItem)) // Player is close to the item position but it was not found
                    {
                        item.UnitItem.MarkInvalid();
                    }

                    return item.UnitItem;
                }).Where(x => x != null).ToArray();

                // Set Cube Owner
                if (_playerMapChanged[_currentProcessId])
                {
                    var cube = rawItemUnits.FirstOrDefault(x => x.Item == Item.HoradricCube);
                    if (cube != null)
                    {
                        _playerCubeOwnerID[_currentProcessId] = cube.ItemData.dwOwnerID;
                    }
                }

                // Unit hover
                var allUnits = ((UnitAny[])playerList.Values.ToArray()).Concat(monsterList).Concat(mercList).Concat(rawObjectUnits).Concat(rawItemUnits);

                var hoveredUnits = allUnits.Where(x => x.IsHovered).ToArray();
                if (hoveredUnits.Length > 0 && hoveredUnits[0].UnitId != lastHoverData.UnitId) hoveredUnits[0].IsHovered = false;

                if (lastHoverData.IsHovered)
                {
                    var units = allUnits.Where(x => x.UnitId == lastHoverData.UnitId).ToArray();
                    if (units.Length > 0) units[0].IsHovered = true;
                }

                // Return data
                _firstMemoryRead = false;
                _errorThrown = false;

                var session = new Session(GameManager.GameIPOffset);

                // Belt items
                var allItems = GetUnits<UnitItem>(UnitType.Item, true).Where(x => x.UnitId < uint.MaxValue).ToArray();
                var belt = allItems.FirstOrDefault(x => x.ItemModeMapped == ItemModeMapped.Player && x.ItemData.BodyLoc == BodyLoc.BELT);
                var beltItems = allItems.Where(x => x.ItemModeMapped == ItemModeMapped.Belt).ToArray();

                var beltSize = belt == null ? 1 :
                    new Item[] { Item.Sash, Item.LightBelt }.Contains(belt.Item) ? 2 :
                    new Item[] { Item.Belt, Item.HeavyBelt }.Contains(belt.Item) ? 3 : 4;

                playerUnit.BeltItems = Enumerable.Range(0, 4).Select(i => Enumerable.Range(0, beltSize).Select(j => beltItems.FirstOrDefault(item => item.X == i + j * 4)).ToArray()).ToArray();
                
                return new GameData
                {
                    PlayerPosition = playerUnit.Position,
                    MapSeed = mapSeed,
                    Area = levelId,
                    Difficulty = gameDifficulty,
                    MainWindowHandle = GameManager.MainWindowHandle,
                    PlayerName = playerUnit.Name,
                    PlayerUnit = playerUnit,
                    Players = playerList,
                    Corpses = corpseList,
                    Monsters = monsterList,
                    Mercs = mercList,
                    Objects = objectList,
                    Items = itemList,
                    BeltItems = beltItems,
                    AllItems = allItems,
                    ItemLog = Items.ItemLog[_currentProcessId].ToArray(),
                    Session = session,
                    Roster = rosterData,
                    MenuOpen = menuData,
                    MenuPanelOpen = menuOpen,
                    LastNpcInteracted = lastNpcInteracted,
                    ProcessId = _currentProcessId,
                };
            }
        }

        public static UnitPlayer PlayerUnit => PlayerUnits.TryGetValue(_currentProcessId, out var player) ? player : null;

        private static T[] GetUnits<T>(UnitType unitType, bool saveToCache = false) where T : UnitAny
        {
            var allUnits = new Dictionary<uint, T>();
            Func<IntPtr, T> CreateUnit = (ptr) => (T)Activator.CreateInstance(typeof(T), new object[] { ptr });

            var unitHashTable = GameManager.UnitHashTable(128 * 8 * (int)unitType);

            foreach (var ptrUnit in unitHashTable.UnitTable)
            {
                if (ptrUnit == IntPtr.Zero) continue;

                var unit = CreateUnit(ptrUnit);

                Action<object> UseCachedUnit = (seenUnit) =>
                {
                    var castedSeenUnit = (T)seenUnit;
                    castedSeenUnit.CopyFrom(unit);

                    allUnits[castedSeenUnit.UnitId] = castedSeenUnit;
                };

                do
                {
                    if (saveToCache && cache.TryGetValue(unit.UnitId, out var seenUnit1) && seenUnit1 is T && !allUnits.ContainsKey(((T)seenUnit1).UnitId))
                    {
                        UseCachedUnit(seenUnit1);
                    }
                    else if (saveToCache && cache.TryGetValue(unit.HashString, out var seenUnit2) && seenUnit2 is T && !allUnits.ContainsKey(((T)seenUnit2).UnitId))
                    {
                        UseCachedUnit(seenUnit2);
                    }
                    else if (unit.IsValidUnit && !allUnits.ContainsKey(unit.UnitId))
                    {
                        allUnits[unit.UnitId] = unit;

                        if (saveToCache)
                        {
                            cache[unit.UnitId] = unit;
                            //cache[unit.HashString] = unit;
                        }
                    }
                } while (unit.Struct.pListNext != IntPtr.Zero && (unit = CreateUnit(unit.Struct.pListNext)).IsValidUnit);
            }

            return allUnits.Values.ToArray();
        }

        private static void UpdateMemoryData()
        {
            if (!Items.ItemUnitHashesSeen.ContainsKey(_currentProcessId))
            {
                Items.ItemUnitHashesSeen.Add(_currentProcessId, new HashSet<string>());
                Items.ItemUnitIdsSeen.Add(_currentProcessId, new HashSet<uint>());
                Items.ItemUnitIdsToSkip.Add(_currentProcessId, new HashSet<uint>());
                Items.InventoryItemUnitIdsToSkip.Add(_currentProcessId, new HashSet<uint>());
                Items.ItemVendors.Add(_currentProcessId, new Dictionary<uint, Npc>());
                Items.ItemLog.Add(_currentProcessId, new List<ItemLogEntry>());
            }
            else
            {
                Items.ItemUnitHashesSeen[_currentProcessId].Clear();
                Items.ItemUnitIdsSeen[_currentProcessId].Clear();
                Items.ItemUnitIdsToSkip[_currentProcessId].Clear();
                Items.InventoryItemUnitIdsToSkip[_currentProcessId].Clear();
                Items.ItemVendors[_currentProcessId].Clear();
                Items.ItemLog[_currentProcessId].Clear();
            }

            if (!Corpses.ContainsKey(_currentProcessId))
            {
                Corpses.Add(_currentProcessId, new Dictionary<string, UnitPlayer>());
            }
            else
            {
                Corpses[_currentProcessId].Clear();
            }
        }

        //private static HashSet<Room> GetRooms(Room startingRoom, ref HashSet<Room> roomsList)
        //{
        //    var roomsNear = startingRoom.RoomsNear;
        //    foreach (var roomNear in roomsNear)
        //    {
        //        if (!roomsList.Contains(roomNear))
        //        {
        //            roomsList.Add(roomNear);
        //            GetRooms(roomNear, ref roomsList);
        //        }
        //    }

        //    if (!roomsList.Contains(startingRoom.RoomNextFast))
        //    {
        //        roomsList.Add(startingRoom.RoomNextFast);
        //        GetRooms(startingRoom.RoomNextFast, ref roomsList);
        //    }

        //    return roomsList;
        //}
    }
}
