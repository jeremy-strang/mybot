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

using System.Drawing;
using MapAssist.Files;
using MapAssist.Helpers;
using MapAssist.Settings;
using MapAssist.Types;
using YamlDotNet.Serialization;

namespace MapAssist.Settings
{
    public class MapAssistConfiguration
    {
        public static MapAssistConfiguration Default { get; set; }
        public static MapAssistConfiguration Loaded { get; set; }
        public static void Load()
        {
            Default = ConfigurationParser<MapAssistConfiguration>.ParseConfigurationMain(Properties.Resources.Config);
            Loaded = ConfigurationParser<MapAssistConfiguration>.ParseConfigurationMain(Properties.Resources.Config, $"./Config.yaml");
            Localization.LoadLocalizationFile();
            PointOfInterestHandler.UpdateLocalizationNames();
        }

        public void Save()
        {
            new ConfigurationParser<MapAssistConfiguration>().SerializeToFile(this);
        }

        [YamlMember(Alias = "HotkeyConfiguration", ApplyNamingConventions = false)]
        public HotkeyConfiguration HotkeyConfiguration { get; set; }

        [YamlMember(Alias = "HiddenAreas", ApplyNamingConventions = false)]
        public Area[] HiddenAreas { get; set; }

        [YamlMember(Alias = "RenderingConfiguration", ApplyNamingConventions = false)]
        public RenderingConfiguration RenderingConfiguration { get; set; }

        [YamlMember(Alias = "MapConfiguration", ApplyNamingConventions = false)]
        public MapConfiguration MapConfiguration { get; set; }

        [YamlMember(Alias = "ItemLog", ApplyNamingConventions = false)]
        public ItemLogConfiguration ItemLog { get; set; }

        [YamlMember(Alias = "MapColorConfiguration", ApplyNamingConventions = false)]
        public MapColorConfiguration MapColorConfiguration { get; set; }

        [YamlMember(Alias = "GameInfo", ApplyNamingConventions = false)]
        public GameInfoConfiguration GameInfo { get; set; }

        [YamlMember(Alias = "D2Path", ApplyNamingConventions = false)]
        public string D2LoDPath { get; set; }

        [YamlMember(Alias = "LanguageCode", ApplyNamingConventions = false)]
        public Locale LanguageCode { get; set; }
    }

    public class MapColorConfiguration
    {
        
        [YamlMember(Alias = "Walkable", ApplyNamingConventions = false)]
        public Color? Walkable { get; set; }
        
        [YamlMember(Alias = "Border", ApplyNamingConventions = false)]
        public Color? Border { get; set; }
    }

    public class MapConfiguration
    {
        [YamlMember(Alias = "SuperUniqueMonster", ApplyNamingConventions = false)]
        public IconRendering SuperUniqueMonster { get; set; }

        [YamlMember(Alias = "UniqueMonster", ApplyNamingConventions = false)]
        public IconRendering UniqueMonster { get; set; }

        [YamlMember(Alias = "ChampionMonster", ApplyNamingConventions = false)]
        public IconRendering ChampionMonster { get; set; }

        [YamlMember(Alias = "MinionMonster", ApplyNamingConventions = false)]
        public IconRendering MinionMonster { get; set; }

        [YamlMember(Alias = "NormalMonster", ApplyNamingConventions = false)]
        public IconRendering NormalMonster { get; set; }

        [YamlMember(Alias = "Npc", ApplyNamingConventions = false)]
        public PointOfInterestRendering Npc { get; set; }

        [YamlMember(Alias = "NextArea", ApplyNamingConventions = false)]
        public PointOfInterestRendering NextArea { get; set; }

        [YamlMember(Alias = "PreviousArea", ApplyNamingConventions = false)]
        public PointOfInterestRendering PreviousArea { get; set; }

        [YamlMember(Alias = "Waypoint", ApplyNamingConventions = false)]
        public PointOfInterestRendering Waypoint { get; set; }

        [YamlMember(Alias = "Quest", ApplyNamingConventions = false)]
        public PointOfInterestRendering Quest { get; set; }

        [YamlMember(Alias = "Player", ApplyNamingConventions = false)]
        public PointOfInterestRendering Player { get; set; }

        [YamlMember(Alias = "PartyPlayer", ApplyNamingConventions = false)]
        public PointOfInterestRendering PartyPlayer { get; set; }

        [YamlMember(Alias = "NonPartyPlayer", ApplyNamingConventions = false)]
        public PointOfInterestRendering NonPartyPlayer { get; set; }

        [YamlMember(Alias = "HostilePlayer", ApplyNamingConventions = false)]
        public PointOfInterestRendering HostilePlayer { get; set; }

        [YamlMember(Alias = "MyMerc", ApplyNamingConventions = false)]
        public PointOfInterestRendering MyMerc { get; set; }

        [YamlMember(Alias = "OtherMercs", ApplyNamingConventions = false)]
        public PointOfInterestRendering OtherMercs { get; set; }

        [YamlMember(Alias = "Corpse", ApplyNamingConventions = false)]
        public PointOfInterestRendering Corpse { get; set; }

        [YamlMember(Alias = "Portal", ApplyNamingConventions = false)]
        public PortalRendering Portal { get; set; }

        [YamlMember(Alias = "SuperChest", ApplyNamingConventions = false)]
        public PointOfInterestRendering SuperChest { get; set; }

        [YamlMember(Alias = "NormalChest", ApplyNamingConventions = false)]
        public PointOfInterestRendering NormalChest { get; set; }

        [YamlMember(Alias = "LockedChest", ApplyNamingConventions = false)]
        public PointOfInterestRendering LockedChest { get; set; }

        [YamlMember(Alias = "TrappedChest", ApplyNamingConventions = false)]
        public PointOfInterestRendering TrappedChest { get; set; }

        [YamlMember(Alias = "Shrine", ApplyNamingConventions = false)]
        public PointOfInterestRendering Shrine { get; set; }

        [YamlMember(Alias = "ArmorWeapRack", ApplyNamingConventions = false)]
        public PointOfInterestRendering ArmorWeapRack { get; set; }

        [YamlMember(Alias = "Item", ApplyNamingConventions = false)]
        public PointOfInterestRendering Item { get; set; }
    }
}

public class RenderingConfiguration
{
    [YamlMember(Alias = "Opacity", ApplyNamingConventions = false)]
    public double Opacity { get; set; }

    [YamlMember(Alias = "IconOpacity", ApplyNamingConventions = false)]
    public double IconOpacity { get; set; }

    [YamlMember(Alias = "OverlayMode", ApplyNamingConventions = false)]
    public bool OverlayMode { get; set; }

    [YamlMember(Alias = "Position", ApplyNamingConventions = false)]
    public MapPosition Position { get; set; }

    [YamlMember(Alias = "MonsterHealthBar", ApplyNamingConventions = false)]
    public bool MonsterHealthBar { get; set; }

    [YamlMember(Alias = "ToggleViaInGameMap", ApplyNamingConventions = false)]
    public bool ToggleViaInGameMap { get; set; }

    [YamlMember(Alias = "ToggleViaInGamePanels", ApplyNamingConventions = false)]
    public bool ToggleViaInGamePanels { get; set; }

    [YamlMember(Alias = "StickToLastGameWindow", ApplyNamingConventions = false)]
    public bool StickToLastGameWindow { get; set; }

    [YamlMember(Alias = "Size", ApplyNamingConventions = false)]
    public int Size { get; set; }
    internal int InitialSize { get; set; }

    [YamlMember(Alias = "ZoomLevel", ApplyNamingConventions = false)]
    public double ZoomLevel { get; set; }

    [YamlMember(Alias = "BuffPosition", ApplyNamingConventions = false)]
    public BuffPosition BuffPosition { get; set; }

    [YamlMember(Alias = "BuffSize", ApplyNamingConventions = false)]
    public double BuffSize { get; set; }

    [YamlMember(Alias = "LinesMode", ApplyNamingConventions = false)]
    public MapLinesMode LinesMode { get; set; }
}

public class HotkeyConfiguration
{
    [YamlMember(Alias = "ToggleKey", ApplyNamingConventions = false)]
    public string ToggleKey { get; set; }

    [YamlMember(Alias = "AreaLevelKey", ApplyNamingConventions = false)]
    public string AreaLevelKey { get; set; }

    [YamlMember(Alias = "ZoomInKey", ApplyNamingConventions = false)]
    public string ZoomInKey { get; set; }

    [YamlMember(Alias = "ZoomOutKey", ApplyNamingConventions = false)]
    public string ZoomOutKey { get; set; }
}

public class GameInfoConfiguration
{
    [YamlMember(Alias = "Position", ApplyNamingConventions = false)]
    public GameInfoPosition Position { get; set; }

    [YamlMember(Alias = "ShowGameName", ApplyNamingConventions = false)]
    public bool ShowGameName { get; set; }

    [YamlMember(Alias = "ShowArea", ApplyNamingConventions = false)]
    public bool ShowArea { get; set; }

    [YamlMember(Alias = "ShowDifficulty", ApplyNamingConventions = false)]
    public bool ShowDifficulty { get; set; }

    [YamlMember(Alias = "ShowGameIP", ApplyNamingConventions = false)]
    public bool ShowGameIP { get; set; }

    [YamlMember(Alias = "HuntingIP", ApplyNamingConventions = false)]
    public string HuntingIP { get; set; }

    [YamlMember(Alias = "ShowAreaLevel", ApplyNamingConventions = false)]
    public bool ShowAreaLevel { get; set; }

    [YamlMember(Alias = "ShowOverlayFPS", ApplyNamingConventions = false)]
    public bool ShowOverlayFPS { get; set; }
    
    [YamlMember(Alias = "LabelFont", ApplyNamingConventions = false)]
    public string LabelFont { get; set; }

    [YamlMember(Alias = "LabelFontSize", ApplyNamingConventions = false)]
    public double LabelFontSize { get; set; }

    [YamlMember(Alias = "LabelTextShadow", ApplyNamingConventions = false)]
    public bool LabelTextShadow { get; set; }
}

public class ItemLogConfiguration
{
    [YamlMember(Alias = "Enabled", ApplyNamingConventions = false)]
    public bool Enabled { get; set; }

    [YamlMember(Alias = "Position", ApplyNamingConventions = false)]
    public GameInfoPosition Position { get; set; }

    [YamlMember(Alias = "FilterFileName", ApplyNamingConventions = false)]
    public string FilterFileName { get; set; }

    [YamlMember(Alias = "CheckVendorItems", ApplyNamingConventions = false)]
    public bool CheckVendorItems { get; set; }

    [YamlMember(Alias = "CheckItemOnIdentify", ApplyNamingConventions = false)]
    public bool CheckItemOnIdentify { get; set; }

    [YamlMember(Alias = "PlaySoundOnDrop", ApplyNamingConventions = false)]
    public bool PlaySoundOnDrop { get; set; }

    [YamlMember(Alias = "SoundFile", ApplyNamingConventions = false)]
    public string SoundFile { get; set; }

    [YamlMember(Alias = "SoundVolume", ApplyNamingConventions = false)]
    public int SoundVolume { get; set; }

    [YamlMember(Alias = "DisplayForSeconds", ApplyNamingConventions = false)]
    public double DisplayForSeconds { get; set; }

    [YamlMember(Alias = "LabelFont", ApplyNamingConventions = false)]
    public string LabelFont { get; set; }

    [YamlMember(Alias = "LabelFontSize", ApplyNamingConventions = false)]
    public double LabelFontSize { get; set; }

    [YamlMember(Alias = "LabelTextShadow", ApplyNamingConventions = false)]
    public bool LabelTextShadow { get; set; }
}
