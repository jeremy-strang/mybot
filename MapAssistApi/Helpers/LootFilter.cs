﻿using MapAssist.Settings;
using MapAssist.Types;
using System;
using System.Collections.Generic;
using System.Linq;

namespace MapAssist.Helpers
{
    public static class LootFilter
    {
        public static (bool, ItemFilter) Filter(UnitItem item, int areaLevel, int playerLevel)
        {
            // Skip low quality items
            var lowQuality = (item.ItemData.ItemFlags & ItemFlags.IFLAG_LOWQUALITY) == ItemFlags.IFLAG_LOWQUALITY;
            if (lowQuality) return (false, null);

            // Populate a list of filter rules by combining rules from "Any" and the item base name
            // Use only one list or the other depending on if "Any" exists
            var matches = LootLogConfiguration.Filters.Where(f => f.Key == Item.Any || (uint)f.Key == item.TxtFileNo).ToList();

            // Early breakout
            // We know that there is an item in here without any actual filters
            // So we know that simply having the name match means we can return true
            if (matches.Any(kv => kv.Value == null))
            {
                return (!item.IsAnyPlayerHolding, null);
            }

            // Scan the list of rules
            foreach (var rule in matches.SelectMany(kv => kv.Value))
            {
                // Skip generic unid rules for identified items on ground or in inventory
                if (item.IsIdentified && (item.IsDropped || item.IsAnyPlayerHolding) && rule.TargetsUnidItem()) continue;

                if (item.IsInStore && !rule.CheckVendor) continue;

                // Requirement check functions
                var requirementsFunctions = new Dictionary<string, Func<bool>>()
                {
                    ["Qualities"] = () => rule.Qualities.Contains(item.ItemData.ItemQuality),
                    ["Sockets"] = () => rule.Sockets.Contains(Items.GetItemStat(item, Stats.Stat.NumSockets)),
                    ["Ethereal"] = () => item.IsEthereal == rule.Ethereal,
                    ["MinAreaLevel"] = () => areaLevel >= rule.MinAreaLevel,
                    ["MaxAreaLevel"] = () => areaLevel <= rule.MaxAreaLevel,
                    ["MinPlayerLevel"] = () => playerLevel >= rule.MinPlayerLevel,
                    ["MaxPlayerLevel"] = () => playerLevel <= rule.MaxPlayerLevel,
                    ["MinQualityLevel"] = () => Items.GetQualityLevel(item) >= rule.MinQualityLevel,
                    ["MaxQualityLevel"] = () => Items.GetQualityLevel(item) <= rule.MaxQualityLevel,
                    ["AllAttributes"] = () => Items.GetItemStatAllAttributes(item) >= rule.AllAttributes,
                    ["AllResist"] = () => Items.GetItemStatResists(item, false) >= rule.AllResist,
                    ["SumResist"] = () => Items.GetItemStatResists(item, true) >= rule.SumResist,
                    ["ClassSkills"] = () =>
                    {
                        if (rule.ClassSkills.Count() == 0) return true;
                        return rule.ClassSkills.All(subrule => Items.GetItemStatAddClassSkills(item, subrule.Key).Item2 >= subrule.Value);
                    },
                    ["SkillTrees"] = () =>
                    {
                        if (rule.SkillTrees.Count() == 0) return true;
                        return rule.SkillTrees.All(subrule => Items.GetItemStatAddSkillTreeSkills(item, subrule.Key).Item2 >= subrule.Value);
                    },
                    ["Skills"] = () =>
                    {
                        if (rule.Skills.Count() == 0) return true;
                        return rule.Skills.All(subrule => Items.GetItemStatAddSingleSkills(item, subrule.Key).Item2 >= subrule.Value);
                    },
                    ["SkillCharges"] = () =>
                    {
                        if (rule.SkillCharges.Count() == 0) return true;
                        return rule.SkillCharges.All(subrule => Items.GetItemStatAddSkillCharges(item, subrule.Key).Item1 >= subrule.Value);
                    },
                };

                foreach (var (stat, shift) in Stats.StatShifts.Select(x => (x.Key, x.Value)))
                {
                    requirementsFunctions.Add(stat.ToString(), () => Items.GetItemStatShifted(item, stat) >= (int)rule[stat]);
                }

                var requirementMet = true;
                foreach (var property in rule.GetType().GetProperties())
                {
                    if (property.PropertyType == typeof(object)) continue; // This is the item from Stat property

                    var propertyValue = rule.GetType().GetProperty(property.Name).GetValue(rule, null);
                    if (propertyValue == null) continue;

                    if (requirementsFunctions.TryGetValue(property.Name, out var requirementFunc))
                    {
                        requirementMet &= requirementFunc();
                    }
                    else if (Enum.TryParse<Stats.Stat>(property.Name, out var stat))
                    {
                        requirementMet &= Stats.NegativeValueStats.Contains(stat)
                            ? (int)propertyValue < 0 && Items.GetItemStat(item, stat) <= (int)propertyValue
                            : Items.GetItemStat(item, stat) >= (int)propertyValue;
                    }
                    if (!requirementMet) break;
                }
                if (!requirementMet) continue;

                // Item meets all filter requirements
                return (true, rule);
            }

            return (false, null);
        }
    }
}
