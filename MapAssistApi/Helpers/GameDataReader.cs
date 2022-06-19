using MapAssist.Settings;
using MapAssist.Types;
using System.Collections.Generic;
using System.Linq;

namespace MapAssist.Helpers
{
    public class GameDataReader
    {
        private static readonly NLog.Logger _log = NLog.LogManager.GetCurrentClassLogger();
        private volatile GameData _gameData;
        private AreaData _areaData;
        private MapApi _mapApi;
        private List<PointOfInterest> _pointOfInterest;

        public (GameData, AreaData, List<PointOfInterest>, bool) Get()
        {
            var gameData = GameMemory.GetGameData();
            var changed = false;

            if (gameData != null)
            {
                if (gameData.HasGameChanged(_gameData))
                {
                    if (gameData.MapSeed == 0 && !gameData.MapSeedReady)
                    {
                        _log.Info($"Brute forcing first map seed");

                        changed = true;
                        _areaData = null;
                    }
                    else
                    {
                        _log.Info($"Game changed to {gameData.Difficulty} with {gameData.MapSeed} seed");
                    }

                    _mapApi = new MapApi(gameData);
                }

                if (gameData.HasMapChanged(_gameData) && gameData.MapSeed > 0 && gameData.Area != Area.None)
                {
                    _log.Info($"Area changed to {gameData.Area}");
                    _areaData = _mapApi.GetMapData(gameData.Area);

                    if (_areaData == null)
                    {
                        _log.Info($"Area data not loaded");
                    }
                    else if (_areaData.PointsOfInterest == null)
                    {
                        _areaData.PointsOfInterest = PointOfInterestHandler.Get(_mapApi, _areaData, gameData);
                        _log.Info($"Found {_areaData.PointsOfInterest.Count} points of interest");
                    }
                    else
                    {
                        _log.Info($"POI not null: Found {_areaData.PointsOfInterest.Count} points of interest");
                    }

                    changed = true;
                }
            }

            _gameData = gameData;

            ImportFromGameData();

            if (_areaData != null)
            {
                _pointOfInterest = _areaData.PointsOfInterest;
            }
            if (_pointOfInterest == null)
            {
                _pointOfInterest = new List<PointOfInterest>();
            }
            return (_gameData, _areaData, _pointOfInterest, changed);
        }

        private void ImportFromGameData()
        {
            if (_gameData == null || _areaData == null) return;

            foreach (var gameObject in _gameData.Objects)
            {
                if (!_areaData.IncludesPoint(gameObject.Position)) continue;

                if (gameObject.IsShrine || gameObject.IsWell)
                {
                    var existingPoint = _areaData.PointsOfInterest.FirstOrDefault(x => x.Position == gameObject.Position);

                    if (existingPoint != null)
                    {
                        existingPoint.Label = Shrine.ShrineDisplayName(gameObject);
                    }
                    else
                    {
                        _areaData.PointsOfInterest.Add(new PointOfInterest()
                        {
                            Area = _areaData.Area,
                            Label = Shrine.ShrineDisplayName(gameObject),
                            Position = gameObject.Position,
                            RenderingSettings = MapAssistConfiguration.Loaded.MapConfiguration.Shrine,
                            Type = PoiType.Shrine
                        });
                    }
                }
            }
        }
    }
}
