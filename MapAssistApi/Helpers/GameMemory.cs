using MapAssist.Settings;
using MapAssist.Types;
using System;
using System.Collections.Generic;
using System.Linq;

namespace MapAssist.Helpers
{
    public static class GameMemory
    {
        private static readonly HashSet<Area> _towns = new HashSet<Area>() {
            Area.RogueEncampment,
            Area.LutGholein,
            Area.KurastDocks,
            Area.ThePandemoniumFortress,
            Area.Harrogath
        };

        private static readonly HashSet<Item> _junkItems = new HashSet<Item>()
        {
            Item.Gold,
            Item.Arrows,
            Item.Bolts,
            Item.StranglingGasPotion,
            Item.ChokingGasPotion,
            Item.ExplodingPotion,
            Item.OilPotion,
            Item.AntidotePotion,
            Item.ThawingPotion,
        };

        private static Dictionary<int, uint> _lastMapSeeds = new Dictionary<int, uint>();
        private static Dictionary<int, bool> _playerMapChanged = new Dictionary<int, bool>();
        private static Dictionary<int, Area> _playerArea = new Dictionary<int, Area>();
        private static Dictionary<int, Session> _sessions = new Dictionary<int, Session>();
        private static int _currentProcessId;

        public static Dictionary<int, MapSeed> MapSeeds = new Dictionary<int, MapSeed>();
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
                var currentWindowHandle = GameManager.MainWindowHandle;

                var menuData = processContext.Read<Structs.MenuData>(GameManager.MenuDataOffset);
                var lastHoverData = processContext.Read<Structs.HoverData>(GameManager.LastHoverDataOffset);
                var lastNpcInteracted = (Npc)processContext.Read<ushort>(GameManager.InteractedNpcOffset);
                var rosterData = new Roster(GameManager.RosterDataOffset);
                var pets = new Pets(GameManager.PetsOffset);

                if (!menuData.InGame)
                {
                    if (_sessions.ContainsKey(_currentProcessId))
                    {
                        _sessions.Remove(_currentProcessId);
                    }

                    if (_playerArea.ContainsKey(_currentProcessId))
                    {
                        _playerArea.Remove(_currentProcessId);
                    }

                    if (_lastMapSeeds.ContainsKey(_currentProcessId))
                    {
                        _lastMapSeeds.Remove(_currentProcessId);
                    }

                    if (Corpses.ContainsKey(_currentProcessId))
                    {
                        Corpses[_currentProcessId].Clear();
                    }

                    return null;
                }

                if (!_sessions.ContainsKey(_currentProcessId))
                {
                    _sessions.Add(_currentProcessId, new Session(GameManager.GameNameOffset));
                }

                var rawPlayerUnits = GetUnits<UnitPlayer>(UnitType.Player).Select(x => x.Update()).Where(x => x != null).ToArray();
                var playerUnit = rawPlayerUnits.FirstOrDefault(x => x.IsPlayer && x.IsPlayerUnit);

                if (playerUnit == null)
                {
                    return null;
                    //if (_errorThrown) return null;

                    //_errorThrown = true;
                    //throw new Exception("Player unit not found.");
                }
                _errorThrown = false;

                PlayerUnits[_currentProcessId] = playerUnit;

                var stashTabOrder = rawPlayerUnits
                    .Where(o => o.StateList.Contains(State.SharedStash) || o.IsPlayer)
                    .OrderBy(o => o.Struct.UnkSortStashesBy)
                    .Select(o => o.UnitId).ToList();

                var levelId = playerUnit.Area;

                if (!levelId.IsValid())
                {
                    if (_errorThrown) return null;

                    _errorThrown = true;
                    //throw new Exception("Level id out of bounds.");
                }

                if (!MapSeeds.TryGetValue(_currentProcessId, out var _mapSeedData))
                {
                    _mapSeedData = new MapSeed();
                    MapSeeds[_currentProcessId] = _mapSeedData;
                }

                // Update area timer
                var areaCacheFound = _playerArea.TryGetValue(_currentProcessId, out var previousArea);
                if (!areaCacheFound || previousArea != levelId)
                {
                    if (areaCacheFound)
                    {
                        _sessions[_currentProcessId].TotalAreaTimeElapsed[previousArea] = _sessions[_currentProcessId].AreaTimeElapsed;
                    }

                    _playerArea[_currentProcessId] = levelId;

                    if (areaCacheFound)
                    {
                        _sessions[_currentProcessId].LastAreaChange = DateTime.Now;
                        _sessions[_currentProcessId].PreviousAreaTime = _sessions[_currentProcessId].TotalAreaTimeElapsed.TryGetValue(levelId, out var previousTime) ? previousTime : 0d;
                    }
                }

                // Check for map seed
                var mapSeed = _mapSeedData.Get(playerUnit);
                var mapSeedIsReady = _mapSeedData.IsReady;

                if (mapSeedIsReady)
                {
                    if (mapSeed <= 0 || mapSeed > 0xFFFFFFFF)
                    {
                        if (_errorThrown) return null;

                        _errorThrown = true;
                        //throw new Exception("Map seed is out of bounds.");
                    }
                }

                // Check if new game
                if (_lastMapSeeds.ContainsKey(_currentProcessId) && mapSeed == _lastMapSeeds[_currentProcessId])
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
                    //throw new Exception("Game difficulty out of bounds.");
                }

                var areaLevel = levelId.Level(gameDifficulty);

                // Players
                var playerList = rawPlayerUnits.Where(x => x.UnitType == UnitType.Player && x.IsPlayer)
                    .Select(x => x.UpdateRosterEntry(rosterData)).ToArray()
                    .Where(x => x != null && x.UnitId < uint.MaxValue).ToDictionary(x => x.UnitId, x => x);

                // Roster
                foreach (var entry in rosterData.List)
                {
                    entry.UpdateParties(playerUnit.RosterEntry);
                }

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

                foreach (var petEntry in pets.List)
                {
                    var pet = rawMonsterUnits.FirstOrDefault(x => x.UnitId == petEntry.UnitId);

                    if (pet != null)
                    {
                        petEntry.IsPlayerOwned = playerUnit.UnitId == petEntry.OwnerId;
                        pet.PetEntry = petEntry;
                    }
                }

                var mercList = rawMonsterUnits.Where(x => x.IsMerc).ToArray();
                //var summonsList = rawMonsterUnits.Where(x => x.IsSummon).ToArray();

                // Objects
                var rawObjectUnits = GetUnits<UnitObject>(UnitType.Object, true);
                foreach (var obj in rawObjectUnits)
                {
                    obj.Update();
                }
                var objectList = rawObjectUnits.Where(x => x != null && x.UnitType == UnitType.Object && x.UnitId < uint.MaxValue).ToArray();

                // Missiles
                // enemy missiles
                //var rawMissileUnits = GetUnits<UnitMissile>(UnitType.Missile, false);
                //var clientMissileList = rawMissileUnits.Where(x => x != null && x.UnitType == UnitType.Missile && x.UnitId < uint.MaxValue).ToArray();

                // player missiles
                //var rawServerMissileUnits = GetUnits<UnitMissile>(UnitType.ServerMissile, false);
                //var serverMissileList = rawServerMissileUnits.Where(x => x != null && x.UnitType == UnitType.Missile && x.UnitId < uint.MaxValue).ToArray();
                //var missileList = clientMissileList.Concat(serverMissileList).ToArray();

                // Items
                var allItems = GetUnits<UnitItem>(UnitType.Item, true).Where(x => x.UnitId < uint.MaxValue).ToArray();
                var rawItemUnits = new List<UnitItem>();
                foreach (var item in allItems)
                {
                    if (!_towns.Contains(levelId) && item.ItemModeMapped != ItemModeMapped.Ground && item.ItemModeMapped != ItemModeMapped.Inventory) continue;
                    if (_junkItems.Contains(item.Item)) continue;

                    //if (item.IsPlayerOwned && item.IsIdentified && !Items.InventoryItemUnitIdsToSkip[_currentProcessId].Contains(item.UnitId))
                    //{
                    item.IsCached = false;
                    //}

                    var checkInventoryItem = Items.CheckInventoryItem(item, _currentProcessId);

                    item.Update();

                    if (item.ItemModeMapped == ItemModeMapped.Stash)
                    {
                        var stashIndex = stashTabOrder.FindIndex(a => a == item.ItemData.dwOwnerID);
                        if (stashIndex >= 0)
                        {
                            item.StashTab = (StashTab)stashIndex + 1;
                        }
                    }

                    cache[item.UnitId] = item;

                    if (item.ItemModeMapped == ItemModeMapped.Ground)
                    {
                        cache[item.HashString] = item;
                    }

                    item.IsPlayerOwned = rosterData.List[0].UnitId != uint.MaxValue && item.ItemData.dwOwnerID == rosterData.List[0].UnitId;

                    //if (Items.ItemUnitIdsToSkip[_currentProcessId].Contains(item.UnitId)) continue;

                    //if (_playerMapChanged[_currentProcessId] && item.IsAnyPlayerHolding && item.Item != Item.HoradricCube && !Items.ItemUnitIdsToSkip[_currentProcessId].Contains(item.UnitId))
                    //{
                    //    Items.ItemUnitIdsToSkip[_currentProcessId].Add(item.UnitId);
                    //    continue;
                    //}

                    if (item.UnitId == uint.MaxValue) continue;

                    item.IsPlayerOwned = rosterData.List[0].UnitId != uint.MaxValue && item.ItemData.dwOwnerID == rosterData.List[0].UnitId;

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

                    var checkDroppedItem = Items.CheckDroppedItem(item, _currentProcessId);
                    var checkVendorItem = Items.CheckVendorItem(item, _currentProcessId);
                    if (item.IsValidItem && !item.IsInSocket && (checkDroppedItem || checkVendorItem || checkInventoryItem))
                    {
                        Items.LogItem(item, levelId, areaLevel, PlayerUnit.Level, _currentProcessId);
                    }

                    if (item.Item == Item.HoradricCube && !item.IsDropped)
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

                // Player wearing items
                playerUnit.WearingItems = allItems.Where(x => x.IsPlayerOwned && x.ItemModeMapped == ItemModeMapped.Player).ToArray();

                // Belt items
                var belt = allItems.FirstOrDefault(x => x.IsPlayerOwned && x.ItemModeMapped == ItemModeMapped.Player && x.ItemData.BodyLoc == BodyLoc.BELT);
                var beltItems = allItems.Where(x => rosterData.List[0].UnitId != uint.MaxValue && x.ItemModeMapped == ItemModeMapped.Belt).ToArray();

                var beltSize = belt == null ? 1 :
                    new Item[] { Item.Sash, Item.LightBelt }.Contains(belt.Item) ? 2 :
                    new Item[] { Item.Belt, Item.HeavyBelt }.Contains(belt.Item) ? 3 : 4;

                playerUnit.BeltItems = Enumerable.Range(0, 4).Select(i => Enumerable.Range(0, beltSize).Select(j => beltItems.FirstOrDefault(item => item.X == i + j * 4)).ToArray()).ToArray();

                // Unit hover
                var allUnits = ((UnitAny[])playerList.Values.ToArray()).Concat(monsterList).Concat(mercList).Concat(rawObjectUnits).Concat(rawItemUnits);

                var hoveredUnits = allUnits.Where(x => x.IsHovered).ToArray();
                if (hoveredUnits.Length > 0) hoveredUnits[0].IsHovered = false;

                if (lastHoverData.IsHovered)
                {
                    var units = allUnits.Where(x => x.UnitId == lastHoverData.UnitId && x.UnitType == lastHoverData.UnitType).ToArray();
                    if (units.Length > 0) units[0].IsHovered = true;
                }

                // Return data
                _firstMemoryRead = false;
                _errorThrown = false;

                if (currentWindowHandle != GameManager.MainWindowHandle)
                {
                    if (_errorThrown) return null;

                    _errorThrown = true;
                    throw new Exception("Window handle changed in the middle of the frame");
                }

                return new GameData
                {
                    PlayerPosition = playerUnit.Position,
                    MapSeed = mapSeed,
                    MapSeedReady = mapSeedIsReady,
                    Area = levelId,
                    Difficulty = gameDifficulty,
                    MainWindowHandle = currentWindowHandle,
                    PlayerName = playerUnit.Name,
                    PlayerUnit = playerUnit,
                    Players = playerList,
                    Corpses = corpseList,
                    Monsters = monsterList,
                    Mercs = mercList,
                    Summons = new UnitMonster[0] { },
                    Objects = objectList,
                    Missiles = new UnitMissile[0]{ },
                    Items = itemList,
                    AllItems = allItems,
                    ItemLog = Items.ItemLog[_currentProcessId].ToArray(),
                    Session = _sessions[_currentProcessId],
                    Roster = rosterData,
                    MenuOpen = menuData,
                    LastNpcInteracted = lastNpcInteracted,
                    ProcessId = _currentProcessId
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
                    //else if (saveToCache && cache.TryGetValue(unit.HashString, out var seenUnit2) && seenUnit2 is T && !allUnits.ContainsKey(((T)seenUnit2).UnitId))
                    //{
                    //    UseCachedUnit(seenUnit2);
                    //}
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
                Items.ItemDisplayNames.Add(_currentProcessId, new Dictionary<string, string>());
            }
            else
            {
                Items.ItemUnitHashesSeen[_currentProcessId].Clear();
                Items.ItemUnitIdsSeen[_currentProcessId].Clear();
                Items.ItemUnitIdsToSkip[_currentProcessId].Clear();
                Items.InventoryItemUnitIdsToSkip[_currentProcessId].Clear();
                Items.ItemVendors[_currentProcessId].Clear();
                Items.ItemLog[_currentProcessId].Clear();
                Items.ItemDisplayNames[_currentProcessId].Clear();
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
