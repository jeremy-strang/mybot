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

namespace MapAssist.Botty
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

        private bool disposed;


        public Api()
        {
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


        public string RetrieveDataFromMemory(Formatting formatting = Formatting.None)
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
                        var player_life = stats.ContainsKey(Stat.Life) ? stats[Stat.Life] >> 8 : int.MaxValue;
                        var player_max_life = stats.ContainsKey(Stat.MaxLife) ? stats[Stat.MaxLife] >> 8 : int.MaxValue;
                        var player_mana = stats.ContainsKey(Stat.Mana) ? stats[Stat.Mana] >> 8 : int.MaxValue;
                        var player_max_mana = stats.ContainsKey(Stat.MaxMana) ? stats[Stat.MaxMana] >> 8 : int.MaxValue;
                        var player_level = stats.ContainsKey(Stat.Level) ? stats[Stat.Level] : int.MaxValue;
                        var player_experience =
                            stats.ContainsKey(Stat.Experience) ? stats[Stat.Experience] : int.MaxValue;
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

                        UnitItem[] flattenedBelt = playerUnit.BeltItems.SelectMany(x => x).ToArray();

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

                        var msg = new
                        {
                            success = true,
                            monsters = new List<dynamic>(),
                            objects = new List<dynamic>(),
                            items = new List<dynamic>(),
                            item_log = new List<dynamic>(),
                            points_of_interest = new List<dynamic>(),
                            player_pos = _gameData.PlayerPosition,
                            area_origin = _areaData.Origin,
                            collision_grid = _areaData.CollisionGrid,
                            current_area = _areaData.Area.ToString(),
                            used_skill = _gameData.PlayerUnit.Skills.UsedSkillId,
                            left_skill = _gameData.PlayerUnit.Skills.LeftSkillId,
                            right_skill = _gameData.PlayerUnit.Skills.RightSkillId,
                            wp_menu = _gameData.MenuOpen,
                            player_life,
                            player_max_life,
                            player_mana,
                            player_max_mana,
                            player_level,
                            player_experience,
                            player_gold,
                            player_stats,
                            player_state_strings = playerUnit.StateStrings,
                            //player_unit = playerUnit.Struct,
                            player_name = playerUnit.Name,
                            player_class = playerUnit.Struct.playerClass.ToString(),
                            static_npcs = new List<dynamic>(),
                            belt_health_pots, // number of health pots in player's belt
                            belt_mana_pots, // number of mana pots in player's belt
                            belt_rejuv_pots, // number of rejuv pots in player's belt
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
                            msg.points_of_interest.Add(new {
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
                            msg.item_log.Add(new
                            {
                                text = item.Text,
                                hash = item.ItemHashString,
                                unit_item = item.UnitItem.ToString(),
                            });
                        }

                        foreach (UnitItem item in _gameData.Items)
                        {
                            msg.items.Add(new
                            {
                                position = item.Position,
                                mode = item.ItemMode,
                                id = item.UnitId,
                                flags = item.ItemData.ItemFlags,
                                quality = item.ItemData.ItemQuality,
                                name = Items.GetItemName(item),
                                base_name = item.ItemBaseName,
                                is_hovered = item.IsHovered,
                            });
                        }

                        return JsonConvert.SerializeObject(msg, formatting);
                    }
                }
            }
            catch (Exception ex)
            {
                //_log.Error(ex);
            }

            return JsonConvert.SerializeObject(new { success = false }, formatting);
        }

        ~Api()
        {
            Dispose();
        }
    }
}
