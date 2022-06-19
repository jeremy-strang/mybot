using GameOverlay.Drawing;
using GameOverlay.Windows;
using MapAssist.Files.Font;
using MapAssist.Settings;
using MapAssist.Structs;
using MapAssist.Types;
using SharpDX;
using SharpDX.Direct2D1;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Numerics;
using System.Text;
using Color = System.Drawing.Color;
using Pen = System.Drawing.Pen;

namespace MapAssist.Helpers
{
    public class Compositor : IDisposable
    {
        private static readonly NLog.Logger _log = NLog.LogManager.GetCurrentClassLogger();
        public GameData _gameData;
        public AreaData _areaData;
        private int _frameCount = 0;
        private ExocetFont _exocetFont;
        private FormalFont _formalFont;

        private Matrix3x2 mapTransformMatrix;
        private Matrix3x2 areaTransformMatrix;
        private HashSet<(Bitmap, Point)> gamemaps = new HashSet<(Bitmap, Point)>();
        private (Color?, Color?) gamemapColors = (Color.Empty, Color.Empty);
        private Rectangle _drawBounds;
        private readonly float _rotateRadians = (float)(45 * Math.PI / 180f);
        private float scaleWidth = 1;
        private float scaleHeight = 1;
        private const int WALKABLE = 0;
        private const int BORDER = 1;

        public Compositor()
        {
            Properties.Resources.ResourceManager.IgnoreCase = true;

            _exocetFont = new ExocetFont();
            _formalFont = new FormalFont();
        }

        public void SetArea(AreaData areaData)
        {
            _areaData = areaData;
            if (_areaData == null) return;

            _areaData.CalcViewAreas(_rotateRadians);

            foreach (var adjacentArea in _areaData.AdjacentAreas.Values)
            {
                adjacentArea.CalcViewAreas(_rotateRadians);
            }

            gamemaps = new HashSet<(Bitmap, Point)>();
        }

        public void Init(Graphics gfx, GameData gameData, Rectangle drawBounds)
        {
            _gameData = gameData;
            _drawBounds = drawBounds;
            _frameCount += 1;
            (scaleWidth, scaleHeight) = GetScaleRatios();

            if (_areaData == null) return;

            var renderWidth = MapAssistConfiguration.Loaded.RenderingConfiguration.OverlayMode
                ? MapAssistConfiguration.Loaded.RenderingConfiguration.Size
                : scaleWidth * _areaData.ViewOutputRect.Width;

            switch (MapAssistConfiguration.Loaded.RenderingConfiguration.Position)
            {
                case MapPosition.TopLeft:
                    _drawBounds.Right = _drawBounds.Left + renderWidth;
                    break;

                case MapPosition.TopRight:
                    _drawBounds.Left = _drawBounds.Right - renderWidth;
                    break;
            }

            CalcTransformMatrices(gfx);

            var maybeWalkableColor = MapAssistConfiguration.Loaded.MapColorConfiguration.Walkable;
            var maybeBorderColor = MapAssistConfiguration.Loaded.MapColorConfiguration.Border;

            if (gamemapColors != (maybeWalkableColor, maybeBorderColor))
            {
                gamemaps.Clear();
                gamemapColors = (maybeWalkableColor, maybeBorderColor);
            }

            if (gamemaps.Count > 0) return;

            RenderTarget renderTarget = gfx.GetRenderTarget();

            var areasToRender = new AreaData[] { _areaData };
            if (_areaData.Area.RequiresStitching())
            {
                areasToRender = areasToRender.Concat(_areaData.AdjacentAreas.Values.Where(area => area.Area.RequiresStitching())).ToArray();
            }

            foreach (var renderArea in areasToRender)
            {
                var imageSize = new Size2((int)renderArea.ViewInputRect.Width, (int)renderArea.ViewInputRect.Height);
                var gamemap = new Bitmap(renderTarget, imageSize, new BitmapProperties(renderTarget.PixelFormat));
                var bytes = new byte[imageSize.Width * imageSize.Height * 4];

                if (maybeWalkableColor != null || maybeBorderColor != null)
                {
                    var walkableColor = maybeWalkableColor != null ? (Color)maybeWalkableColor : Color.Transparent;
                    var borderColor = maybeBorderColor != null ? (Color)maybeBorderColor : Color.Transparent;

                    for (var y = 0; y < imageSize.Height; y++)
                    {
                        var _y = y + (int)renderArea.ViewInputRect.Top;
                        for (var x = 0; x < imageSize.Width; x++)
                        {
                            var _x = x + (int)renderArea.ViewInputRect.Left;

                            var i = imageSize.Width * 4 * y + x * 4;
                            var type = renderArea.CollisionGrid[_y][_x];

                            // // Uncomment this to show a red border for debugging
                            // if (x == 0 || y == 0 || y == imageSize.Height - 1 || x == imageSize.Width - 1)
                            // {
                            //     bytes[i] = 0;
                            //     bytes[i + 1] = 0;
                            //     bytes[i + 2] = 255;
                            //     bytes[i + 3] = 255;
                            //     continue;
                            // }

                            var pixelColor = type == WALKABLE && maybeWalkableColor != null ? walkableColor :
                                type == BORDER && maybeBorderColor != null ? borderColor :
                                Color.Transparent;

                            if (pixelColor != Color.Transparent)
                            {
                                bytes[i] = pixelColor.B;
                                bytes[i + 1] = pixelColor.G;
                                bytes[i + 2] = pixelColor.R;
                                bytes[i + 3] = pixelColor.A;
                            }
                        }
                    }
                }

                gamemap.CopyFromMemory(bytes, imageSize.Width * 4);
                var origin = renderArea.Origin.Add(renderArea.ViewInputRect.Left - _areaData.ViewInputRect.Left, renderArea.ViewInputRect.Top - _areaData.ViewInputRect.Top);

                gamemaps.Add((gamemap, origin));
            }
        }

        public void DrawGamemap(Graphics gfx)
        {
            if (_gameData.Area != _areaData.Area)
            {
                throw new ApplicationException($"Asked to compose an image for a different area. Compositor area: {_areaData.Area}, Game data: {_areaData.Area}");
            }

            RenderTarget renderTarget = gfx.GetRenderTarget();

            renderTarget.Transform = Matrix3x2.Identity.ToDXMatrix(); // Needed for the draw bounds to work properly
            renderTarget.PushAxisAlignedClip(_drawBounds, AntialiasMode.Aliased);

            renderTarget.Transform = mapTransformMatrix.ToDXMatrix();

            foreach (var (gamemap, origin) in gamemaps)
            {
                DrawBitmap(gfx, gamemap, origin.Subtract(_areaData.Origin).Subtract(_areaData.MapPadding, _areaData.MapPadding), (float)MapAssistConfiguration.Loaded.RenderingConfiguration.Opacity);
            }

            renderTarget.PopAxisAlignedClip();
        }

        public void DrawOverlay(Graphics gfx)
        {
            RenderTarget renderTarget = gfx.GetRenderTarget();

            renderTarget.Transform = Matrix3x2.Identity.ToDXMatrix(); // Needed for the draw bounds to work properly
            renderTarget.PushAxisAlignedClip(_drawBounds, AntialiasMode.Aliased);

            renderTarget.Transform = areaTransformMatrix.ToDXMatrix();

            DrawExpRange(gfx);
            DrawPointsOfInterest(gfx);
            DrawMonsters(gfx);
            DrawMissiles(gfx);
            DrawItems(gfx);
            DrawPlayers(gfx);

            renderTarget.PopAxisAlignedClip();
        }

        private void DrawExpRange(Graphics gfx)
        {
            var color = MapAssistConfiguration.Loaded.MapColorConfiguration.ExpRange;

            if (color != null && !_areaData.Area.IsTown())
            {
                var distance = 60;
                var snap = 40;
                var offset = -20;

                var offsetX = offset - (_areaData.Origin.X % snap);
                var offsetY = offset - (_areaData.Origin.Y % snap);

                var brush = CreateMapBrush(gfx, (Color)color);

                var center = _gameData.PlayerUnit.Position;
                center.X = (float)Math.Round((center.X + offsetX) / snap) * snap - offsetX;
                center.Y = (float)Math.Round((center.Y + offsetY) / snap) * snap - offsetY;

                var rect = new Rectangle(center.X - distance, center.Y - distance, center.X + distance, center.Y + distance);
                gfx.DrawRectangle(brush, rect, 0.5f);
            }
        }

        private void DrawPointsOfInterest(Graphics gfx)
        {
            var drawPoiIcons = new List<(IconRendering, Point)>();
            var drawPoiLabels = new List<(PointOfInterestRendering, Point, string, Color?)>();

            var drawnPreviousNextAreas = new List<Point>();

            var areasToRender = new AreaData[] { _areaData };
            if (_areaData.Area.RequiresStitching())
            {
                areasToRender = areasToRender.Concat(_areaData.AdjacentAreas.Values.Where(area => area.Area.RequiresStitching())).ToArray();
            }

            foreach (var area in areasToRender)
            {
                if (area.PointsOfInterest == null) continue;

                foreach (var poi in area.PointsOfInterest)
                {
                    if ((new PoiType[] { PoiType.PreviousArea, PoiType.NextArea }).Contains(poi.Type))
                    {
                        if (drawnPreviousNextAreas.Exists(x => x.Subtract(poi.Position).Length() < 5))
                        {
                            continue;
                        }
                        else
                        {
                            drawnPreviousNextAreas.Add(poi.Position);
                        }
                    }

                    if (poi.PoiMatchesPortal(_gameData.Objects, _gameData.Difficulty))
                    {
                        continue;
                    }

                    if (poi.RenderingSettings.CanDrawIcon())
                    {
                        drawPoiIcons.Add((poi.RenderingSettings, poi.Position));
                    }
                }

                foreach (var poi in area.PointsOfInterest)
                {
                    if (poi.Area != _areaData.Area && (new PoiType[] { PoiType.PreviousArea, PoiType.NextArea, PoiType.Quest, PoiType.Waypoint, PoiType.AreaPortal }).Contains(poi.Type))
                    {
                        continue;
                    }

                    if (poi.RenderingSettings.CanDrawLine() && !_areaData.Area.IsTown() && !area.Area.IsTown() && poi.Area == _areaData.Area)
                    {
                        var fontSize = gfx.ScaleFontSize((float)poi.RenderingSettings.LabelFontSize);
                        var padding = poi.RenderingSettings.CanDrawLabel() ? fontSize * 1.3f / 2 : 0; // 1.3f is the line height adjustment
                        var poiPosition = MovePointInBounds(poi.Position, _gameData.PlayerPosition, padding);
                        DrawLine(gfx, poi.RenderingSettings, _gameData.PlayerPosition, poiPosition);
                    }

                    if (!string.IsNullOrWhiteSpace(poi.Label))
                    {
                        if (poi.PoiMatchesPortal(_gameData.Objects, _gameData.Difficulty))
                        {
                            continue;
                        }

                        if (poi.Type == PoiType.Shrine && !IsInBounds(poi.Position, _gameData.PlayerPosition))
                        {
                            continue;
                        }

                        if (poi.RenderingSettings.CanDrawLine() && poi.RenderingSettings.CanDrawLabel())
                        {
                            var poiPosition = MovePointInBounds(poi.Position, _gameData.PlayerPosition);
                            drawPoiLabels.Add((poi.RenderingSettings, poiPosition, poi.Label, null));
                        }
                        else if (poi.RenderingSettings.CanDrawLabel())
                        {
                            drawPoiLabels.Add((poi.RenderingSettings, poi.Position, poi.Label, null));
                        }
                    }
                }
            }

            foreach (var gameObject in _gameData.Objects)
            {
                var foundInArea = areasToRender.FirstOrDefault(area => area.IncludesPoint(gameObject.Position));
                if (foundInArea != null && foundInArea.Area != _areaData.Area && !foundInArea.Area.RequiresStitching()) continue; // Don't show gamedata objects in another area if areas aren't stitched together

                if (gameObject.IsPortal)
                {
                    var destinationArea = (Area)Enum.ToObject(typeof(Area), gameObject.ObjectData.InteractType);

                    var playerNameUnicode = Encoding.UTF8.GetString(gameObject.ObjectData.Owner).TrimEnd((char)0);
                    var playerName = !string.IsNullOrWhiteSpace(playerNameUnicode) ? playerNameUnicode : null;

                    var rosterEntry = _gameData.Roster.List.FirstOrDefault(x => x.Name == playerNameUnicode);

                    var render = rosterEntry != null && rosterEntry.UnitId == _gameData.PlayerUnit.UnitId ? MapAssistConfiguration.Loaded.MapConfiguration.MyPortal :
                        rosterEntry != null && rosterEntry.InParty ? MapAssistConfiguration.Loaded.MapConfiguration.PartyPortal :
                        rosterEntry != null ? MapAssistConfiguration.Loaded.MapConfiguration.NonPartyPortal :
                        MapAssistConfiguration.Loaded.MapConfiguration.GamePortal;

                    if (render.CanDrawIcon())
                    {
                        drawPoiIcons.Add((render, gameObject.Position));
                    }

                    if (render.CanDrawLabel(destinationArea))
                    {
                        var label = destinationArea.PortalLabel(_gameData.Difficulty, playerName);

                        if (string.IsNullOrWhiteSpace(label) || label == "None") continue;
                        drawPoiLabels.Add((render, gameObject.Position, label, null));
                    }
                }
                else if (gameObject.IsArmorWeapRack && MapAssistConfiguration.Loaded.MapConfiguration.ArmorWeapRack.CanDrawIcon())
                {
                    drawPoiIcons.Add((MapAssistConfiguration.Loaded.MapConfiguration.ArmorWeapRack, gameObject.Position));
                }
                else if (gameObject.IsChest)
                {
                    if ((gameObject.ObjectData.InteractType & (byte)Chest.InteractFlags.Trap) == (byte)Chest.InteractFlags.Trap)
                    {
                        if (MapAssistConfiguration.Loaded.MapConfiguration.TrappedChest.CanDrawIcon())
                        {
                            drawPoiIcons.Add((MapAssistConfiguration.Loaded.MapConfiguration.TrappedChest, gameObject.Position));
                        }
                    }

                    if ((gameObject.ObjectData.InteractType & (byte)Chest.InteractFlags.Locked) == (byte)Chest.InteractFlags.Locked)
                    {
                        if (MapAssistConfiguration.Loaded.MapConfiguration.LockedChest.CanDrawIcon())
                        {
                            drawPoiIcons.Add((MapAssistConfiguration.Loaded.MapConfiguration.LockedChest, gameObject.Position));
                        }
                    }
                    else
                    {
                        if (MapAssistConfiguration.Loaded.MapConfiguration.NormalChest.CanDrawIcon())
                        {
                            drawPoiIcons.Add((MapAssistConfiguration.Loaded.MapConfiguration.NormalChest, gameObject.Position));
                        }
                    }
                }
            }

            // Draw POI icons (not listed in poiRenderingOrder)
            foreach ((var rendering, var position) in drawPoiIcons)
            {
                DrawIcon(gfx, rendering, position);
            }

            // Draw POI labels (not listed in poiRenderingOrder)
            foreach ((var rendering, var position, var text, Color? color) in drawPoiLabels)
            {
                DrawIconText(gfx, rendering, position, text, color);
            }
        }

        private void DrawMissiles(Graphics gfx)
        {
            foreach (var missile in _gameData.Missiles)
            {
                if (MissileTypes._MissileTypes.TryGetValue(missile.TxtFileNo, out var missileType))
                {
                    var missileRenderingConfig = new IconRendering[]
                    {
                        MapAssistConfiguration.Loaded.MapConfiguration.MissilePhysicalLarge,
                        MapAssistConfiguration.Loaded.MapConfiguration.MissilePhysicalSmall,
                        MapAssistConfiguration.Loaded.MapConfiguration.MissileFireLarge,
                        MapAssistConfiguration.Loaded.MapConfiguration.MissileFireSmall,
                        MapAssistConfiguration.Loaded.MapConfiguration.MissileIceLarge,
                        MapAssistConfiguration.Loaded.MapConfiguration.MissileIceSmall,
                        MapAssistConfiguration.Loaded.MapConfiguration.MissileLightLarge,
                        MapAssistConfiguration.Loaded.MapConfiguration.MissileLightSmall,
                        MapAssistConfiguration.Loaded.MapConfiguration.MissilePoisonLarge,
                        MapAssistConfiguration.Loaded.MapConfiguration.MissilePoisonSmall,
                        MapAssistConfiguration.Loaded.MapConfiguration.MissileMagicLarge,
                        MapAssistConfiguration.Loaded.MapConfiguration.MissileMagicSmall,
                    };
                    var render = (IconRendering)missileRenderingConfig[(int)missileType].Clone();
                    if (render.CanDrawIcon())
                    {
                        render.IconSize = render.IconSize / 5;  // scale down by factor 5
                        DrawIcon(gfx, render, missile.Position);
                    }
                }
            }
        }

        private void DrawMonsters(Graphics gfx)
        {
            var drawMonsterIcons = new List<(IconRendering, UnitMonster)>();
            var drawMonsterLabels = new List<(PointOfInterestRendering, Point, string, Color?)>();

            RenderTarget renderTarget = gfx.GetRenderTarget();

            foreach (var monster in _gameData.Monsters)
            {
                var mobRender = GetMonsterIconRendering(monster);

                if (NpcExtensions.IsTownsfolk(monster.Npc))
                {
                    var npcRender = MapAssistConfiguration.Loaded.MapConfiguration.Npc;
                    if (npcRender.CanDrawIcon())
                    {
                        drawMonsterIcons.Add((npcRender, monster));
                        if (npcRender.CanDrawLabel())
                        {
                            drawMonsterLabels.Add((npcRender, monster.Position, NpcExtensions.Name(monster.Npc), npcRender.LabelColor));
                        }
                    }
                }
                else if (mobRender.CanDrawIcon())
                {
                    drawMonsterIcons.Add((mobRender, monster));
                }
            }

            // All Monster icons must be listed here for rendering
            var monsterRenderingOrder = new IconRendering[]
            {
                MapAssistConfiguration.Loaded.MapConfiguration.Npc,
                MapAssistConfiguration.Loaded.MapConfiguration.NormalMonster,
                MapAssistConfiguration.Loaded.MapConfiguration.MinionMonster,
                MapAssistConfiguration.Loaded.MapConfiguration.ChampionMonster,
                MapAssistConfiguration.Loaded.MapConfiguration.UniqueMonster,
                MapAssistConfiguration.Loaded.MapConfiguration.SuperUniqueMonster,
            };

            foreach ((var rendering, var monster) in drawMonsterIcons.OrderBy(x => Array.IndexOf(monsterRenderingOrder, x.Item1)))
            {
                var monsterPosition = monster.Position;

                DrawIcon(gfx, rendering, monsterPosition);

                // Draw Monster Immunities on top of monster icon
                var iCount = monster.Immunities.Count;
                if (iCount > 0)
                {
                    monsterPosition = Vector2.Transform(monsterPosition.ToVector(), areaTransformMatrix).ToPoint();

                    var currentTransform = renderTarget.Transform;
                    renderTarget.Transform = Matrix3x2.Identity.ToDXMatrix();

                    var iconShape = GetIconShape(rendering).ToRectangle();

                    var ellipseSize = Math.Max(iconShape.Height / 12, 3 / scaleWidth); // Arbirarily set to be a fraction of the the mob icon size. The important point is that it scales with the mob icon consistently.
                    var dx = ellipseSize * scaleWidth * 1.5f; // Amount of space each indicator will take up, including spacing

                    var iX = -dx * (iCount - 1) / 2f; // Moves the first indicator sufficiently left so that the whole group of indicators will be centered.

                    foreach (var immunity in monster.Immunities)
                    {
                        var render = new IconRendering()
                        {
                            IconShape = Shape.Ellipse,
                            IconColor = ResistColors.ResistColor[immunity],
                            IconSize = ellipseSize
                        };

                        var iPoint = monsterPosition.Add(new Point(iX, -iconShape.Height - render.IconSize));
                        DrawIcon(gfx, render, iPoint, equalScaling: true);
                        iX += dx;
                    }

                    renderTarget.Transform = currentTransform;
                }
            }

            foreach ((var rendering, var position, var text, Color? color) in drawMonsterLabels.OrderBy(x => Array.IndexOf(monsterRenderingOrder, x.Item1)))
            {
                DrawIconText(gfx, rendering, position, text, color);
            }
        }

        private void DrawItems(Graphics gfx)
        {
            var drawItemIcons = new List<(IconRendering, Point)>();
            var drawItemLabels = new List<(PointOfInterestRendering, Point, string, Color?)>();

            if (MapAssistConfiguration.Loaded.ItemLog.Enabled)
            {
                foreach (var item in _gameData.Items)
                {
                    if (item.IsValidItem && item.IsDropped && !item.IsIdentified)
                    {
                        if (!_areaData.IncludesPoint(item.Position) && !IsInBounds(item.Position, _gameData.PlayerPosition)) continue; // Don't show item if not in drawn areas

                        var itemPosition = item.Position;
                        var render = MapAssistConfiguration.Loaded.MapConfiguration.Item;

                        drawItemIcons.Add((render, itemPosition));
                        drawItemLabels.Add((render, item.Position, item.ItemBaseName, item.ItemBaseColor));
                    }
                }
            }

            foreach ((var rendering, var position) in drawItemIcons)
            {
                DrawIcon(gfx, rendering, position);
            }

            foreach ((var rendering, var position, var text, Color? color) in drawItemLabels)
            {
                DrawIconText(gfx, rendering, position, text, color);
            }
        }

        private void DrawPlayers(Graphics gfx)
        {
            var drawPlayerIcons = new List<(IconRendering, Point)>();
            var drawPlayerLabels = new List<(PointOfInterestRendering, Point, string, Color?)>();

            var areasToRender = new AreaData[] { _areaData };
            if (_areaData.Area.RequiresStitching())
            {
                areasToRender = areasToRender.Concat(_areaData.AdjacentAreas.Values.Where(area => area.Area.RequiresStitching())).ToArray();
            }

            foreach (var pet in _gameData.Summons.ToArray())
            {
                var rendering = MapAssistConfiguration.Loaded.MapConfiguration.MySummons;
                if (!pet.IsPlayerOwned) rendering = MapAssistConfiguration.Loaded.MapConfiguration.OtherSummons;

                if (rendering.CanDrawIcon())
                {
                    drawPlayerIcons.Add((rendering, pet.Position));
                }
            }

            foreach (var merc in _gameData.Mercs.ToArray())
            {
                if (merc.IsCorpse) continue;

                var rendering = MapAssistConfiguration.Loaded.MapConfiguration.MyMerc;
                if (!merc.IsPlayerOwned) rendering = MapAssistConfiguration.Loaded.MapConfiguration.OtherMercs;

                if (rendering.CanDrawIcon())
                {
                    drawPlayerIcons.Add((rendering, merc.Position));
                }
            }

            foreach (var corpse in _gameData.Corpses)
            {
                var rendering = MapAssistConfiguration.Loaded.MapConfiguration.Corpse;
                var fontSize = gfx.ScaleFontSize((float)rendering.LabelFontSize);
                var canDrawLabel = rendering.CanDrawLabel();
                var canDrawIcon = rendering.CanDrawIcon();
                var canDrawLine = rendering.CanDrawLine();

                if (corpse.Act.ActId != _gameData.PlayerUnit.Act.ActId) continue; // Don't show corpse if not in the same act
                if (!areasToRender.Any(area => area.Area == corpse.Area)) continue; // Don't show corpse if not in drawn areas

                if (canDrawIcon)
                {
                    drawPlayerIcons.Add((rendering, corpse.Position));
                }

                if (canDrawLabel)
                {
                    var poiPosition = MovePointInBounds(corpse.Position, _gameData.PlayerPosition);
                    drawPlayerLabels.Add((rendering, poiPosition, corpse.Name + " (Corpse)", null)); //fix label when language is merged in
                }

                if (canDrawLine && corpse.Name == _gameData.PlayerUnit.Name)
                {
                    var padding = canDrawLabel ? fontSize * 1.3f / 2 : 0; // 1.3f is the line height adjustment
                    var poiPosition = MovePointInBounds(corpse.Position, _gameData.PlayerPosition, padding);
                    DrawLine(gfx, rendering, _gameData.PlayerPosition, poiPosition);
                }
            }

            if (_gameData.Roster.EntriesByUnitId.TryGetValue(_gameData.PlayerUnit.UnitId, out var myPlayerEntry))
            {
                foreach (var player in _gameData.Roster.List)
                {
                    var myPlayer = player.UnitId == myPlayerEntry.UnitId;
                    var inMyParty = player.PartyID != ushort.MaxValue && player.PartyID == myPlayerEntry.PartyID;
                    var playerName = player.Name;

                    var canDrawIcon = MapAssistConfiguration.Loaded.MapConfiguration.Player.CanDrawIcon();
                    var canDrawLabel = MapAssistConfiguration.Loaded.MapConfiguration.Player.CanDrawLabel();

                    if (_gameData.Players.TryGetValue(player.UnitId, out var playerUnit))
                    {
                        if (!myPlayer && playerUnit.Act.ActId != _gameData.PlayerUnit.Act.ActId) continue; // Don't show player if not in the same act
                        if (!myPlayer && !areasToRender.Any(area => area.IncludesPoint(playerUnit.Position))) continue; // Don't show player if not in drawn areas

                        // use data from the unit table if available
                        if (playerUnit.RosterEntry.InParty)
                        {
                            var rendering = myPlayer
                                ? MapAssistConfiguration.Loaded.MapConfiguration.Player
                                : MapAssistConfiguration.Loaded.MapConfiguration.PartyPlayer;

                            var canDrawThisIcon = myPlayer
                                ? canDrawIcon
                                : MapAssistConfiguration.Loaded.MapConfiguration.PartyPlayer.CanDrawIcon();

                            if (canDrawThisIcon)
                            {
                                drawPlayerIcons.Add((rendering, playerUnit.Position));
                            }

                            var canDrawThisLabel = myPlayer
                                ? canDrawLabel
                                : MapAssistConfiguration.Loaded.MapConfiguration.PartyPlayer.CanDrawLabel();

                            if (canDrawThisLabel && !myPlayer)
                            {
                                drawPlayerLabels.Add((rendering, playerUnit.Position, playerName, rendering.LabelColor));
                            }
                        }
                        else
                        {
                            // not in my party
                            var rendering = (myPlayer
                                ? MapAssistConfiguration.Loaded.MapConfiguration.Player
                                : (!playerUnit.IsCorpse && (playerUnit.RosterEntry.IsHostile || playerUnit.RosterEntry.IsHostileTo)
                                    ? MapAssistConfiguration.Loaded.MapConfiguration.HostilePlayer
                                    : MapAssistConfiguration.Loaded.MapConfiguration.NonPartyPlayer));

                            if (rendering.CanDrawIcon())
                            {
                                drawPlayerIcons.Add((rendering, playerUnit.Position));
                            }

                            if (rendering.CanDrawLine() && !_areaData.Area.IsTown() && !playerUnit.Area.IsTown())
                            {
                                var fontSize = gfx.ScaleFontSize((float)MapAssistConfiguration.Loaded.MapConfiguration.HostilePlayer.LabelFontSize);
                                var padding = rendering.CanDrawLabel() ? fontSize * 1.3f / 2 : 0; // 1.3f is the line height adjustment
                                var poiPosition = MovePointInBounds(playerUnit.Position, _gameData.PlayerPosition, padding);
                                DrawLine(gfx, MapAssistConfiguration.Loaded.MapConfiguration.HostilePlayer, _gameData.PlayerPosition, poiPosition);
                            }

                            if (rendering.CanDrawLabel() && !myPlayer)
                            {
                                drawPlayerLabels.Add((rendering, playerUnit.Position, playerName, rendering.LabelColor));
                            }
                        }
                    }
                    else
                    {
                        if (!myPlayer && !areasToRender.Select(area => area.Area).Contains(player.Area)) continue; // Don't show player if not in drawn areas

                        // otherwise use the data from the roster
                        // only draw if in the same party, otherwise position/area data will not be up to date
                        if (inMyParty && player.PartyID < ushort.MaxValue)
                        {
                            var rendering = MapAssistConfiguration.Loaded.MapConfiguration.PartyPlayer;
                            if (canDrawIcon)
                            {
                                drawPlayerIcons.Add((rendering, player.Position));
                            }

                            if (canDrawLabel && !myPlayer)
                            {
                                drawPlayerLabels.Add((rendering, player.Position, playerName, rendering.LabelColor));
                            }
                        }
                    }
                }
            }

            // All Player icons must be listed here for rendering
            var playersRenderingOrder = new IconRendering[]
            {
                MapAssistConfiguration.Loaded.MapConfiguration.Corpse,
                MapAssistConfiguration.Loaded.MapConfiguration.OtherMercs,
                MapAssistConfiguration.Loaded.MapConfiguration.MyMerc,
                MapAssistConfiguration.Loaded.MapConfiguration.NonPartyPlayer,
                MapAssistConfiguration.Loaded.MapConfiguration.PartyPlayer,
                MapAssistConfiguration.Loaded.MapConfiguration.Player,
                MapAssistConfiguration.Loaded.MapConfiguration.HostilePlayer,
            };

            foreach ((var rendering, var position) in drawPlayerIcons.OrderBy(x => Array.IndexOf(playersRenderingOrder, x.Item1)))
            {
                DrawIcon(gfx, rendering, position);
            }

            foreach ((var rendering, var position, var text, Color? color) in drawPlayerLabels.OrderBy(x => Array.IndexOf(playersRenderingOrder, x.Item1)))
            {
                DrawIconText(gfx, rendering, position, text, color);
            }
        }

        public void DrawBuffs(Graphics gfx, Point mouseRelativePos)
        {
            RenderTarget renderTarget = gfx.GetRenderTarget();
            renderTarget.Transform = Matrix3x2.Identity.ToDXMatrix();

            var buffImageScale = (float)MapAssistConfiguration.Loaded.RenderingConfiguration.BuffSize * 59 / 132 * gfx.Height / 1080;

            var stateList = _gameData.PlayerUnit.StateList;
            var imgDimensions = 132f * buffImageScale;

            var buffAlignment = MapAssistConfiguration.Loaded.RenderingConfiguration.BuffPosition;
            var buffYPos = 0f;

            var playerBuffPosition = (gfx.Height / 2f) - imgDimensions - (gfx.Height * .15f);

            switch (buffAlignment)
            {
                case BuffPosition.Player:
                    buffYPos = playerBuffPosition;
                    break;

                case BuffPosition.Top:
                    buffYPos = gfx.Height * .12f;
                    break;

                case BuffPosition.Bottom:
                    if (_gameData.MenuOpen.SkillSelect)
                    {
                        return;
                    }

                    buffYPos = gfx.Height * .78f;
                    break;
            }

            var buffsByColor = new Dictionary<Color, List<Bitmap>>();
            var totalBuffs = 0;

            if (MapAssistConfiguration.Loaded.RenderingConfiguration.ShowBuffBarBuffs) buffsByColor.Add(States.BuffColor, new List<Bitmap>());
            if (MapAssistConfiguration.Loaded.RenderingConfiguration.ShowBuffBarAuras) buffsByColor.Add(States.AuraColor, new List<Bitmap>());
            if (MapAssistConfiguration.Loaded.RenderingConfiguration.ShowBuffBarPassives) buffsByColor.Add(States.PassiveColor, new List<Bitmap>());
            if (MapAssistConfiguration.Loaded.RenderingConfiguration.ShowBuffBarDebuffs) buffsByColor.Add(States.DebuffColor, new List<Bitmap>());

            var alertLoweredRes = false;

            foreach (var state in stateList)
            {
                var resImg = Properties.Resources.ResourceManager.GetObject(state.ToString());

                if (resImg != null)
                {
                    Color buffColor = States.StateColor(state);
                    if (state == State.Conviction && _gameData.PlayerUnit.Skills.RightSkillId != Skill.Conviction && !_gameData.PlayerUnit.IsActiveInfinity)
                    {
                        buffColor = States.DebuffColor;
                    }

                    if (buffsByColor.ContainsKey(buffColor))
                    {
                        var bmp = CreateResourceBitmap(gfx, state.ToString());
                        bmp.Tag = state.ToString().ToProperCase();
                        buffsByColor[buffColor].Add(bmp);
                        totalBuffs++;
                    }

                    var loweredRes = (state == State.Conviction && buffColor == States.DebuffColor)
                         || state == State.Convicted
                         || state == State.LowerResist;

                    if (MapAssistConfiguration.Loaded.RenderingConfiguration.BuffAlertLowRes && loweredRes)
                    {
                        alertLoweredRes = true;
                    }
                }
            }

            if (buffAlignment == BuffPosition.Bottom && _gameData.MenuOpen.PotionBelt)
            {
                var potionTopLeft = new Point(
                    0.5f * gfx.Width + 0.113f * gfx.Height + 1.17f,
                    0.785f * gfx.Height - 4
                );

                var buffsBottomRight = new Point(
                    gfx.Width / 2f + totalBuffs * imgDimensions / 2f,
                    buffYPos + imgDimensions
                );

                if (potionTopLeft.X < buffsBottomRight.X && potionTopLeft.Y < buffsBottomRight.Y)
                {
                    return;
                }
            }

            if (buffImageScale > 0)
            {
                var buffIndex = 0;
                foreach (var buff in buffsByColor)
                {
                    for (var i = 0; i < buff.Value.Count; i++)
                    {
                        var buffImg = buff.Value[i];
                        var buffColor = buff.Key;
                        var drawPoint = new Point((gfx.Width / 2f) - (totalBuffs * imgDimensions / 2f) + (buffIndex * imgDimensions), buffYPos);
                        DrawBitmap(gfx, buffImg, drawPoint, 1, size: buffImageScale);
                        var size = new Point(imgDimensions + buffImageScale, imgDimensions + buffImageScale);
                        var rect = new Rectangle(drawPoint.X, drawPoint.Y, drawPoint.X + size.X, drawPoint.Y + size.Y);

                        if (rect.IncludesPoint(mouseRelativePos))
                        {
                            var fontFamily = MapAssistConfiguration.Loaded.ItemLog.LabelFont;
                            var fontSize = (float)MapAssistConfiguration.Loaded.ItemLog.LabelFontSize;

                            DrawText(gfx, new Point(drawPoint.X + size.X / 2, drawPoint.Y - 15), (string)buffImg.Tag, fontFamily, fontSize, Color.White, true, TextAlign.Center, 0.8f);
                        }

                        var pen = new Pen(buffColor, buffImageScale);
                        if (buffColor == States.DebuffColor)
                        {
                            var debuffColor = States.DebuffColor;
                            debuffColor = Color.FromArgb(100, debuffColor.R, debuffColor.G, debuffColor.B);
                            var brush = CreateBrush(gfx, debuffColor);

                            gfx.FillRectangle(brush, rect);
                            gfx.DrawRectangle(brush, rect, 1);
                        }
                        else
                        {
                            var brush = CreateBrush(gfx, buffColor);
                            gfx.DrawRectangle(brush, rect, 1);
                        }

                        buffIndex++;
                    }
                }
            }

            if (MapAssistConfiguration.Loaded.RenderingConfiguration.ShowResistances || alertLoweredRes)
            {
                var fontFamily = MapAssistConfiguration.Loaded.GameInfo.LabelFont;
                var alertFontSize = gfx.ScaleFontSize(40);
                var playerResPosition = gfx.Height / 2f - gfx.Height * .20f;

                if (alertLoweredRes && (_frameCount / 20) % 2 == 0)
                {
                    DrawText(gfx, new Point(gfx.Width / 2, playerResPosition), "⚠️", fontFamily, alertFontSize, Color.Red, true, TextAlign.Center, 0.8f);
                }

                foreach (var (i, immunity, value) in _gameData.PlayerUnit.GetResists(_gameData.Difficulty).Select((x, i) => (i, x.Key, x.Value)))
                {
                    var immunityFontSize = gfx.ScaleFontSize(14);
                    var distBetween = immunityFontSize * 2.0f;

                    DrawText(gfx, new Point(gfx.Width / 2 + (i - 1.5f) * distBetween, playerResPosition + alertFontSize), value.ToString(), fontFamily, immunityFontSize, ResistColors.ResistColor[immunity], true, TextAlign.Center, 0.8f);
                }
            }
        }

        public void DrawMonsterBar(Graphics gfx)
        {
            if (!MapAssistConfiguration.Loaded.RenderingConfiguration.MonsterHealthBar) return;

            var areasToRender = new AreaData[] { _areaData };
            if (_areaData.Area.RequiresStitching())
            {
                areasToRender = areasToRender.Concat(_areaData.AdjacentAreas.Values.Where(area => area.Area.RequiresStitching())).ToArray();
            }

            (UnitMonster, string)[] getActiveMonsters()
            {
                var areaMonsters = _gameData.Monsters.Where(x => areasToRender.Any(y => y.IncludesPoint(x.Position))).ToArray();
                var hoveredUnit = _gameData.Monsters.Where(x => x.IsHovered).ToArray();

                var bosses = areaMonsters.Where(x => NPC.Bosses.Contains(x.Npc) && (x.IsHovered || hoveredUnit.Count() == 0)).Select(x => (x, NpcExtensions.Name(x.Npc))).ToArray();
                if (bosses.Count() > 0) return bosses;

                var superUniques = areaMonsters.Where(x => x.IsSuperUnique && (x.IsHovered || hoveredUnit.Count() == 0)).Select(x => (x, NpcExtensions.LocalizedName(x.SuperUniqueName))).ToArray();
                if (superUniques.Count() > 0) return superUniques;

                return new (UnitMonster, string)[] { };
            };

            var activeMonsters = getActiveMonsters();
            if (activeMonsters.Length == 0) return;

            foreach (var (i, (activeMonster, name)) in activeMonsters.Select((value, i) => (i, value)))
            {
                // Health
                var healthPerc = activeMonster.HealthPercentage;
                var infoText = $"{name} HP: {healthPerc:P}";

                var barWidth = gfx.Width * 0.3f;
                var barHeight = gfx.Height * 0.04f;
                var font = MapAssistConfiguration.Loaded.GameInfo.LabelFont;

                var fontSize = barHeight / 2f;
                var blackBrush = CreateBrush(gfx, Color.Black);
                var darkFillBrush = CreateBrush(gfx, Color.FromArgb(66, 0, 125));
                var lightFillBrush = CreateBrush(gfx, Color.FromArgb(100, 93, 107));

                var center = new Point(gfx.Width / 2, gfx.Height * (0.043f + i * 0.05f));
                var barRect = new Rectangle(center.X - barWidth / 2, center.Y - barHeight / 2, center.X + barWidth / 2, center.Y + barHeight / 2);
                var fillRect = new Rectangle(center.X - barWidth / 2, center.Y - barHeight / 2, center.X - barWidth / 2 + barWidth * healthPerc, center.Y + barHeight / 2);

                gfx.FillRectangle(lightFillBrush, barRect);
                gfx.FillRectangle(darkFillBrush, fillRect);
                gfx.DrawRectangle(blackBrush, barRect, 2);

                var infoTextPosition = center.Add(0, gfx.Height * (activeMonster.Immunities.Count() > 0 ? -0.007f : 0));

                DrawText(gfx, infoTextPosition, infoText, font, fontSize, Color.FromArgb(190, 171, 113), false, TextAlign.Center);

                // Immunities
                var immunityFontSize = gfx.ScaleFontSize(14);
                var immunitiesDistanceBetween = gfx.ScaleFontSize(10);
                var immunitiesWidth = activeMonster.Immunities.Select(x => gfx.MeasureString(CreateFont(gfx, font, immunityFontSize), x.ToString()).X).ToArray();
                var immunitiesTotalWidth = immunitiesWidth.Sum() + immunitiesDistanceBetween * (activeMonster.Immunities.Count() - 1);

                foreach (var (j, immunity) in activeMonster.Immunities.Select((x, j) => (j, x)))
                {
                    DrawText(gfx, new Point(gfx.Width / 2 - immunitiesTotalWidth / 2 + immunitiesWidth.Take(j).Sum() + immunitiesWidth[j] / 2 + j * immunitiesDistanceBetween, center.Y + gfx.Height * 0.01f), immunity.ToString(), font, immunityFontSize, ResistColors.ResistColor[immunity], true, TextAlign.Center, 0.8f);
                }
            }
        }

        public Point DrawGameInfo(Graphics gfx, Point anchor,
                    DrawGraphicsEventArgs e, bool errorLoadingAreaData)
        {
            var isTopLeft = MapAssistConfiguration.Loaded.GameInfo.Position == GameInfoPosition.TopLeft;
            if (isTopLeft ? _gameData.MenuOpen.IsLeftMenuOpen() : _gameData.MenuOpen.IsRightMenuOpen())
            {
                return anchor;
            }

            RenderTarget renderTarget = gfx.GetRenderTarget();
            renderTarget.Transform = Matrix3x2.Identity.ToDXMatrix();

            // Setup
            var font = MapAssistConfiguration.Loaded.GameInfo.LabelFont;
            var fontSize = gfx.ScaleFontSize((float)MapAssistConfiguration.Loaded.GameInfo.LabelFontSize);
            var lineHeight = gfx.LineHeight(fontSize);
            var textShadow = MapAssistConfiguration.Loaded.GameInfo.LabelTextShadow;
            var textAlign = MapAssistConfiguration.Loaded.GameInfo.Position == GameInfoPosition.TopRight ? TextAlign.Right : TextAlign.Left;
            var textColor = Color.FromArgb(199, 179, 119);

            // Game Name
            if (MapAssistConfiguration.Loaded.GameInfo.ShowGameName && _gameData.Session.GameName.Length > 0)
            {
                var gameNameText = "Game: " + _gameData.Session.GameName;
                DrawText(gfx, anchor, gameNameText, font, fontSize, textColor, true, textAlign);
                anchor.Y += lineHeight;

                if (_gameData.Session.GamePass.Length > 0)
                {
                    var gamePassText = "Password: " + _gameData.Session.GamePass;
                    DrawText(gfx, anchor, gamePassText, font, fontSize, textColor, true, textAlign);
                    anchor.Y += lineHeight;
                }
            }

            // Game Timer
            if (MapAssistConfiguration.Loaded.GameInfo.ShowGameTimer)
            {
                var gameElapsed = "Game Time: " + _gameData.Session.GameTimerDisplay;
                DrawText(gfx, anchor, gameElapsed, font, fontSize, textColor, textShadow, textAlign);
                anchor.Y += lineHeight;
            }

            // Area
            if (MapAssistConfiguration.Loaded.GameInfo.ShowArea)
            {
                var areaText = _gameData.Area.Name();
                DrawText(gfx, anchor, areaText, font, fontSize, textColor, textShadow, textAlign);
                anchor.Y += lineHeight;
            }

            // Difficulty
            if (MapAssistConfiguration.Loaded.GameInfo.ShowDifficulty)
            {
                var difficultyText = "Difficulty: " + _gameData.Difficulty.ToString();
                DrawText(gfx, anchor, difficultyText, font, fontSize, textColor, textShadow, textAlign);
                anchor.Y += lineHeight;
            }

            // Area Level
            if (MapAssistConfiguration.Loaded.GameInfo.ShowAreaLevel)
            {
                var areaLevel = _gameData.Area.Level(_gameData.Difficulty);
                if (areaLevel > 0)
                {
                    var areaLevelText = "Area Level: " + areaLevel;
                    DrawText(gfx, anchor, areaLevelText, font, fontSize, textColor, textShadow, textAlign);
                    anchor.Y += lineHeight;
                }
            }

            // Area Timer
            if (MapAssistConfiguration.Loaded.GameInfo.ShowAreaTimer)
            {
                var areaElapsed = "Area Time: " + _gameData.Session.AreaTimerDisplay;
                DrawText(gfx, anchor, areaElapsed, font, fontSize, textColor, textShadow, textAlign);
                anchor.Y += lineHeight;
            }

            // Overlay FPS
            if (MapAssistConfiguration.Loaded.GameInfo.ShowOverlayFPS)
            {
                var fpsText = "FPS: " + gfx.FPS.ToString() + " / DeltaTime: " + e.DeltaTime.ToString();
                DrawText(gfx, anchor, fpsText, font, fontSize, textColor, textShadow, textAlign);
                anchor.Y += lineHeight;
            }

            if (!_gameData.MapSeedReady)
            {
                DrawText(gfx, anchor, "Finding map seed...", font, fontSize * 1.3f, Color.Orange, textShadow, textAlign);
                anchor.Y += lineHeight;
            }
            else if (errorLoadingAreaData)
            {
                DrawText(gfx, anchor, "ERROR LOADING AREA!", font, fontSize * 1.5f, Color.Orange, textShadow, textAlign);
                anchor.Y += lineHeight;
            }

            return anchor;
        }

        public void DrawItemLog(Graphics gfx, Point anchor)
        {
            var isTopLeft = MapAssistConfiguration.Loaded.ItemLog.Position == GameInfoPosition.TopLeft;
            if (isTopLeft ? _gameData.MenuOpen.IsLeftMenuOpen() : _gameData.MenuOpen.IsRightMenuOpen())
            {
                return;
            }

            // Setup
            var fontSize = gfx.ScaleFontSize((float)MapAssistConfiguration.Loaded.ItemLog.LabelFontSize);
            var font = CreateFont(gfx, MapAssistConfiguration.Loaded.ItemLog.LabelFont, fontSize);
            var lineHeight = gfx.LineHeight(fontSize);
            var textShadow = MapAssistConfiguration.Loaded.ItemLog.LabelTextShadow;
            var shadowBrush = CreateBrush(gfx, Color.Black, 0.6f);
            var shadowOffset = fontSize * 0.0625f; // 1/16th

            // Item Log
            var itemsToShow = _gameData.ItemLog.Where(item => item != null && !item.ItemLogExpired && item.UnitItem.ItemBaseColor != Color.Empty).ToArray();
            for (var i = 0; i < itemsToShow.Length; i++)
            {
                var item = itemsToShow[i];
                var itemText = item.Text;
                var position = anchor.Add(0, i * lineHeight);
                var brush = CreateBrush(gfx, item.UnitItem.ItemBaseColor);
                var stringSize = gfx.MeasureString(font, itemText);

                if (MapAssistConfiguration.Loaded.ItemLog.Position == GameInfoPosition.TopRight)
                {
                    position = position.Subtract(stringSize.X, 0);
                }
                else if (MapAssistConfiguration.Loaded.ItemLog.ShowDirectionToItem)
                {
                    position = position.Add(stringSize.Y, 0);
                }

                if (MapAssistConfiguration.Loaded.ItemLog.ShowDistanceToItem && item.Area == _gameData.Area && !item.UnitItem.IsInStore)
                {
                    var smallFont = CreateFont(gfx, MapAssistConfiguration.Loaded.ItemLog.LabelFont, fontSize * 0.7f);
                    var rangePosition = position.Add(stringSize.X + 8, fontSize * 0.2f);

                    var rangeText = item.UnitItem.IsDropped
                        ? $"(range: {Math.Round(_gameData.PlayerPosition.DistanceTo(item.UnitItem.Position))})"
                        : "(picked up)";

                    if (MapAssistConfiguration.Loaded.ItemLog.Position == GameInfoPosition.TopRight)
                    {
                        var rangeTextSize = gfx.MeasureString(smallFont, rangeText);
                        position = position.Subtract(rangeTextSize.X, 0);
                        rangePosition = rangePosition.Subtract(rangeTextSize.X, 0);
                    }

                    if (textShadow)
                    {
                        gfx.DrawText(smallFont, shadowBrush, rangePosition.X + shadowOffset, rangePosition.Y + shadowOffset, rangeText);
                    }
                    gfx.DrawText(smallFont, brush, rangePosition, rangeText);
                }

                if (textShadow)
                {
                    gfx.DrawText(font, shadowBrush, position.X + shadowOffset, position.Y + shadowOffset, itemText);
                }
                gfx.DrawText(font, brush, position, itemText);

                if (MapAssistConfiguration.Loaded.ItemLog.ShowDirectionToItem && item.Area == _gameData.Area && item.UnitItem.IsDropped)
                {
                    var startPosition = Vector2.Transform(_gameData.PlayerPosition.ToVector(), areaTransformMatrix).ToPoint();
                    var endPosition = Vector2.Transform(item.UnitItem.Position.ToVector(), areaTransformMatrix).ToPoint();

                    var angle = endPosition.Subtract(startPosition).Angle();

                    var arrowcenter = position.Add(-stringSize.Y / 2 - 5, stringSize.Y / 2);
                    var arrowStartPosition = arrowcenter.Add(stringSize.Y / 2, 0).Rotate(angle + (float)Math.PI, arrowcenter);
                    var arrowEndPosition = arrowcenter.Add(stringSize.Y / 2, 0).Rotate(angle, arrowcenter);

                    var rendering = new PointOfInterestRendering()
                    {
                        LineColor = item.UnitItem.ItemBaseColor,
                        LineThickness = 2,
                        ArrowHeadSize = 8
                    };

                    DrawLine(gfx, rendering, arrowStartPosition, arrowEndPosition, transformForMap: false, renderIfShort: true, spacing: 0);
                }
            }
        }

        public void DrawPlayerInfo(Graphics gfx)
        {
            if (_gameData.MenuOpen.EscMenu) return;

            var centerX = gfx.Width / 2 + 2;
            var fontFamily = MapAssistConfiguration.Loaded.GameInfo.LabelFont;

            // Player life & mana
            var lmOffsetX = gfx.Height * .453f;
            var lmY = gfx.Height * .91f;

            var fontSize = gfx.ScaleFontSize(20);

            var life = _gameData.PlayerUnit.Life;
            var maxLife = _gameData.PlayerUnit.MaxLife;
            var lifePerc = _gameData.PlayerUnit.LifePercentage;

            var lifeText = new string[]
            {
                MapAssistConfiguration.Loaded.RenderingConfiguration.ShowLife ?  life + "/" + maxLife : null,
                MapAssistConfiguration.Loaded.RenderingConfiguration.ShowLifePerc ?  lifePerc.ToString("F0") + "%" : null
            }.Where(line => line != null).ToArray();

            foreach (var (line, i) in lifeText.Select((x, i) => (x, i)))
            {
                DrawText(gfx, new Point(centerX - lmOffsetX, lmY + fontSize * i), line, fontFamily, fontSize, Color.White, true, TextAlign.Center);
            }

            var mana = _gameData.PlayerUnit.Mana;
            var maxMana = _gameData.PlayerUnit.MaxMana;
            var manaPerc = _gameData.PlayerUnit.ManaPercentage;

            var manaText = new string[]
            {
                MapAssistConfiguration.Loaded.RenderingConfiguration.ShowMana?  mana + "/" + maxMana: null,
                MapAssistConfiguration.Loaded.RenderingConfiguration.ShowManaPerc ?  manaPerc.ToString("F0") + "%" : null
            }.Where(line => line != null).ToArray();

            foreach (var (line, i) in manaText.Select((x, i) => (x, i)))
            {
                DrawText(gfx, new Point(centerX + lmOffsetX * 1.02f, lmY + fontSize * i), line, fontFamily, fontSize, Color.White, true, TextAlign.Center);
            }

            // Player Experience
            if (_gameData.PlayerUnit.Level > 0)
            {
                var blackBrush = CreateBrush(gfx, Color.Black, 0.7f);
                var font = CreateFont(gfx, fontFamily, gfx.ScaleFontSize(17));

                var anchor = new Point(centerX, gfx.Height * 0.94f);

                var text = new string[] {
                    MapAssistConfiguration.Loaded.RenderingConfiguration.ShowCurrentLevel ? "Lvl " + _gameData.PlayerUnit.Level : null,
                    MapAssistConfiguration.Loaded.RenderingConfiguration.ShowExpProgress ? _gameData.PlayerUnit.LevelProgress.ToString("n2") + "%": null
                }.Where(x => x != null).ToArray();

                if (text.Length > 0)
                {
                    var textSize = gfx.MeasureString(font, string.Join(Environment.NewLine, text));

                    foreach (var line in text)
                    {
                        var lineSize = gfx.MeasureString(font, line);

                        gfx.FillRectangle(blackBrush, new Rectangle(anchor.X - textSize.X / 2, anchor.Y - lineSize.Y / 2, anchor.X + textSize.X / 2, anchor.Y + lineSize.Y / 2));
                        DrawText(gfx, anchor, line, fontFamily, font.FontSize * 0.8f, Color.White, false, TextAlign.Center);

                        anchor = anchor.Add(0, lineSize.Y);
                    }
                }
            }

            // Belt items
            if (MapAssistConfiguration.Loaded.RenderingConfiguration.ShowPotionBelt)
            {
                var font = CreateFont(gfx, fontFamily, gfx.ScaleFontSize(20));
                var colors = new Color[]
                {
                    Color.FromArgb(238, 168, 174), // Health
                    Color.FromArgb(169, 183, 238), // Mana
                    Color.FromArgb(200, 119, 199), // Rejuv
                };

                for (var i = 0; i < 4; i++)
                {
                    var items = _gameData.PlayerUnit.BeltItems[i].Where(x => x != null).ToArray();

                    if (items.Length == 0) continue;

                    var itemTypes = items.Select(x => x.Item.IsHealthPotion() ? 0 : x.Item.IsManaPotion() ? 1 : x.Item.IsRejuvPotion() ? 2 : 3).ToArray();
                    var color = itemTypes.Distinct().Count() == 1 && itemTypes[0] < colors.Length ? colors[itemTypes[0]] : Color.White;
                    var showAsterisk = items.Count(x => x.Item == items[0].Item) < items.Length;

                    var position = new Point(
                        0.5f * gfx.Width + 0.16f * gfx.Height + 8.00f + 0.0575f * gfx.Height * i,
                        0.99f * gfx.Height - font.FontSize
                    );

                    DrawText(gfx, position, items.Length.ToString(), fontFamily, font.FontSize, color, true, TextAlign.Right);

                    position.Y += font.FontSize - 0.05f * gfx.Height;

                    if (showAsterisk)
                    {
                        DrawText(gfx, position, "*", fontFamily, font.FontSize, color, true, TextAlign.Right);
                    }
                }
            }
        }

        public void DrawWatermark(Graphics gfx)
        {
            var font = "Exocet Blizzard Mixed Caps";
            var fontSize = gfx.ScaleFontSize(18);
            var textColor = Color.FromArgb(199, 179, 119);

            var text = "https://mapassist.github.io";
            var textSize = gfx.MeasureString(CreateFont(gfx, font, fontSize), text);
            var anchor = new Point(gfx.Width - 5, gfx.Height - textSize.Y);
            DrawText(gfx, anchor, text, font, fontSize, textColor, true, TextAlign.Right, opacity: 0.5f);

            fontSize = gfx.ScaleFontSize(12);
            text = "100% Free Software and Support";
            textSize = gfx.MeasureString(CreateFont(gfx, font, fontSize), text);

            anchor = anchor.Subtract(0, textSize.Y);
            DrawText(gfx, anchor, text, font, fontSize, textColor, true, TextAlign.Right, opacity: 0.5f);
        }

        // Drawing Utility Functions
        private void DrawBitmap(Graphics gfx, Bitmap bitmapDX, Point anchor, float opacity,
            float size = 1)
        {
            RenderTarget renderTarget = gfx.GetRenderTarget();

            var sourceRect = new Rectangle(0, 0, bitmapDX.Size.Width, bitmapDX.Size.Height);
            var destRect = new Rectangle(
                anchor.X,
                anchor.Y,
                anchor.X + bitmapDX.Size.Width * size,
                anchor.Y + bitmapDX.Size.Height * size);

            renderTarget.DrawBitmap(bitmapDX, destRect, opacity, BitmapInterpolationMode.NearestNeighbor, sourceRect);
        }

        private void DrawIcon(Graphics gfx, IconRendering rendering, Point position,
            bool equalScaling = false)
        {
            var renderTarget = gfx.GetRenderTarget();
            var currentTransform = renderTarget.Transform;
            renderTarget.Transform = Matrix3x2.Identity.ToDXMatrix();

            position = Vector2.Transform(position.ToVector(), currentTransform.ToMatrix()).ToPoint();

            var fill = !rendering.IconShape.ToString().ToLower().EndsWith("outline");
            var fillBrush = CreateIconBrush(gfx, rendering.IconColor, rendering.IconOpacity);
            var outlineBrush = CreateIconBrush(gfx, rendering.IconOutlineColor, rendering.IconOpacity);

            var points = GetIconShape(rendering, equalScaling).Select(point => point.Add(position)).ToArray();

            var _scaleHeight = equalScaling ? scaleWidth : scaleHeight;

            using (var geo = points.ToGeometry(gfx, fill))
            {
                switch (rendering.IconShape)
                {
                    case Shape.Ellipse:
                        if (rendering.IconColor.A > 0)
                        {
                            gfx.FillEllipse(fillBrush, position, rendering.IconSize * scaleWidth / 2, rendering.IconSize * _scaleHeight / 2); // Divide by 2 because the parameter requires a radius
                        }

                        if (rendering.IconOutlineColor.A > 0)
                        {
                            gfx.DrawEllipse(outlineBrush, position, rendering.IconSize * scaleWidth / 2, rendering.IconSize * _scaleHeight / 2, rendering.IconThickness); // Divide by 2 because the parameter requires a radius
                        }

                        break;

                    case Shape.Portal:
                        if (rendering.IconColor.A > 0)
                        {
                            gfx.FillEllipse(fillBrush, position, rendering.IconSize * scaleWidth / 2, rendering.IconSize * 2 * scaleWidth / 2); // Use scaleWidth so it doesn't shrink the height in overlay mode, allows portal to look the same in both modes
                        }

                        if (rendering.IconOutlineColor.A > 0)
                        {
                            gfx.DrawEllipse(outlineBrush, position, rendering.IconSize * scaleWidth / 2, rendering.IconSize * 2 * scaleWidth / 2, rendering.IconThickness); // Use scaleWidth so it doesn't shrink the height in overlay mode, allows portal to look the same in both modes
                        }

                        break;

                    default:
                        if (points == null) break;

                        if (rendering.IconColor.A > 0)
                        {
                            gfx.FillGeometry(geo, fillBrush);
                        }

                        if (rendering.IconOutlineColor.A > 0)
                        {
                            gfx.DrawGeometry(geo, outlineBrush, rendering.IconThickness);
                        }

                        if (rendering.IconShape == Shape.Pentagram && (rendering.IconColor.A > 0 || rendering.IconOutlineColor.A > 0))
                        {
                            var brush = rendering.IconOutlineColor.A > 0 ? outlineBrush : fillBrush;
                            gfx.DrawEllipse(brush, position, rendering.IconSize * scaleWidth / 2 + rendering.IconThickness, rendering.IconSize * _scaleHeight / 2 + rendering.IconThickness, rendering.IconThickness); // Divide by 2 because the parameter requires a radius
                        }

                        break;
                }
            }

            renderTarget.Transform = currentTransform;
        }

        private void DrawLine(Graphics gfx, PointOfInterestRendering rendering, Point startPosition, Point endPosition,
            bool transformForMap = true, bool renderIfShort = false, int spacing = 5)
        {
            var renderTarget = gfx.GetRenderTarget();
            var currentTransform = renderTarget.Transform;
            renderTarget.Transform = Matrix3x2.Identity.ToDXMatrix();

            if (transformForMap)
            {
                startPosition = Vector2.Transform(startPosition.ToVector(), areaTransformMatrix).ToPoint();
                endPosition = Vector2.Transform(endPosition.ToVector(), areaTransformMatrix).ToPoint();
            }

            var angle = endPosition.Subtract(startPosition).Angle();
            var length = endPosition.Rotate(-angle, startPosition).X - startPosition.X;

            var brush = CreateIconBrush(gfx, rendering.LineColor, rendering.IconOpacity);

            startPosition = startPosition.Rotate(-angle, startPosition).Add(spacing * scaleWidth, 0).Rotate(angle, startPosition); // Add a little extra spacing from the start point

            if (renderIfShort || length > 60)
            {
                if (rendering.CanDrawArrowHead())
                {
                    endPosition = endPosition.Rotate(-angle, startPosition).Subtract(spacing * scaleWidth, 0).Rotate(angle, startPosition); // Subtract a little extra spacing from the end point

                    var points = new Point[]
                    {
                        new Point((float)(Math.Sqrt(3) / -2), 0.5f),
                        new Point((float)(Math.Sqrt(3) / -2), -0.5f),
                        new Point(0, 0),
                    }.Select(point => point.Multiply(rendering.ArrowHeadSize).Rotate(angle).Add(endPosition)).ToArray(); // Divide by 2 to make the line end inside the triangle

                    endPosition = endPosition.Rotate(-angle, startPosition).Subtract(rendering.ArrowHeadSize / 2f, 0).Rotate(angle, startPosition); // Make the line end inside the triangle

                    gfx.DrawLine(brush, startPosition, endPosition, rendering.LineThickness);
                    gfx.FillTriangle(brush, points[0], points[1], points[2]);
                }
                else
                {
                    gfx.DrawLine(brush, startPosition, endPosition, rendering.LineThickness);
                }
            }

            renderTarget.Transform = currentTransform;
        }

        private void DrawIconText(Graphics gfx, PointOfInterestRendering rendering, Point position, string text,
            Color? color = null)
        {
            var renderTarget = gfx.GetRenderTarget();
            var currentTransform = renderTarget.Transform;
            renderTarget.Transform = Matrix3x2.Identity.ToDXMatrix();

            var playerCoord = Vector2.Transform(_gameData.PlayerPosition.ToVector(), areaTransformMatrix);
            position = Vector2.Transform(position.ToVector(), areaTransformMatrix).ToPoint();

            var useColor = color ?? rendering.LabelColor;
            var opacity = (float)(MapAssistConfiguration.Loaded.RenderingConfiguration.IconOpacity * rendering.IconOpacity);

            var fontSize = gfx.ScaleFontSize((float)rendering.LabelFontSize);
            var font = CreateFont(gfx, rendering.LabelFont, fontSize);
            var iconShape = GetIconShape(rendering).ToRectangle();
            var textSize = gfx.MeasureString(font, text);
            var textShadow = rendering.LabelTextShadow;

            var multiplier = playerCoord.Y < position.Y ? 1 : -1;
            if (rendering.CanDrawIcon())
            {
                position = position.Add(new Point(0, iconShape.Height / 2 * (!rendering.CanDrawArrowHead() ? -1 : multiplier)));
            }

            position = position.Add(new Point(0, (textSize.Y / 2 + 5) * (!rendering.CanDrawArrowHead() ? -1 : multiplier)));
            position = MoveTextInBounds(position, text, textSize);

            DrawText(gfx, position, text, rendering.LabelFont, fontSize, useColor, textShadow, TextAlign.Center, opacity);

            renderTarget.Transform = currentTransform;
        }

        private void DrawText(Graphics gfx, Point position, string text, string fontFamily, float fontSize,
            Color color, bool textShadow, TextAlign align, float opacity = 1f)
        {
            var font = CreateFont(gfx, fontFamily, fontSize);
            var brush = CreateBrush(gfx, color, opacity);

            var stringSize = gfx.MeasureString(font, text);
            if (align == TextAlign.Center)
            {
                position = position.Subtract(stringSize.X / 2, stringSize.Y / 2);
            }
            else if (align == TextAlign.Right)
            {
                position = position.Subtract(stringSize.X, 0);
            }

            if (textShadow)
            {
                var shadowOpacity = opacity * 0.6f;
                var shadowBrush = CreateBrush(gfx, Color.Black, shadowOpacity);
                var shadowOffset = fontSize * 0.0625f;
                gfx.DrawText(font, shadowBrush, position.X + shadowOffset, position.Y + shadowOffset, text);
            }

            gfx.DrawText(font, brush, position, text);
        }

        // Utility Functions
        private Point[] GetIconShape(IconRendering render,
            bool equalScaling = false)
        {
            var _scaleHeight = equalScaling ? scaleWidth : scaleHeight;
            var halfSize = render.IconSize / 2f;

            Func<Point, Point> Transform(float heightScale, bool addRotation)
            {
                Point _transform(Point point)
                {
                    return point.Multiply(render.IconSize).Subtract(halfSize).Rotate(addRotation ? _rotateRadians : 0).Multiply(scaleWidth, heightScale);
                };

                return _transform;
            };

            switch (render.IconShape)
            {
                case Shape.Square:
                    return new Point[]
                    {
                        new Point(0, 0),
                        new Point(1, 0),
                        new Point(1, 1),
                        new Point(0, 1)
                    }.Select(Transform(_scaleHeight, true)).ToArray();

                case Shape.Ellipse: // Use a rectangle since that's effectively the same size and that's all this function is used for at the moment
                    return new Point[]
                    {
                        new Point(0, 0),
                        new Point(1, 0),
                        new Point(1, 1),
                        new Point(0, 1)
                    }.Select(Transform(_scaleHeight, true)).ToArray();

                case Shape.Portal: // Use a rectangle since that's effectively the same size and that's all this function is used for at the moment
                    return new Point[]
                    {
                        new Point(0, 0),
                        new Point(1, 0),
                        new Point(1, 1),
                        new Point(0, 1)
                    }.Select(Transform(scaleWidth * 2, true)).ToArray(); // Use scaleWidth so it doesn't shrink the height in overlay mode, allows portal to look the same in both modes

                case Shape.Polygon:
                    var cutSize = 0.1f;

                    return new Point[]
                    {
                        new Point(0, 0.5f), new Point(0.5f - cutSize, 0.5f - cutSize),
                        new Point(0.5f, 0), new Point(0.5f + cutSize, 0.5f - cutSize),
                        new Point(1, 0.5f),
                        new Point(0.5f + cutSize, 0.5f + cutSize),
                        new Point(0.5f, 1),
                        new Point(0.5f - cutSize, 0.5f + cutSize)
                    }.Select(Transform(_scaleHeight, false)).ToArray();

                case Shape.Cross:
                    var a = 0.25f;
                    var b = 0.50f;
                    var c = 0.75f;
                    var d = 1;

                    return new Point[]
                    {
                        new Point(0, a), new Point(a, 0), new Point(b, a), new Point(c, 0),
                        new Point(d, a), new Point(c, b), new Point(d, c), new Point(c, d),
                        new Point(b, c), new Point(a, d), new Point(0, c), new Point(a, b)
                    }.Select(Transform(_scaleHeight, false)).ToArray();

                case Shape.Dress:
                    return new Point[]
                    {
                        new Point(0.50f, 0),
                        new Point(0.60f, 0.20f),
                        new Point(0.22f, 0.85f),
                        new Point(0.50f, 1),
                        new Point(0.78f, 0.85f),
                        new Point(0.40f, 0.20f)
                    }.Select(Transform(scaleWidth, false)).ToArray();

                case Shape.Kite:
                    return new Point[]
                    {
                        new Point(0.50f, 0),
                        new Point(0.15f, 0.35f),
                        new Point(0.50f, 1),
                        new Point(0.85f, 0.35f)
                    }.Select(Transform(scaleWidth, false)).ToArray();

                case Shape.Stick:
                    return new Point[]
                    {
                        new Point(0.42f, 0),
                        new Point(0.58f, 0),
                        new Point(0.50f, 0.65f),
                    }.Select(Transform(scaleWidth, false)).ToArray();

                case Shape.Leg:
                    return new Point[]
                    {
                        new Point(0.2f, 0.6f),
                        new Point(0.4f, 0f),
                        new Point(0.50f, 0),
                        new Point(0.35f, 0.40f),
                        new Point(0.4f, 0.40f),
                        new Point(0.50f, 0.50f),
                    }.Select(Transform(scaleWidth, false)).ToArray();

                case Shape.Pentagram:
                    return new Point[]
                    {
                        new Point(0.50f, 1f),
                        new Point(0.22f, 0.1f),
                        new Point(0.96f, 0.66f),
                        new Point(0.04f, 0.66f),
                        new Point(0.78f, 0.1f),
                        new Point(0.50f, 1f),
                    }.Select(Transform(_scaleHeight, false)).ToArray();
            }

            return new Point[]
            {
                new Point(0, 0)
            };
        }

        private float GetIconOpacity(IconRendering rendering)
        {
            return (float)(MapAssistConfiguration.Loaded.RenderingConfiguration.IconOpacity * rendering.IconOpacity);
        }

        private IconRendering GetMonsterIconRendering(UnitMonster monster)
        {
            switch (monster.MonsterType)
            {
                case MonsterTypeFlags.SuperUnique: return MapAssistConfiguration.Loaded.MapConfiguration.SuperUniqueMonster;
                case MonsterTypeFlags.Champion: return MapAssistConfiguration.Loaded.MapConfiguration.ChampionMonster;
                case MonsterTypeFlags.Minion: return MapAssistConfiguration.Loaded.MapConfiguration.MinionMonster;
                case MonsterTypeFlags.Unique: return MapAssistConfiguration.Loaded.MapConfiguration.UniqueMonster;
            }
            return MapAssistConfiguration.Loaded.MapConfiguration.NormalMonster;
        }

        private bool IsInBounds(Point point, Point origin,
            float padding = 0)
        {
            return point == MovePointInBounds(point, origin, padding);
        }

        private Point MovePointInBounds(Point point, Point origin,
            float padding = 0)
        {
            var resizeScale = 1f;

            var bounds = new Rectangle(_drawBounds.Left + padding, _drawBounds.Top + padding, _drawBounds.Right - padding, _drawBounds.Bottom - padding);
            var startScreenCoord = Vector2.Transform(origin.ToVector(), areaTransformMatrix);
            var endScreenCoord = Vector2.Transform(point.ToVector(), areaTransformMatrix);

            if (endScreenCoord.X < bounds.Left) resizeScale = Math.Min(resizeScale, (bounds.Left - startScreenCoord.X) / (endScreenCoord.X - startScreenCoord.X));
            if (endScreenCoord.X > bounds.Right) resizeScale = Math.Min(resizeScale, (bounds.Right - startScreenCoord.X) / (endScreenCoord.X - startScreenCoord.X));
            if (endScreenCoord.Y < bounds.Top) resizeScale = Math.Min(resizeScale, (bounds.Top - startScreenCoord.Y) / (endScreenCoord.Y - startScreenCoord.Y));
            if (endScreenCoord.Y > bounds.Bottom) resizeScale = Math.Min(resizeScale, (bounds.Bottom - startScreenCoord.Y) / (endScreenCoord.Y - startScreenCoord.Y));

            if (resizeScale < 1)
            {
                return point.Subtract(origin).Multiply(resizeScale).Add(origin);
            }
            else
            {
                return point;
            }
        }

        private Point MoveTextInBounds(Point point, string text, Point size)
        {
            var halfSize = size.Multiply(1 / 2f);

            if (point.X - halfSize.X < _drawBounds.Left) point.X += _drawBounds.Left - point.X + halfSize.X + 1; // Single extra pixel to prevent GameOverlay from word wrapping
            if (point.X + halfSize.X > _drawBounds.Right) point.X += _drawBounds.Right - point.X - halfSize.X - 1; // Single extra pixel to prevent GameOverlay from word wrapping
            if (point.Y - halfSize.Y < _drawBounds.Top) point.Y += _drawBounds.Top - point.Y + halfSize.Y + 1; // Single extra pixel to prevent GameOverlay from word wrapping
            if (point.Y + halfSize.Y > _drawBounds.Bottom) point.Y += _drawBounds.Bottom - point.Y - halfSize.Y - 1; // Single extra pixel to prevent GameOverlay from word wrapping

            return point;
        }

        private (float, float) GetScaleRatios()
        {
            var multiplier = 1f;
            if (MapAssistConfiguration.Loaded.RenderingConfiguration.OverlayMode)
            {
                var zoomLevel = (float)MapAssistConfiguration.Loaded.RenderingConfiguration.ZoomLevel;
                multiplier = 4.5f * (float)Math.Pow(zoomLevel > 1 ? 2 : 4, -zoomLevel + 1); // Hitting +/- should make the map bigger/smaller, respectively, like in overlay = false mode

                if (MapAssistConfiguration.Loaded.RenderingConfiguration.Position != MapPosition.Center)
                {
                    multiplier *= 0.5f;
                }
            }
            else
            {
                var maxUpscale = 2;
                var scaleAreaWidth = _areaData.ViewOutputRect.Width * maxUpscale;
                if (scaleAreaWidth < MapAssistConfiguration.Loaded.RenderingConfiguration.Size)
                {
                    multiplier = scaleAreaWidth / _areaData.ViewOutputRect.Height / maxUpscale * (MapAssistConfiguration.Loaded.RenderingConfiguration.Size / scaleAreaWidth);
                }
                else
                {
                    multiplier = Math.Min(MapAssistConfiguration.Loaded.RenderingConfiguration.Size, _areaData.ViewOutputRect.Width) / _areaData.ViewOutputRect.Height;
                }

                if (multiplier == 0)
                {
                    multiplier = 1;
                }
            }

            if (multiplier != 1 || MapAssistConfiguration.Loaded.RenderingConfiguration.OverlayMode)
            {
                var heightShrink = MapAssistConfiguration.Loaded.RenderingConfiguration.OverlayMode ? 0.5f : 1f;
                var widthShrink = MapAssistConfiguration.Loaded.RenderingConfiguration.OverlayMode ? 1f : 1f;

                return (multiplier * widthShrink, multiplier * heightShrink);
            }
            return (multiplier, multiplier);
        }

        private void CalcTransformMatrices(Graphics gfx)
        {
            mapTransformMatrix = Matrix3x2.Identity;

            if (MapAssistConfiguration.Loaded.RenderingConfiguration.OverlayMode)
            {
                mapTransformMatrix = Matrix3x2.CreateTranslation(_areaData.Origin.ToVector())
                    * Matrix3x2.CreateTranslation(Vector2.Negate(_gameData.PlayerPosition.ToVector()))
                    * Matrix3x2.CreateRotation(_rotateRadians)
                    * Matrix3x2.CreateScale(scaleWidth, scaleHeight);

                if (MapAssistConfiguration.Loaded.RenderingConfiguration.Position == MapPosition.Center)
                {
                    mapTransformMatrix *= Matrix3x2.CreateTranslation(new Vector2(gfx.Width / 2, gfx.Height / 2))
                        * Matrix3x2.CreateTranslation(new Vector2(2, -8)); // Brute forced to perfectly line up with the in game map;
                }
                else
                {
                    mapTransformMatrix *= Matrix3x2.CreateTranslation(new Vector2(_drawBounds.Left, _drawBounds.Top))
                        * Matrix3x2.CreateTranslation(new Vector2(_drawBounds.Width / 2.12f, _drawBounds.Height / 2.42f));
                }

                mapTransformMatrix *= Matrix3x2.CreateTranslation(MapAssistConfiguration.Loaded.RenderingConfiguration.Offset.ToVector());
            }
            else
            {
                mapTransformMatrix = Matrix3x2.CreateTranslation(new Vector2(_areaData.MapPadding / 2, _areaData.MapPadding / 2))
                    * Matrix3x2.CreateTranslation(Vector2.Negate(new Vector2(_areaData.ViewInputRect.Width / 2, _areaData.ViewInputRect.Height / 2)))
                    * Matrix3x2.CreateRotation(_rotateRadians)
                    * Matrix3x2.CreateTranslation(Vector2.Negate(new Vector2(_areaData.ViewOutputRect.Left, _areaData.ViewOutputRect.Top)))
                    * Matrix3x2.CreateScale(scaleWidth, scaleHeight)
                    * Matrix3x2.CreateTranslation(new Vector2(_drawBounds.Left, _drawBounds.Top));

                if (MapAssistConfiguration.Loaded.RenderingConfiguration.Position == MapPosition.Center)
                {
                    mapTransformMatrix *= Matrix3x2.CreateTranslation(new Vector2(_drawBounds.Width / 2, _drawBounds.Height / 2))
                        * Matrix3x2.CreateTranslation(Vector2.Negate(new Vector2(_areaData.ViewOutputRect.Width / 2 * scaleWidth, _areaData.ViewOutputRect.Height / 2 * scaleHeight)));
                }
            }

            areaTransformMatrix = Matrix3x2.CreateTranslation(Vector2.Negate(_areaData.Origin.ToVector()));

            if (!MapAssistConfiguration.Loaded.RenderingConfiguration.OverlayMode)
            {
                areaTransformMatrix *= Matrix3x2.CreateTranslation(Vector2.Negate(new Vector2(_areaData.ViewInputRect.Left, _areaData.ViewInputRect.Top)));
            }

            areaTransformMatrix *= mapTransformMatrix;
        }

        // Creates and cached resources
        private Dictionary<string, Bitmap> cacheBitmaps = new Dictionary<string, Bitmap>();

        private Bitmap CreateResourceBitmap(Graphics gfx, string name)
        {
            var key = name;

            if (!cacheBitmaps.ContainsKey(key))
            {
                var renderTarget = gfx.GetRenderTarget();

                var resImg = Properties.Resources.ResourceManager.GetObject(name);
                cacheBitmaps[key] = new System.Drawing.Bitmap((System.Drawing.Bitmap)resImg).ToDXBitmap(renderTarget);
            }

            return cacheBitmaps[key];
        }

        private Dictionary<(string, float), Font> cacheFonts = new Dictionary<(string, float), Font>();

        private Font CreateFont(Graphics gfx, string fontFamilyName, float size)
        {
            var key = (fontFamilyName, size);
            if (!cacheFonts.ContainsKey(key))
            {
                if (fontFamilyName.Equals("Exocet Blizzard Mixed Caps"))
                {
                    cacheFonts[key] = _exocetFont.CreateFont(size);
                }
                else if (fontFamilyName.Equals("Formal 436"))
                {
                    cacheFonts[key] = _formalFont.CreateFont(size);
                }
                else
                {
                    cacheFonts[key] = gfx.CreateFont(fontFamilyName, size);
                }
            }

            return cacheFonts[key];
        }

        private Dictionary<(Color, float?), SolidBrush> cacheBrushes = new Dictionary<(Color, float?), SolidBrush>();

        private SolidBrush CreateMapBrush(Graphics gfx, Color color,
            float opacity = 1)
        {
            return CreateBrush(gfx, color, opacity * (float)MapAssistConfiguration.Loaded.RenderingConfiguration.Opacity);
        }

        private SolidBrush CreateIconBrush(Graphics gfx, Color color,
            float opacity = 1)
        {
            return CreateBrush(gfx, color, opacity * (float)MapAssistConfiguration.Loaded.RenderingConfiguration.IconOpacity);
        }

        private SolidBrush CreateBrush(Graphics gfx, Color color,
            float opacity = 1)
        {
            var key = (color, opacity);
            if (!cacheBrushes.ContainsKey(key)) cacheBrushes[key] = gfx.CreateSolidBrush(color.SetOpacity((float)opacity).ToGameOverlayColor());
            return cacheBrushes[key];
        }

        ~Compositor() => Dispose();

        public void Dispose()
        {
            foreach (var (gamemap, _) in gamemaps)
            {
                if (gamemap != null) gamemap.Dispose();
            }

            gamemaps = new HashSet<(Bitmap, Point)>();

            foreach (var item in cacheBitmaps.Values) item.Dispose();
            foreach (var item in cacheFonts.Values) item.Dispose();
            foreach (var item in cacheBrushes.Values) item.Dispose();
        }
    }
}
