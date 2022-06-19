using GameOverlay.Drawing;
using MapAssist.Helpers;
using MapAssist.Structs;
using System;
using System.Collections.Generic;

namespace MapAssist.Types
{
    public abstract class UnitAny
    {
        public IntPtr PtrUnit { get; private set; }
        public Structs.UnitAny Struct { get; private set; }
        public UnitType UnitType => Struct.UnitType;
        public uint UnitId => Struct.UnitId;
        public uint TxtFileNo => Struct.TxtFileNo;
        public Area Area { get; private set; }
        public Point Position => new Point(X, Y);
        public float X => IsMovable ? Path.DynamicX : (float)Path.StaticX;
        public float Y => IsMovable ? Path.DynamicY : (float)Path.StaticY;
        public StatListExStruct StatsStruct { get; private set; }
        public uint[] StateFlags { get; set; }
        public List<State> StateList { get; set; }
        public DateTime FoundTime { get; set; } = DateTime.Now;
        public bool IsHovered { get; set; } = false;
        public bool IsCached { get; set; } = false;
        private Path Path { get; set; }

        public Dictionary<Stats.Stat, Dictionary<ushort, int>> StatLayers { get; private set; }
        public Dictionary<Stats.Stat, int> Stats { get; private set; }
        public Dictionary<Stats.Stat, Dictionary<ushort, int>> StatLayersBase { get; private set; }
        public Dictionary<Stats.Stat, int> StatsBase { get; private set; }
        public Dictionary<Stats.Stat, Dictionary<ushort, int>> StatLayersAdded { get; private set; }
        public Dictionary<Stats.Stat, int> StatsAdded { get; private set; }
        public Dictionary<Stats.Stat, Dictionary<ushort, int>> StaffModsLayers { get; private set; }
        public Dictionary<Stats.Stat, int> StaffMods { get; private set; }

        public UnitAny(IntPtr ptrUnit)
        {
            PtrUnit = ptrUnit;

            if (IsValidPointer)
            {
                using (var processContext = GameManager.GetProcessContext())
                {
                    Struct = processContext.Read<Structs.UnitAny>(PtrUnit);
                    Path = new Path(Struct.pPath);
                }
            }
        }

        public void CopyFrom(UnitAny other)
        {
            if (Struct.UnitId != other.Struct.UnitId) IsCached = false; // Reload all data since the unit id changed

            PtrUnit = other.PtrUnit;
            Struct = other.Struct;
            Path = other.Path;
        }

        protected UpdateResult Update()
        {
            if (IsValidPointer)
            {
                using (var processContext = GameManager.GetProcessContext())
                {
                    var newStruct = processContext.Read<Structs.UnitAny>(PtrUnit);

                    if (newStruct.UnitId == uint.MaxValue) return UpdateResult.InvalidUpdate;
                    else Struct = newStruct;

                    if (IsCached) return UpdateResult.Cached;

                    if (IsValidUnit)
                    {
                        Area = Path.Room.RoomEx.Level.LevelId;

                        if (Struct.pStatsListEx != IntPtr.Zero)
                        {
                            StatsStruct = processContext.Read<StatListExStruct>(Struct.pStatsListEx);
                            StateFlags = StatsStruct.StateFlags;

                            (Stats, StatLayers) = ReadStats(StatsStruct.Stats);
                            (StatsBase, StatLayersBase) = ReadStats(StatsStruct.BaseStats.Stats);

                            if (UnitType == UnitType.Item)
                            {
                                var addedStatsStruct = GetAddedStatsListPtr();
                                if (addedStatsStruct.HasValue)
                                {
                                    (StatsAdded, StatLayersAdded) = ReadStats(addedStatsStruct.Value.BaseStats.Stats);

                                    if (addedStatsStruct.Value.pPrevLink != IntPtr.Zero)
                                    {
                                        var staffModsStruct = processContext.Read<StatListExStruct>(addedStatsStruct.Value.pPrevLink);
                                        (StaffMods, StaffModsLayers) = ReadStats(staffModsStruct.BaseStats.Stats);
                                    }
                                }
                            }
                        }

                        if (GameMemory.cache.ContainsKey(UnitId)) IsCached = true;

                        return UpdateResult.Updated;
                    }
                }
            }

            return UpdateResult.InvalidUpdate;
        }

        protected (Dictionary<Stats.Stat, int>, Dictionary<Stats.Stat, Dictionary<ushort, int>>) ReadStats(StatArrayStruct statArray)
        {
            using (var processContext = GameManager.GetProcessContext())
            {
                var stats = new Dictionary<Stats.Stat, int>();
                var statLayers = new Dictionary<Stats.Stat, Dictionary<ushort, int>>();

                var statValues = processContext.Read<StatValue>(statArray.pFirstStat, Convert.ToInt32(statArray.Size));

                foreach (var stat in statValues)
                {
                    if (statLayers.ContainsKey(stat.Stat))
                    {
                        if (stat.Layer == 0) continue;
                        if (!statLayers[stat.Stat].ContainsKey(stat.Layer))
                        {
                            statLayers[stat.Stat].Add(stat.Layer, stat.Value);
                        }
                    }
                    else
                    {
                        stats.Add(stat.Stat, stat.Value);
                        statLayers.Add(stat.Stat, new Dictionary<ushort, int>() { { stat.Layer, stat.Value } });
                    }
                }

                return (stats, statLayers);
            }
        }

        protected List<State> GetStateList()
        {
            var stateList = new List<State>();
            for (var i = 0; i <= States.StateCount; i++)
            {
                if (GetState((State)i))
                {
                    stateList.Add((State)i);
                }
            }
            return stateList;
        }

        protected StatListExStruct? GetAddedStatsListPtr(int flags = 0x40)
        {
            using (var processContext = GameManager.GetProcessContext())
            {
                if ((StatsStruct.BaseStats.Flags & 0x80000000) == 0)
                {
                    return null;
                }

                StatListExStruct statList;
                if (StatsStruct.pMyStats != IntPtr.Zero && (flags & 0x2000) != 0)
                {
                    statList = processContext.Read<StatListExStruct>(StatsStruct.pMyStats);
                }
                else if (StatsStruct.pLastList != IntPtr.Zero)
                {
                    statList = processContext.Read<StatListExStruct>(StatsStruct.pLastList);
                }
                else
                {
                    return null;
                }

                var tries = 0;
                while ((flags & statList.BaseStats.Flags & 0xFFFFDFFF) == 0)
                {
                    if (tries++ >= 10) return null; // Just to be safe

                    if (StatsStruct.pPrevLink != IntPtr.Zero)
                    {
                        var addressToRead = statList.pPrevLink;

                        statList = processContext.Read<StatListExStruct>(addressToRead);

                        if (addressToRead == statList.pPrevLink) // Memory didn't change
                        {
                            return null;
                        }
                    }
                    else
                    {
                        return null;
                    }
                }

                return statList;
            }
        }

        public bool GetState(State state)
        {
            return (StateFlags[(int)state >> 5] & StateMasks.gdwBitMasks[(int)state & 31]) > 0;
        }

        private bool IsMovable => !(Struct.UnitType == UnitType.Object || Struct.UnitType == UnitType.Item);

        public bool IsValidPointer => PtrUnit != IntPtr.Zero;

        public bool IsValidUnit => Struct.pUnitData != IntPtr.Zero && Struct.pPath != IntPtr.Zero && Struct.UnitType <= UnitType.Tile;

        public bool IsPlayer => Struct.UnitType == UnitType.Player && Struct.pAct != IntPtr.Zero;

        public bool IsMonster
        {
            get
            {
                if (Struct.UnitType != UnitType.Monster) return false;
                if (Struct.Mode == 0) return false;
                if (NPC.Dummies.ContainsKey(TxtFileNo)) return false;
                if (StateList.Contains(State.Revive)) return false;

                return true;
            }
        }

        public bool IsCorpse => Struct.isCorpse && UnitId != GameMemory.PlayerUnit.UnitId && Area != Area.None;

        public bool IsTargetableCorpse
        {
            get
            {
                return IsCorpse &&
                    !GetState(State.Freeze) &&
                    !GetState(State.Revive) &&
                    !GetState(State.Redeemed) &&
                    !GetState(State.CorpseNoDraw) &&
                    !GetState(State.Shatter) &&
                    !GetState(State.CorpseNoSelect);
            }
        }

        public List<string> StateStrings
        {
            get
            {
                var stateStrings = new List<string>();
                foreach (int i in Enum.GetValues(typeof(State)))
                {
                    var state = (State)i;
                    if (GetState(state) && state != State.Alignment) stateStrings.Add(state.ToString());
                }
                return stateStrings;
            }
        }

        public double DistanceTo(UnitAny other) => Math.Sqrt((Math.Pow(other.X - Position.X, 2) + Math.Pow(other.Y - Position.Y, 2)));

        public override bool Equals(object obj) => obj is UnitAny other && Equals(other);

        public bool Equals(UnitAny unit) => !(unit is null) && UnitId == unit.UnitId;

        public override int GetHashCode() => UnitId.GetHashCode();

        public abstract string HashString { get; }

        public static bool operator ==(UnitAny unit1, UnitAny unit2) => (unit1 is null && unit2 is null) || (!(unit1 is null) && unit1.Equals(unit2));

        public static bool operator !=(UnitAny unit1, UnitAny unit2) => !(unit1 == unit2);

        public enum UpdateResult
        {
            Updated,
            Cached,
            InvalidUpdate
        }
    }
}
