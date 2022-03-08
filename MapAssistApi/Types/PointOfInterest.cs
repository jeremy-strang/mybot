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

using GameOverlay.Drawing;
using MapAssist.Settings;
using System;

namespace MapAssist.Types
{
    public class PointOfInterest
    {
        public string Label;
        public Area Area;
        public Area NextArea;
        public Point Position;
        public PointOfInterestRendering RenderingSettings;
        public PoiType Type;


        public bool PoiMatchesPortal(UnitObject[] gameDataObjectList, Difficulty difficulty)
        {
            if (Type == PoiType.AreaPortal)
            {
                foreach (var gameObject in gameDataObjectList)
                {
                    if (gameObject.IsPortal)
                    {
                        var area = (Area)Enum.ToObject(typeof(Area), gameObject.ObjectData.InteractType);
                        if (area.PortalLabel(difficulty) == Label)
                        {
                            return true;
                        }
                    }
                }
            }
            return false;
        }
    }

    public enum PoiType
    {
        NextArea,
        PreviousArea,
        Waypoint,
        Quest,
        AreaSpecificQuest,
        AreaPortal,
        Shrine,
        SuperChest,
        ArmorWeapRack
    }
}
