﻿using GameOverlay.Drawing;
using MapAssist.Settings;
using MapAssist.Types;
using System.Collections.Generic;
using System.Linq;

namespace MapAssist.Helpers
{
    public static class PointOfInterestHandler
    {
        private static Dictionary<GameObject, string> QuestObjects;

        private static Dictionary<Area, Dictionary<GameObject, string>> AreaSpecificQuestObjects;

        private static readonly Dictionary<Area, Area> AreaPreferredNextArea = new Dictionary<Area, Area>()
        {
            [Area.BloodMoor] = Area.ColdPlains,
            [Area.ColdPlains] = Area.StonyField,
            [Area.UndergroundPassageLevel1] = Area.DarkWood,
            [Area.DarkWood] = Area.BlackMarsh,
            [Area.BlackMarsh] = Area.TamoeHighland,
            [Area.RockyWaste] = Area.DryHills,
            [Area.DryHills] = Area.FarOasis,
            [Area.FarOasis] = Area.LostCity,
            [Area.FlayerJungle] = Area.LowerKurast,
            [Area.KurastBazaar] = Area.UpperKurast,
            [Area.UpperKurast] = Area.KurastCauseway,
            [Area.KurastCauseway] = Area.Travincal,
        };

        private static readonly Dictionary<Area, Area[]> AreaPreferredQuestArea = new Dictionary<Area, Area[]>()
        {
            [Area.BloodMoor] = new[] { Area.DenOfEvil },
            [Area.ColdPlains] = new[] { Area.BurialGrounds },
            [Area.BlackMarsh] = new[] { Area.ForgottenTower },
            [Area.TamoeHighland] = new[] { Area.PitLevel1 },
            [Area.DryHills] = new[] { Area.HallsOfTheDeadLevel1 },
            [Area.FarOasis] = new[] { Area.MaggotLairLevel1 },
            [Area.LostCity] = new[] { Area.ValleyOfSnakes },
            [Area.SpiderForest] = new[] { Area.SpiderCavern },
            [Area.FlayerJungle] = new[] { Area.FlayerDungeonLevel1 },
            [Area.KurastBazaar] = new[] { Area.SewersLevel1Act3, Area.RuinedTemple },
            [Area.CrystallinePassage] = new[] { Area.FrozenRiver },
        };

        private static readonly Dictionary<Area, Dictionary<GameObject, Area>> AreaPortals = new Dictionary<Area, Dictionary<GameObject, Area>>()
        {
            [Area.FrigidHighlands] = new Dictionary<GameObject, Area>()
            {
                [GameObject.PermanentTownPortal] = Area.Abaddon,
            },
            [Area.ArreatPlateau] = new Dictionary<GameObject, Area>()
            {
                [GameObject.PermanentTownPortal] = Area.PitOfAcheron,
            },
            [Area.FrozenTundra] = new Dictionary<GameObject, Area>()
            {
                [GameObject.PermanentTownPortal] = Area.InfernalPit,
            },
        };

        private static readonly HashSet<GameObject> Shrines = new HashSet<GameObject>
        {
            GameObject.Shrine,
            GameObject.HornShrine,
            GameObject.ForestAltar,
            GameObject.DesertShrine1,
            GameObject.DesertShrine2,
            GameObject.DesertShrine3,
            GameObject.DesertShrine4,
            GameObject.DesertShrine5,
            GameObject.SteleDesertMagicShrine,
            GameObject.JungleShrine2,
            GameObject.JungleShrine3,
            GameObject.JungleShrine4,
            GameObject.JungleShrine5,
        };

        private static readonly HashSet<GameObject> Doors = new HashSet<GameObject>
        {
            GameObject.DoorCathedralLeft,
            GameObject.DoorCathedralRight,
            GameObject.DoorCourtyardLeft,
            GameObject.DoorCourtyardRight,
            GameObject.DoorGateLeft,
            GameObject.DoorGateRight,
            GameObject.DoorMonasteryDoubleRight,
            GameObject.DoorWoodenLeft,
            GameObject.DoorWoodenLeft2,
            GameObject.DoorWoodenRight,
            GameObject.IronGrateDoorLeft,
            GameObject.IronGrateDoorRight,
            GameObject.SlimeDoor1,
            GameObject.SlimeDoor2,
            GameObject.TombDoorLeft,
            GameObject.TombDoorLeft2,
            GameObject.TombDoorRight,
            GameObject.TombDoorRight2,
            GameObject.WoodenDoorLeft,
            GameObject.WoodenDoorRight,
            GameObject.WoodenGrateDoorLeft,
            GameObject.WoodenGrateDoorRight,
            GameObject.AndarielDoor,
            GameObject.PenBreakableDoor,
            GameObject.SecretDoor1
        };

        public static void UpdateLocalizationNames()
        {
            QuestObjects = new Dictionary<GameObject, string>
            {
                [GameObject.CairnStoneAlpha] = Area.Tristram.Name(),
                [GameObject.WirtCorpse] = Items.GetItemNameFromKey("leg"),
                [GameObject.InifussTree] = Items.GetItemNameFromKey("Inifuss"),
                [GameObject.Malus] = Items.GetItemNameFromKey("Malus"),
                [GameObject.HoradricScrollChest] = Items.GetItemNameFromKey("tr1"),
                [GameObject.HoradricCubeChest] = Items.GetItemNameFromKey("box"),
                [GameObject.StaffOfKingsChest] = Items.GetItemNameFromKey("Staff of Kings"),
                [GameObject.YetAnotherTome] = AreaExtensions.NameFromKey("The Summoner"),
                [GameObject.HoradricOrifice] = Items.GetItemNameFromKey("orifice"),
                [GameObject.KhalimChest1] = Items.GetItemNameFromKey("qhr"),
                [GameObject.KhalimChest2] = Items.GetItemNameFromKey("qbr"),
                [GameObject.KhalimChest3] = Items.GetItemNameFromKey("qey"),
                [GameObject.LamEsensTome] = Items.GetItemNameFromKey("bbb"),
                [GameObject.GidbinnAltarDecoy] = Items.GetItemNameFromKey("gidbinn"),
                [GameObject.HellForge] = Items.GetItemNameFromKey("Hellforge"),
                [GameObject.DrehyaWildernessStartPosition] = AreaExtensions.NameFromKey("Drehya"), //anya
                [GameObject.NihlathakWildernessStartPosition] = AreaExtensions.NameFromKey("Nihlathak"),
                [GameObject.CagedWussie] = AreaExtensions.NameFromKey("cagedwussie1"),
            };
            AreaSpecificQuestObjects = new Dictionary<Area, Dictionary<GameObject, string>>()
            {
                [Area.MatronsDen] = new Dictionary<GameObject, string>()
                {
                    [GameObject.SparklyChest] = AreaExtensions.NameFromKey("Lilith"),
                },
                [Area.FurnaceOfPain] = new Dictionary<GameObject, string>()
                {
                    [GameObject.SparklyChest] = AreaExtensions.NameFromKey("Izual"),
                },
                [Area.PalaceCellarLevel3] = new Dictionary<GameObject, string>()
                {
                    [GameObject.ArcaneSanctuaryPortal] = AreaExtensions.NameFromKey("Arcane Sanctuary"),
                },
            };
        }

        public static List<PointOfInterest> Get(MapApi mapApi, AreaData areaData, GameData gameData)
        {
            var pointsOfInterest = new List<PointOfInterest>();
            var areaRenderDecided = new List<Area>();

            if (areaData.Area == Area.UberTristram) return pointsOfInterest; // No actual points of interest here, Wirt's leg appears without this line

            if (areaData.AdjacentLevels.Any())
            {
                // Next Area Point of Interest
                switch (areaData.Area)
                {
                    case Area.CanyonOfTheMagi:
                        // Work out which tomb is the right once.
                        // Load the maps for all of the tombs, and check which one has the Orifice.
                        // Declare that tomb as point of interest.
                        Area[] tombs = new[]
                        {
                            Area.TalRashasTomb1, Area.TalRashasTomb2, Area.TalRashasTomb3, Area.TalRashasTomb4,
                            Area.TalRashasTomb5, Area.TalRashasTomb6, Area.TalRashasTomb7
                        };
                        var realTomb = tombs.FirstOrDefault(x => mapApi.GetMapData(x).Objects.ContainsKey(GameObject.HoradricOrifice));

                        if (realTomb != Area.None && areaData.AdjacentLevels[realTomb].Exits.Any())
                        {
                            pointsOfInterest.Add(new PointOfInterest
                            {
                                Area = areaData.Area,
                                NextArea = realTomb,
                                Label = realTomb.MapLabel(gameData.Difficulty),
                                Position = areaData.AdjacentLevels[realTomb].Exits[0],
                                RenderingSettings = MapAssistConfiguration.Loaded.MapConfiguration.NextArea,
                                Type = PoiType.NextArea
                            });
                            areaRenderDecided.Add(realTomb);
                        }
                        break;

                    case Area.TamoeHighland:
                        var monastery = areaData.AdjacentLevels.First(level => level.Key == Area.MonasteryGate).Value;

                        var monasteryArea = mapApi.GetMapData(Area.MonasteryGate);
                        var outerCloister = monasteryArea.AdjacentLevels.First(level => level.Key == Area.OuterCloister).Value;

                        pointsOfInterest.Add(new PointOfInterest
                        {
                            Area = areaData.Area,
                            NextArea = Area.MonasteryGate,
                            Label = Area.MonasteryGate.MapLabel(gameData.Difficulty),
                            Position = new Point(outerCloister.Exits[0].X, monastery.Exits[0].Y),
                            RenderingSettings = MapAssistConfiguration.Loaded.MapConfiguration.NextArea,
                            Type = PoiType.NextArea
                        });
                        areaRenderDecided.Add(Area.MonasteryGate);
                        break;

                    case Area.OuterCloister:
                        // Barracks Door is based on waypoint position
                        var waypoint = areaData.Objects.First(obj => obj.Key == GameObject.WaypointPortal).Value.First();
                        var poiPosition = new Point();
                        switch (waypoint.X)
                        {
                            case 15129:
                                // Waypoint = { X: 15129, Y: 4954 }
                                // SE Door = { X: 15280, Y: 4940 }
                                poiPosition = new Point(15280, 4940);
                                break;

                            case 15154:
                                // Waypoint = { X: 15154, Y: 4919 }
                                // NE Door = { X: 15141, Y: 4802 }
                                poiPosition = new Point(15141, 4802);
                                break;

                            case 15159:
                                // Waypoint = { X: 15159, Y: 4934 }
                                // NW Door = { X: 15002, Y: 4943 }
                                poiPosition = new Point(15002, 4943);
                                break;
                        }
                        pointsOfInterest.Add(new PointOfInterest
                        {
                            Area = areaData.Area,
                            NextArea = Area.Barracks,
                            Label = Area.Barracks.MapLabel(gameData.Difficulty),
                            Position = poiPosition,
                            RenderingSettings = MapAssistConfiguration.Loaded.MapConfiguration.NextArea,
                            Type = PoiType.NextArea
                        });
                        areaRenderDecided.Add(Area.OuterCloister);
                        break;

                    case Area.InnerCloister:
                        // Cathedral door
                        pointsOfInterest.Add(new PointOfInterest
                        {
                            Area = areaData.Area,
                            NextArea = Area.Cathedral,
                            Label = Area.Cathedral.MapLabel(gameData.Difficulty),
                            Position = new Point(20053, 5000),
                            RenderingSettings = MapAssistConfiguration.Loaded.MapConfiguration.NextArea,
                            Type = PoiType.NextArea
                        });
                        areaRenderDecided.Add(Area.InnerCloister);
                        break;

                    case Area.SpiderForest:
                        {
                            if (areaData.AdjacentLevels.TryGetValue(Area.FlayerJungle, out var flayerJungleLevel))
                            {
                                pointsOfInterest.Add(new PointOfInterest
                                {
                                    Area = areaData.Area,
                                    NextArea = Area.FlayerJungle,
                                    Label = Area.FlayerJungle.MapLabel(gameData.Difficulty),
                                    Position = flayerJungleLevel.Exits[0],
                                    RenderingSettings = MapAssistConfiguration.Loaded.MapConfiguration.NextArea,
                                    Type = PoiType.NextArea
                                });
                                areaRenderDecided.Add(Area.FlayerJungle);
                            }
                            else if (areaData.AdjacentLevels.TryGetValue(Area.GreatMarsh, out var greatMarshLevel))
                            {
                                pointsOfInterest.Add(new PointOfInterest
                                {
                                    Area = areaData.Area,
                                    NextArea = Area.GreatMarsh,
                                    Label = Area.GreatMarsh.MapLabel(gameData.Difficulty),
                                    Position = greatMarshLevel.Exits[0],
                                    RenderingSettings = MapAssistConfiguration.Loaded.MapConfiguration.NextArea,
                                    Type = PoiType.NextArea
                                });
                                areaRenderDecided.Add(Area.GreatMarsh);
                            }
                        }
                        break;

                    case Area.GreatMarsh:
                        {
                            if (areaData.AdjacentLevels.TryGetValue(Area.FlayerJungle, out var flayerJungleLevel))
                            {
                                pointsOfInterest.Add(new PointOfInterest
                                {
                                    Area = areaData.Area,
                                    NextArea = Area.FlayerJungle,
                                    Label = Area.FlayerJungle.MapLabel(gameData.Difficulty),
                                    Position = flayerJungleLevel.Exits[0],
                                    RenderingSettings = MapAssistConfiguration.Loaded.MapConfiguration.NextArea,
                                    Type = PoiType.NextArea
                                });
                                areaRenderDecided.Add(Area.FlayerJungle);
                            }
                        }
                        break;

                    default:
                        if (AreaPreferredNextArea.TryGetValue(areaData.Area, out var nextArea))
                        {
                            var nextLevel = areaData.AdjacentLevels[nextArea];
                            if (nextLevel.Exits.Any())
                            {
                                pointsOfInterest.Add(new PointOfInterest
                                {
                                    Area = areaData.Area,
                                    NextArea = nextArea,
                                    Label = nextArea.MapLabel(gameData.Difficulty),
                                    Position = nextLevel.Exits[0],
                                    RenderingSettings = MapAssistConfiguration.Loaded.MapConfiguration.NextArea,
                                    Type = PoiType.NextArea
                                });
                                areaRenderDecided.Add(nextArea);
                            }
                        }
                        else
                        {
                            var maxAdjacentArea = areaData.AdjacentLevels.Keys.Max();
                            if (maxAdjacentArea > areaData.Area)
                            {
                                var nextLevel = areaData.AdjacentLevels[maxAdjacentArea];
                                if (nextLevel.Exits.Any())
                                {
                                    pointsOfInterest.Add(new PointOfInterest
                                    {
                                        Area = areaData.Area,
                                        NextArea = maxAdjacentArea,
                                        Label = maxAdjacentArea.MapLabel(gameData.Difficulty),
                                        Position = nextLevel.Exits[0],
                                        RenderingSettings = MapAssistConfiguration.Loaded.MapConfiguration.NextArea,
                                        Type = PoiType.NextArea
                                    });
                                    areaRenderDecided.Add(maxAdjacentArea);
                                }
                            }
                        }
                        break;
                }

                // Quest Area Point of Interest
                if (AreaPreferredQuestArea.TryGetValue(areaData.Area, out var questAreas))
                {
                    foreach (var questArea in questAreas)
                    {
                        var questLevel = areaData.AdjacentLevels[questArea];
                        if (questLevel.Exits.Any())
                        {
                            pointsOfInterest.Add(new PointOfInterest
                            {
                                Area = areaData.Area,
                                NextArea = questArea,
                                Label = questArea.MapLabel(gameData.Difficulty),
                                Position = questLevel.Exits[0],
                                RenderingSettings = MapAssistConfiguration.Loaded.MapConfiguration.Quest,
                                Type = PoiType.Quest
                            });
                            areaRenderDecided.Add(questArea);
                        }
                    }
                }

                // Previous Area Point of Interest
                switch (areaData.Area)
                {
                    case Area.MonasteryGate:
                        var outerCloister = areaData.AdjacentLevels.First(level => level.Key == Area.OuterCloister).Value;
                        var tamoe = areaData.AdjacentLevels.First(level => level.Key == Area.TamoeHighland).Value;

                        pointsOfInterest.Add(new PointOfInterest
                        {
                            Area = areaData.Area,
                            NextArea = tamoe.Area,
                            Label = tamoe.Area.MapLabel(gameData.Difficulty),
                            Position = new Point(outerCloister.Exits[0].X, tamoe.Exits[0].Y),
                            RenderingSettings = MapAssistConfiguration.Loaded.MapConfiguration.PreviousArea,
                            Type = PoiType.PreviousArea
                        });
                        break;

                    case Area.Barracks:
                        var outerCloisterArea = mapApi.GetMapData(Area.OuterCloister);
                        var barracksAreaData = Get(mapApi, outerCloisterArea, gameData);
                        var barracks = barracksAreaData.FirstOrDefault(poi => poi.Type == PoiType.NextArea);

                        pointsOfInterest.Add(new PointOfInterest
                        {
                            Area = areaData.Area,
                            NextArea = Area.OuterCloister,
                            Label = Area.OuterCloister.MapLabel(gameData.Difficulty),
                            Position = barracks.Position,
                            RenderingSettings = MapAssistConfiguration.Loaded.MapConfiguration.PreviousArea,
                            Type = PoiType.PreviousArea
                        });
                        break;

                    case Area.Cathedral:
                        var innerCloisterArea = mapApi.GetMapData(Area.InnerCloister);
                        var cathedralAreaData = Get(mapApi, innerCloisterArea, gameData);
                        var cathedral = cathedralAreaData.FirstOrDefault(poi => poi.Type == PoiType.NextArea);

                        pointsOfInterest.Add(new PointOfInterest
                        {
                            Area = areaData.Area,
                            NextArea = Area.InnerCloister,
                            Label = Area.InnerCloister.MapLabel(gameData.Difficulty),
                            Position = cathedral.Position,
                            RenderingSettings = MapAssistConfiguration.Loaded.MapConfiguration.PreviousArea,
                            Type = PoiType.PreviousArea
                        });
                        break;

                    default:
                        foreach (var level in areaData.AdjacentLevels.Values)
                        {
                            // Already made render decision for this.
                            if (areaRenderDecided.Contains(level.Area))
                            {
                                continue;
                            }

                            foreach (var position in level.Exits)
                            {
                                pointsOfInterest.Add(new PointOfInterest
                                {
                                    Area = areaData.Area,
                                    NextArea = level.Area,
                                    Label = level.Area.MapLabel(gameData.Difficulty),
                                    Position = position,
                                    RenderingSettings = MapAssistConfiguration.Loaded.MapConfiguration.PreviousArea,
                                    Type = PoiType.PreviousArea
                                });
                            }
                        }
                        break;
                }
            }

            foreach (var objAndPoints in areaData.Objects)
            {
                GameObject obj = objAndPoints.Key;
                Point[] points = objAndPoints.Value;

                if (!points.Any())
                {
                    continue;
                }

                // Area-specific quest objects
                if (AreaSpecificQuestObjects.ContainsKey(areaData.Area))
                {
                    if (AreaSpecificQuestObjects[areaData.Area].ContainsKey(obj))
                    {
                        pointsOfInterest.Add(new PointOfInterest
                        {
                            Area = areaData.Area,
                            Label = AreaSpecificQuestObjects[areaData.Area][obj],
                            Position = points[0],
                            RenderingSettings = MapAssistConfiguration.Loaded.MapConfiguration.Quest,
                            Type = PoiType.AreaSpecificQuest
                        });
                    }
                }

                // Area-specific portals
                if (AreaPortals.ContainsKey(areaData.Area))
                {
                    if (AreaPortals[areaData.Area].ContainsKey(obj))
                    {
                        pointsOfInterest.Add(new PointOfInterest
                        {
                            Area = areaData.Area,
                            Label = AreaPortals[areaData.Area][obj].PortalLabel(gameData.Difficulty),
                            Position = points[0],
                            RenderingSettings = MapAssistConfiguration.Loaded.MapConfiguration.GamePortal,
                            Type = PoiType.AreaPortal
                        });
                    }
                }

                // Waypoints
                if (obj.IsWaypoint())
                {
                    pointsOfInterest.Add(new PointOfInterest
                    {
                        Area = areaData.Area,
                        Label = areaData.Area.Name(),
                        Position = points[0],
                        RenderingSettings = MapAssistConfiguration.Loaded.MapConfiguration.Waypoint,
                        Type = PoiType.Waypoint
                    });
                }
                // Quest objects
                else if (QuestObjects.TryGetValue(obj, out var questObjectName))
                {
                    var usePoints = obj == GameObject.CagedWussie ? points : // Mark all 3 sets of prisoners in Frigid Highlands as quest destinations
                        new Point[] { points[0] };

                    foreach (var point in usePoints)
                    {
                        pointsOfInterest.Add(new PointOfInterest
                        {
                            Area = areaData.Area,
                            Label = questObjectName,
                            Position = point,
                            RenderingSettings = MapAssistConfiguration.Loaded.MapConfiguration.Quest
                        });
                    }
                }
                // Shrines
                else if (Shrines.Contains(obj))
                {
                    foreach (var point in points)
                    {
                        pointsOfInterest.Add(new PointOfInterest
                        {
                            Area = areaData.Area,
                            Label = "",
                            Position = point,
                            RenderingSettings = MapAssistConfiguration.Loaded.MapConfiguration.Shrine,
                            Type = PoiType.Shrine
                        });
                    }
                }
                // Super Chest
                else if (Chest.SuperChests.Contains(obj))
                {
                    foreach (var point in points)
                    {
                        pointsOfInterest.Add(new PointOfInterest
                        {
                            Area = areaData.Area,
                            Label = obj.ToString(),
                            Position = point,
                            RenderingSettings = MapAssistConfiguration.Loaded.MapConfiguration.SuperChest,
                            Type = PoiType.SuperChest
                        });
                    }
                }
                else if (Doors.Contains(obj))
                {
                    foreach (var point in points)
                    {
                        pointsOfInterest.Add(new PointOfInterest
                        {
                            Area = areaData.Area,
                            Label = obj.ToString(),
                            Position = point,
                            RenderingSettings = MapAssistConfiguration.Loaded.MapConfiguration.Door,
                            Type = PoiType.Door
                        });
                    }
                }
            }

            switch (areaData.Area)
            {
                case Area.PlainsOfDespair:
                    foreach (var objAndPoints in areaData.NPCs)
                    {
                        pointsOfInterest.Add(new PointOfInterest
                        {
                            Area = areaData.Area,
                            Label = AreaExtensions.NameFromKey("Izual"),
                            Position = objAndPoints.Value[0],
                            RenderingSettings = MapAssistConfiguration.Loaded.MapConfiguration.Quest
                        });
                    }
                    break;
            }

            return pointsOfInterest.Where(poi => poi.Area == areaData.Area).ToList();
        }
    }
}
