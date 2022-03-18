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

using GameOverlay;
using MapAssist.Helpers;
using MapAssist.Types;
using Newtonsoft.Json;
using NLog;
using System;
using System.Collections.Generic;
using System.Linq;

namespace MapAssist.MyBot
{
    public class Api : IDisposable
    {
        private static readonly Logger _log = LogManager.GetCurrentClassLogger();
        private static readonly object _lock = new object();
        private readonly GameDataReader _gameDataReader;

        private AreaData _areaData;
        private Compositor _compositor = null;
        private volatile GameData _gameData;
        private List<PointOfInterest> _pointsOfInterest;
        private string _currentArea = "";
        private int _currentMapHeight = 0;
        private int _currentMapWidth = 0;
        private double _chicken = 0.5;
        private bool disposed;
        
        public Api(double chicken = 0.5)
        {
            _chicken = chicken;
            _gameDataReader = new GameDataReader();
            TimerService.EnableHighPrecisionTimers();
        }

        public void Dispose()
        {
            // Close the listener
            //listener.Close();
            lock (_lock)
            {
                if (!disposed)
                {
                    disposed = true; // This first to let GraphicsWindow.DrawGraphics know to return instantly
                    if (_compositor != null)
                        _compositor.Dispose(); // This last so it's disposed after GraphicsWindow stops using it
                }
            }
        }

        private struct StatKeyValuePair
        {
            public string key { get; set; }
            public int value { get; set; }
        }

        private bool IsInTown(string currentArea)
        {
            if (currentArea == "RogueEncampment") return true;
            if (currentArea == "LutGholein") return true;
            if (currentArea == "KurastDocks") return true;
            if (currentArea == "ThePandemoniumFortress") return true;
            if (currentArea == "Harrogath") return true;
            return false;
        }

        private List<StatKeyValuePair> GetItemStats(UnitItem item)
        {
            List<StatKeyValuePair> istats = null;
            if (item != null && item.Stats != null)
            {
                istats = item.Stats.Select(it =>
                {
                    Stat key = it.Key;
                    var value = it.Value;
                    if (key == Stat.Life || key == Stat.MaxLife || key == Stat.Mana || key == Stat.MaxMana)
                    {
                        value = value >> 8;
                    }

                    return new StatKeyValuePair { key = key.ToString(), value = value };
                }).ToList();
            }

            return istats;
        }

        public string RetrieveDataFromMemory(bool forceMap = true, Formatting formatting = Formatting.None)
        {
            try
            {
                lock (_lock)
                {
                    (_gameData, _areaData, _pointsOfInterest, _) = _gameDataReader.Get();

                    if (_gameData != null && _areaData != null && _pointsOfInterest != null)
                    {
                        var playerUnit = _gameData.PlayerUnit;
                        Dictionary<Stat, int> stats = playerUnit.Stats;
                        var player_health = stats.ContainsKey(Stat.Life) ? stats[Stat.Life] >> 8 : int.MaxValue;
                        var player_max_health = stats.ContainsKey(Stat.MaxLife) ? stats[Stat.MaxLife] >> 8 : int.MaxValue;
                        var player_health_pct = player_max_health > 0 ? (double)player_health / player_max_health : 1.0;
                        var player_mana = stats.ContainsKey(Stat.Mana) ? stats[Stat.Mana] >> 8 : int.MaxValue;
                        var player_max_mana = stats.ContainsKey(Stat.MaxMana) ? stats[Stat.MaxMana] >> 8 : int.MaxValue;
                        var player_mana_pct = player_max_mana > 0 ? (double)player_mana / player_max_mana : 1.0;
                        var player_level = stats.ContainsKey(Stat.Level) ? stats[Stat.Level] : int.MaxValue;
                        var player_experience = stats.ContainsKey(Stat.Experience) ? stats[Stat.Experience] : int.MaxValue;
                        var player_gold = stats.ContainsKey(Stat.Gold) ? stats[Stat.Gold] : int.MaxValue;
                        var player_stats = stats.Select(item =>
                        {
                            Stat key = item.Key;
                            var value = item.Value;
                            if (key == Stat.Life || key == Stat.MaxLife || key == Stat.Mana || key == Stat.MaxMana)
                            {
                                value = value >> 8;
                            }

                            return new { key = key.ToString(), value };
                        }).ToList();

                        UnitItem[] flattened_belt = playerUnit.BeltItems.SelectMany(x => x).ToArray();

                        var belt_health_pots = 0;
                        var belt_mana_pots = 0;
                        var belt_rejuv_pots = 0;
                        if (_gameData.BeltItems != null)
                        {
                            foreach (var item in _gameData.BeltItems)
                            {
                                if ((item.ItemBaseName ?? "").Contains("Healing Potion")) belt_health_pots++;
                                else if ((item.ItemBaseName ?? "").Contains("Mana Potion")) belt_mana_pots++;
                                else if ((item.ItemBaseName ?? "").Contains("Rejuvenation Potion")) belt_rejuv_pots++;
                            }
                        }

                        var merc = _gameData.Mercs.Where(a => a.IsPlayerOwned).FirstOrDefault();
                        var merc_health_pct = 0.0;
                        dynamic player_merc = null;
                        if (merc != null)
                        {
                            player_merc = new
                            {
                                position = merc.Position,
                                immunities = merc.Immunities,
                                unit_type = merc.UnitType.ToString(),
                                type = merc.MonsterData.MonsterType.ToString(),
                                id = merc.UnitId,
                                name = ((Npc)merc.TxtFileNo).ToString(),
                                mode = merc.Struct.Mode,
                                is_targetable_corpse = merc.IsTargetableCorpse,
                                number = merc.TxtFileNo,
                                heath_percentage = merc.HealthPercentage,
                                corpse = merc.IsCorpse,
                                bossID = merc.MonsterData.BossLineID,
                                state_strings = merc.StateStrings,
                                is_hovered = merc.IsHovered,
                            };
                            merc_health_pct = player_merc.heath_percentage;
                        }

                        var corpses = new List<dynamic>();
                        dynamic player_corpse = null;

                        foreach (var corpse in _gameData.Corpses.Where(a => a.IsCorpse && a.IsPlayer).ToList())
                        {
                            if (corpse.Name == playerUnit.Name)
                            {
                                var pcorpse = new
                                {
                                    position = corpse.Position,
                                    id = corpse.UnitId,
                                    name = corpse.Name,
                                    is_hovered = corpse.IsHovered,
                                    is_corpse = corpse.IsCorpse,
                                    player_class = corpse.Struct.playerClass,
                                    unit_type = corpse.Struct.UnitType,
                                    mode = corpse.Struct.Mode,
                                };
                                player_corpse = pcorpse;
                                corpses.Add(pcorpse);
                            }
                        }

                        var item_on_cursor = false;
                        var items = new List<dynamic>();
                        foreach (UnitItem item in _gameData.AllItems) //.Where(x => x.ItemModeMapped == ItemModeMapped.Ground))
                        {
                            if (item.ItemMode == ItemMode.ONCURSOR)
                            {
                                item_on_cursor = true;
                            }

                            if (item.ItemModeMapped == ItemModeMapped.Ground)
                            {
                                items.Add(new
                                {
                                    position = new int[2] { (int)item.Position.X, (int)item.Position.Y },
                                    id = item.UnitId,
                                    flags = item.ItemData.ItemFlags.ToString(),
                                    quality = item.ItemData.ItemQuality.ToString(),
                                    name = Items.GetItemName(item),
                                    base_name = item.ItemBaseName,
                                    is_hovered = item.IsHovered,
                                    item_mode = item.ItemMode.ToString(),
                                    item_mode_mapped = item.ItemModeMapped.ToString(),
                                    stats = GetItemStats(item),
                                    is_identified = item.IsIdentified,
                                    inventory_page = item.ItemData.InvPage.ToString(),
                                });
                            }
                        }

                        var current_area = _areaData.Area.ToString();
                        var mapH = 0;
                        var mapW = 0;
                        if (_areaData.CollisionGrid != null)
                        {
                            mapH = _areaData.CollisionGrid.GetLength(0);
                            if (mapH > 0)
                            {
                                mapW = _areaData.CollisionGrid[0].GetLength(0);
                            }
                        }

                        var map_changed = current_area != _currentArea || mapH != _currentMapHeight || mapW != _currentMapWidth;
                        _currentArea = current_area;
                        _currentMapHeight = mapH;
                        _currentMapWidth = mapW;

                        var in_game = _gameData.MenuOpen.InGame;
                        var should_chicken = in_game && player_health_pct < _chicken && !IsInTown(current_area) && _areaData.Area != Area.None;

                        var inventory_open = _gameData.MenuOpen.Inventory;
                        var stash_open = _gameData.MenuOpen.Stash;
                        var shop_open = _gameData.MenuOpen.NpcShop;
                        var msg = new
                        {
                            map_changed = map_changed || forceMap,
                            success = true,
                            should_chicken,
                            monsters = new List<dynamic>(),
                            objects = new List<dynamic>(),
                            items,
                            items_logged = new List<dynamic>(),
                            points_of_interest = new List<dynamic>(),
                            corpses,
                            player_corpse,
                            player_pos_world = _gameData.PlayerPosition,
                            area_origin = _areaData.Origin,
                            collision_grid = map_changed || forceMap ? _areaData.CollisionGrid : null,
                            current_area,
                            used_skill = _gameData.PlayerUnit.Skills.UsedSkillId,
                            left_skill = _gameData.PlayerUnit.Skills.LeftSkillId,
                            right_skill = _gameData.PlayerUnit.Skills.RightSkillId,
                            menus = _gameData.MenuOpen,
                            in_game,
                            inventory_open = _gameData.MenuOpen.Inventory,
                            character_open = _gameData.MenuOpen.Character,
                            skill_select_open = _gameData.MenuOpen.SkillSelect,
                            skill_tree_open = _gameData.MenuOpen.SkillTree,
                            chat_open = _gameData.MenuOpen.Chat,
                            npc_interact_open = _gameData.MenuOpen.NpcInteract,
                            esc_menu_open = _gameData.MenuOpen.EscMenu,
                            map_open = _gameData.MenuOpen.Map,
                            npc_shop_open = _gameData.MenuOpen.NpcShop,
                            quest_log_open = _gameData.MenuOpen.QuestLog,
                            waypoint_open = _gameData.MenuOpen.Waypoint,
                            party_open = _gameData.MenuOpen.Party,
                            stash_open = _gameData.MenuOpen.Stash,
                            cube_open = _gameData.MenuOpen.Cube,
                            potion_belt_open = _gameData.MenuOpen.PotionBelt,
                            mercenary_inventory_open = _gameData.MenuOpen.MercenaryInventory,
                            player_health,
                            player_max_health,
                            player_health_pct,
                            player_mana,
                            player_max_mana,
                            player_mana_pct,
                            player_experience,
                            player_gold,
                            player_stats,
                            player_state_strings = playerUnit.StateStrings,
                            //player_unit = playerUnit.Struct,
                            player_name = playerUnit.Name,
                            player_class = playerUnit.Struct.playerClass.ToString(),
                            player_level,
                            player_id = playerUnit.UnitId,
                            player_merc,
                            merc_health_pct,
                            static_npcs = new List<dynamic>(),
                            belt_health_pots, // number of health pots in player's belt
                            belt_mana_pots, // number of mana pots in player's belt
                            belt_rejuv_pots, // number of rejuv pots in player's belt
                            flattened_belt,
                            item_on_cursor,
                        };
                        foreach (var m in _areaData.NPCs)
                        {
                            msg.static_npcs.Add(new
                            {
                                name = m.Key.ToString(),
                                position = m.Value,
                            });
                        }

                        foreach (UnitMonster m in _gameData.Monsters)
                        {
                            if (m.UnitType == UnitType.Monster)
                            {
                                msg.monsters.Add(new
                                {
                                    position = m.Position,
                                    immunities = m.Immunities,
                                    unit_type = m.UnitType.ToString(),
                                    type = m.MonsterData.MonsterType.ToString(),
                                    id = m.UnitId,
                                    name = ((Npc)m.TxtFileNo).ToString(),
                                    mode = m.Struct.Mode,
                                    is_targetable_corpse = m.IsTargetableCorpse,
                                    number = m.TxtFileNo,
                                    heath_percentage = m.HealthPercentage,
                                    corpse = m.IsCorpse,
                                    bossID = m.MonsterData.BossLineID,
                                    state_strings = m.StateStrings,
                                    is_hovered = m.IsHovered,
                                });
                            }
                        }

                        foreach (PointOfInterest p in _pointsOfInterest)
                        {
                            //Console.WriteLine(p.Label);
                            msg.points_of_interest.Add(new
                            {
                                position = p.Position,
                                type = p.Type,
                                label = p.Label,
                            });
                        }

                        foreach (UnitObject o in _gameData.Objects)
                        {
                            if (o.UnitType == UnitType.Object)
                            {
                                msg.objects.Add(new
                                {
                                    position = o.Position,
                                    id = o.UnitId,
                                    selectable = o.ObjectData.InteractType != 0x00,
                                    name = ((GameObject)o.TxtFileNo).ToString(),
                                    mode = o.Struct.Mode,
                                    is_hovered = o.IsHovered,
                                });
                            }
                        }

                        //ItemLog = Items.ItemLog[_currentProcessId].ToArray(),
                        foreach (ItemLogEntry item in _gameData.ItemLog)
                        {
                            msg.items_logged.Add(new
                            {
                                text = item.Text,
                                hash = item.ItemHashString,
                                position = new int[2] { (int)item.UnitItem.Position.X, (int)item.UnitItem.Position.Y },
                                id = item.UnitItem.UnitId,
                                flags = item.UnitItem.ItemData.ItemFlags.ToString(),
                                quality = item.UnitItem.ItemData.ItemQuality.ToString(),
                                name = Items.GetItemName(item.UnitItem),
                                base_name = item.UnitItem.ItemBaseName,
                                is_hovered = item.UnitItem.IsHovered,
                                item_mode = item.UnitItem.ItemMode.ToString(),
                                item_mode_mapped = item.UnitItem.ItemModeMapped.ToString(),
                                stats = GetItemStats(item.UnitItem),
                                is_identified = item.UnitItem.IsIdentified,
                                inventory_page = item.UnitItem.ItemData.InvPage.ToString(),
                            });
                        }

                        return JsonConvert.SerializeObject(msg, formatting);
                    }
                }
            }
            catch (Exception ex)
            {
                //_log.Error(ex);
                //_log.Error(ex.StackTrace);
            }

            return JsonConvert.SerializeObject(new { success = false }, formatting);
        }

        ~Api()
        {
            Dispose();
        }
    }
}
