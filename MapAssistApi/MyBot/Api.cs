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

using GameOverlay;
using MapAssist.Helpers;
using MapAssist.Structs;
using MapAssist.Types;
using Newtonsoft.Json;
using NLog;
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using static MapAssist.Types.Stats;

namespace MapAssist.MyBot
{
    public class Api : IDisposable
    {
        private const string API_VERSION = "1.0.3";
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
        private float _chicken = 0.5F;
        private float _emergencyChicken = 0.0F;
        private float _mercChicken = 0.0F;
        private bool _disposed;
        private IBotConfig _config;
        private HashSet<string> _townNames = new HashSet<string>()
        {
            "RogueEncampment",
            "LutGholein",
            "KurastDocks",
            "ThePandemoniumFortress",
            "Harrogath",
        };
        private HashSet<Stat> _relevantPlayerStats = new HashSet<Stat>() {
            Stat.Strength,
            Stat.Energy,
            Stat.Dexterity,
            Stat.Vitality,
            Stat.Life,
            Stat.MaxLife,
            Stat.Mana,
            Stat.MaxMana,
            Stat.Level,
            Stat.Experience,
            Stat.Gold,
            Stat.StashGold,
            Stat.VelocityPercent,
            Stat.AttackRate,
            Stat.Durability,
            Stat.MaxDurability,
            Stat.LastSentHPPercent,
            Stat.MaxManaPercent,
            Stat.FasterCastRate,
            Stat.AllSkills,
            Stat.FasterRunWalk,
            Stat.FireResist,
            Stat.LightningResist,
            Stat.ColdResist,
            Stat.PoisonResist,
            Stat.MagicFind,
            Stat.GoldFind,
        };

        private HashSet<Types.Item> _magicItemsToUpdate = new HashSet<Types.Item>() {
            //Types.Item.AssaultHelmet,
            //Types.Item.AvengerGuard,
            //Types.Item.SavageHelmet,
            //Types.Item.SlayerGuard,
        };

        private HashSet<Types.Item> _rareItemsToUpdate = new HashSet<Types.Item>() {
            //Types.Item.AssaultHelmet,
            //Types.Item.AvengerGuard,
            //Types.Item.SavageHelmet,
            //Types.Item.SlayerGuard,
            Types.Item.Ring,
            Types.Item.Amulet,
        };

        public Api(IBotConfig config = null)
        {
            _config = config;
            _chicken = config.GetValue("char", "chicken", 0.5F);
            _emergencyChicken = config.GetValue("char", "emergency_chicken", 0.0F);
            _mercChicken = config.GetValue("char", "merc_chicken", 0.0F);
            _gameDataReader = new GameDataReader();
            TimerService.EnableHighPrecisionTimers();
        }

        public void Dispose()
        {
            // Close the listener
            //listener.Close();
            lock (_lock)
            {
                if (!_disposed)
                {
                    _disposed = true; // This first to let GraphicsWindow.DrawGraphics know to return instantly
                    if (_compositor != null)
                        _compositor.Dispose(); // This last so it's disposed after GraphicsWindow stops using it
                }
            }
        }

        private void KillD2r()
        {
            var id = Process.GetCurrentProcess().SessionId;
            var procs = Process.GetProcessesByName("D2R");
            foreach (var proc in procs)
            {
                if (proc.SessionId == id)
                {
                    try { proc.Kill(); } catch (Exception) { }
                }
            }
        }

        private struct StatKeyValuePair
        {
            public string key { get; set; }
            public double value { get; set; }
        }

        private bool IsInTown(string currentArea)
        {
            return _townNames.Contains(currentArea);
        }

        private bool ShouldUpdateItem(UnitItem item)
        {
            var result = false;
            if (item != null && item.ItemModeMapped == ItemModeMapped.Ground)
            {
                result = item.ItemData.ItemQuality == ItemQuality.UNIQUE ||
                    item.ItemData.ItemQuality == ItemQuality.SET ||
                    (item.ItemData.ItemQuality == ItemQuality.RARE && _rareItemsToUpdate.Contains(item.Item)) ||
                    (item.ItemData.ItemQuality == ItemQuality.MAGIC && _magicItemsToUpdate.Contains(item.Item)) ||
                    item.Item == Types.Item.Jewel ||
                    item.Item == Types.Item.SmallCharm ||
                    item.Item == Types.Item.GrandCharm ||
                    item.Item.ToString().Contains("Rune");
            }
            return result;
        }

        private List<StatKeyValuePair> GetItemStats(UnitItem item, PlayerClass playerClass)
        {
            var istats = new List<StatKeyValuePair>();
            if (item != null && item.StatLayers != null)
            {
                foreach (var (stat, values) in item.StatLayers.Select(x => (x.Key, x.Value)))
                {
                    var name = stat.ToString();

                    foreach (var (layer, value) in values.Select(x => (x.Key, x.Value)))
                    {
                        var cleanedValue = (double)value;

                        if (Stats.StatShifts.ContainsKey(stat))
                        {
                            cleanedValue = (double)Items.GetItemStatShifted(item, stat);
                        }
                        else if (Stats.StatDivisors.ContainsKey(stat))
                        {
                            cleanedValue = Items.GetItemStatDecimal(item, stat);
                        }
                        else if (stat == Stats.Stat.AddClassSkills)
                        {
                            var (classSkills, points) = Items.GetItemStatAddClassSkills(item, (PlayerClass)layer);
                            name = classSkills[0].ToString();
                            cleanedValue = points;
                        }
                        else if (stat == Stats.Stat.AddSkillTab)
                        {
                            var (skillTrees, points) = Items.GetItemStatAddSkillTreeSkills(item, (SkillTree)layer);
                            name = skillTrees[0].ToString();
                            cleanedValue = (double)points;
                        }
                        else if (stat == Stats.Stat.SingleSkill || stat == Stats.Stat.NonClassSkill)
                        {
                            var (skills, points) = Items.GetItemStatAddSingleSkills(item, (Skill)layer);
                            name = skills[0].ToString();
                            cleanedValue = (double)points;
                        }
                        else if (stat == Stats.Stat.ItemChargedSkill)
                        {
                            var skill = (Skill)(layer >> 6);

                            var (skillLevel, currentCharges, maxCharges) = Items.GetItemStatAddSkillCharges(item, skill);
                            name = skill.ToString() + "Charges";

                            var chargesText = "";
                            if (currentCharges > 0 && maxCharges > 0)
                            {
                                chargesText = $"{currentCharges}/{maxCharges}";
                            }

                            cleanedValue = (double)skillLevel;
                        }
                        else if (stat.ToString().StartsWith("SkillOn"))
                        {
                            var skill = (Skill)(layer >> 6);
                            var chance = layer % (1 << 6);

                            name = skill.ToString() + "Chance";

                            cleanedValue = (double)chance;
                        }
                        else if (stat == Stats.Stat.Aura)
                        {
                            var skill = (Skill)layer;

                            name = skill.ToString() + "Aura";

                            cleanedValue = (double)value;
                        }

                        var thisAffix = new StatKeyValuePair()
                        {
                            key = name,
                            value = cleanedValue
                        };
                        istats.Add(thisAffix);
                    }
                }
            }
            return istats;
        }

        private dynamic CleanItem(UnitItem item, PlayerClass playerClass)
        {
            var unique_name = "";
            var set_name = "";
            if (item.ItemData.ItemQuality == ItemQuality.UNIQUE)
            {
                unique_name = Items.GetUniqueName(item);
            }
            else if (item.ItemData.ItemQuality == ItemQuality.SET)
            {
                set_name = Items.GetSetName(item);
            }

            var sockets = 0;
            if (item.Stats != null)
            {
                item.Stats.TryGetValue(Stat.NumSockets, out sockets);
            }

            var defense = 0;
            if (item.Stats != null)
            {
                item.Stats.TryGetValue(Stat.Defense, out defense);
            }

            var flags = item.ItemData.ItemFlags.ToString();
            var is_ethereal = flags.Contains("IFLAG_ETHEREAL");

            return new
            {
                position = new int[2] { (int)item.Position.X, (int)item.Position.Y },
                id = item.UnitId,
                quality = item.ItemData.ItemQuality,
                name = Items.GetItemName(item),
                stash_tab = item.StashTab,
                vendor_owner = item.VendorOwner.ToString(),
                is_hovered = item.IsHovered,
                mode = item.ItemMode.ToString(),
                mode_mapped = item.ItemModeMapped.ToString(),
                stats = GetItemStats(item, playerClass),
                inventory_page = item.ItemData.InvPage.ToString(),
                tier = Items.GetItemTier(item),
                type = item.Item.ToString(),
                flags,
                sockets,
                defense,
                set_name,
                unique_name,
                is_ethereal,
                is_identified = item.IsIdentified,
                //item,
            };
        }

        public string RetrieveDataFromMemory(bool forceMap = true, Formatting formatting = Formatting.None)
        {
            var error = "";
            var error_trace = "";
            var success = false;
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
                        var player_level_progress = playerUnit.LevelProgress;
                        var player_gold = stats.ContainsKey(Stat.Gold) ? stats[Stat.Gold] : int.MaxValue;

                        var player_stats = stats.Where(item => _relevantPlayerStats.Contains(item.Key)).Select(item =>
                        {
                            Stat key = item.Key;
                            var value = item.Value;
                            if (key == Stat.Life || key == Stat.MaxLife || key == Stat.Mana || key == Stat.MaxMana)
                            {
                                value = value >> 8;
                            }

                            return new { key = key.ToString(), value };
                        }).ToList();

                        var belt_health_pots = 0;
                        var belt_mana_pots = 0;
                        var belt_rejuv_pots = 0;
                        dynamic belt0 = null;
                        dynamic belt1 = null;
                        dynamic belt2 = null;
                        dynamic belt3 = null;
                        foreach (var item in playerUnit.BeltItems.SelectMany(x => x).ToList())
                        {
                            if (item != null)
                            {
                                if (item.ItemBaseName.Contains("Heal"))
                                {
                                    belt_health_pots++;
                                }
                                else if (item.ItemBaseName.Contains("Mana"))
                                {
                                    belt_mana_pots++;
                                }
                                else if (item.ItemBaseName.Contains("Rejuv"))
                                {
                                    belt_rejuv_pots++;
                                }

                                if (item.Position.X == 0)
                                {
                                    belt0 = new
                                    {
                                        name = "" + item.ItemBaseName,
                                        hash_string = "" + item.HashString,
                                    };
                                }
                                else if (item.Position.X == 1)
                                {
                                    belt1 = new
                                    {
                                        name = "" + item.ItemBaseName,
                                        hash_string = "" + item.HashString,
                                    };
                                }
                                else if (item.Position.X == 2)
                                {
                                    belt2 = new
                                    {
                                        name = "" + item.ItemBaseName,
                                        hash_string = "" + item.HashString,
                                    };
                                }
                                else if (item.Position.X == 3)
                                {
                                    belt3 = new
                                    {
                                        name = "" + item.ItemBaseName,
                                        hash_string = "" + item.HashString,
                                    };
                                }
                            }
                        }
                        var flattened_belt = new List<dynamic>() { belt0, belt1, belt2, belt3 };

                        var merc = _gameData.Mercs.Where(a => a.IsPlayerOwned).FirstOrDefault();
                        var merc_health_pct = 1.0;
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
                        var in_town = IsInTown(current_area);
                        var should_chicken = in_game && !in_town && _areaData.Area != Area.None && (
                            (player_health_pct < _chicken) ||
                            (merc_health_pct < _mercChicken));

                        var should_emergency_chicken = in_game && !in_town && _areaData.Area != Area.None && player_health_pct < _emergencyChicken && player_health > 0;

                        if (should_emergency_chicken)
                        {
                            KillD2r();
                            throw new Exception("Killed D2R due to emergency chicken threshold of " + _emergencyChicken + " being met (player life: " + player_health_pct + ")");
                        }

                        var inventory_open = _gameData.MenuOpen.Inventory;
                        var stash_open = _gameData.MenuOpen.Stash;
                        var shop_open = _gameData.MenuOpen.NpcShop;

                        var item_on_cursor = false;
                        var items = new List<dynamic>();
                        var inventory_items = new List<dynamic>();
                        var stash_items = new List<dynamic>();
                        var cube_items = new List<dynamic>();
                        var vendor_items = new List<dynamic>();
                        var equipped_items = new List<dynamic>();
                        var merc_items = new List<dynamic>();
                        var logged_items = new List<dynamic>();
                        foreach (UnitItem item in _gameData.AllItems) //.Where(x => x.ItemModeMapped == ItemModeMapped.Ground))
                        {
                            if (item.ItemMode == ItemMode.ONCURSOR)
                            {
                                item_on_cursor = true;
                            }

                            if (ShouldUpdateItem(item))
                            {
                                item.Update();
                            }

                            if (item.ItemModeMapped == ItemModeMapped.Ground)
                            {
                                if (item.Item != Types.Item.Gold || (item.Stats != null && item.Stats.TryGetValue(Stat.Gold, out var goldAmount) && goldAmount > 2000))
                                {
                                    items.Add(CleanItem(item, playerUnit.Struct.playerClass));
                                }
                            }
                            else if (item.ItemModeMapped == ItemModeMapped.Inventory)
                            {
                                inventory_items.Add(CleanItem(item, playerUnit.Struct.playerClass));
                            }
                            else if (in_town) // Only populate this data in town for performance
                            {
                                if (item.ItemModeMapped == ItemModeMapped.Stash)
                                {
                                    stash_items.Add(CleanItem(item, playerUnit.Struct.playerClass));
                                }
                                else if (item.ItemModeMapped == ItemModeMapped.Vendor)
                                {
                                    vendor_items.Add(CleanItem(item, playerUnit.Struct.playerClass));
                                }
                                else if (item.ItemModeMapped == ItemModeMapped.Cube)
                                {
                                    cube_items.Add(CleanItem(item, playerUnit.Struct.playerClass));
                                }
                                else if (item.ItemModeMapped == ItemModeMapped.Mercenary)
                                {
                                    merc_items.Add(CleanItem(item, playerUnit.Struct.playerClass));
                                }
                                else if (item.ItemModeMapped == ItemModeMapped.Player)
                                {
                                    equipped_items.Add(CleanItem(item, playerUnit.Struct.playerClass));
                                }
                            }
                        }

                        var static_npcs = new List<dynamic>();
                        foreach (var m in _areaData.NPCs)
                        {
                            static_npcs.Add(new
                            {
                                name = m.Key.ToString(),
                                position = m.Value,
                            });
                        }

                        var monsters = new List<dynamic>();
                        foreach (UnitMonster m in _gameData.Monsters)
                        {
                            if (m.UnitType == UnitType.Monster)
                            {
                                var area_x = m.Position.X - _areaData.Origin.X;
                                var area_y = m.Position.Y - _areaData.Origin.Y;
                                if (area_x > 0 && area_y > 0 && area_x < _currentMapWidth && area_y < _currentMapHeight)
                                {
                                    monsters.Add(new
                                    {
                                        id = m.UnitId,
                                        boss_id = m.MonsterData.BossLineID,
                                        npc = m.Npc,
                                        position = m.Position,
                                        immunities = m.Immunities != null ? m.Immunities.Select(a => a.ToString()).ToList() : new List<string>(),
                                        unit_type = m.UnitType.ToString(),
                                        type = m.MonsterData.MonsterType.ToString(),
                                        name = ((Npc)m.TxtFileNo).ToString(),
                                        mode = m.Struct.Mode,
                                        is_targetable_corpse = m.IsTargetableCorpse,
                                        number = m.TxtFileNo,
                                        heath_percentage = m.HealthPercentage,
                                        corpse = m.IsCorpse,
                                        state_strings = m.StateStrings,
                                        is_hovered = m.IsHovered,
                                    });
                                }
                            }
                        }

                        var points_of_interest = new List<dynamic>();
                        foreach (PointOfInterest p in _pointsOfInterest)
                        {
                            //Console.WriteLine(p.Label);
                            points_of_interest.Add(new
                            {
                                position = p.Position,
                                type = p.Type,
                                label = p.Label,
                            });
                        }

                        var objects = new List<dynamic>();
                        foreach (UnitObject o in _gameData.Objects)
                        {
                            if (o.UnitType == UnitType.Object)
                            {
                                objects.Add(new
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

                        var usedSkill = _gameData.PlayerUnit.Skills.UsedSkillId;
                        var leftSkill = _gameData.PlayerUnit.Skills.LeftSkillId;
                        var rightSkill = _gameData.PlayerUnit.Skills.RightSkillId;
                        var player_skills = new List<dynamic>();
                        if (in_town)
                        {
                            foreach (var s in _gameData.PlayerUnit.Skills.AllSkills)
                            {
                                player_skills.Add(new
                                {
                                    skill = s.Skill.ToString(),
                                    charges = s.Charges,
                                    hard_points = s.HardPoints,
                                    quantity = s.Quantity,
                                });
                            }
                        }

                        success = true;
                        var msg = new
                        {
                            API_VERSION,
                            map_changed = map_changed || forceMap,
                            success,
                            error,
                            error_trace,
                            in_game,
                            in_town,
                            should_chicken,
                            corpses,
                            player_corpse,
                            player_pos_world = _gameData.PlayerPosition,
                            area_origin = _areaData.Origin,
                            current_area,
                            used_skill = usedSkill.ToString(),
                            left_skill = leftSkill.ToString(),
                            left_skill_data = _gameData.PlayerUnit.Skills.AllSkills.Where(s => s.Skill == leftSkill).FirstOrDefault(),
                            right_skill = rightSkill.ToString(),
                            right_skill_data = _gameData.PlayerUnit.Skills.AllSkills.Where(s => s.Skill == rightSkill).FirstOrDefault(),
                            player_skills,
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
                            player_level_progress,
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
                            belt_health_pots, // number of health pots in player's belt
                            belt_mana_pots, // number of mana pots in player's belt
                            belt_rejuv_pots, // number of rejuv pots in player's belt
                            item_on_cursor,
                            items,
                            inventory_items,
                            stash_items,
                            cube_items,
                            vendor_items,
                            equipped_items,
                            merc_items,
                            logged_items,
                            flattened_belt,
                            collision_grid = map_changed || forceMap ? _areaData.CollisionGrid : null,
                            static_npcs,
                            objects,
                            monsters,
                            points_of_interest,
                            map_height = _currentMapHeight,
                            map_width = _currentMapWidth,
                        };

                        return JsonConvert.SerializeObject(msg, formatting);
                    }
                    else
                    {
                        _currentMapHeight = 0;
                        _currentMapWidth = 0;
                        _currentArea = "";
                        success = false;
                    }
                }
            }
            catch (Exception ex)
            {
                error = ex.ToString();
                error_trace = ex.StackTrace;
                success = false;
            }

            return JsonConvert.SerializeObject(new {
                API_VERSION,
                success,
                error,
                error_trace,
            }, formatting);
        }

        ~Api()
        {
            Dispose();
        }
    }
}
