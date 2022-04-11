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

using System;
using System.Collections.Generic;
using System.Drawing;
using System.Linq;

namespace MapAssist.Types
{
    public static class States
    {
        public static readonly int StateCount = (int)Enum.GetValues(typeof(State)).Cast<State>().Max();

        public static readonly Color DebuffColor = Color.FromArgb(255, 35, 55);
        public static readonly Color PassiveColor = Color.FromArgb(180, 180, 180); //255, 35, 55 = red/debuff //180, 180, 180 = gray/passive
        public static readonly Color BuffColor = Color.FromArgb(0, 135, 235);
        public static readonly Color AuraColor = Color.FromArgb(245, 220, 80);

        public static Color StateColor(State state)
        {
            if (PassiveStates.Contains(state)) { return PassiveColor; }
            if (BuffStates.Contains(state)) { return BuffColor; }
            if (AuraStates.Contains(state)) { return AuraColor; }
            if (DebuffStates.Contains(state)) { return DebuffColor; }
            return Color.Gray;
        }

        public static readonly List<State> PassiveStates = new List<State> {
            State.STATE_AVOID,
            State.STATE_AXEMASTERY,
            State.STATE_CLAWMASTERY,
            State.STATE_COLDMASTERY,
            State.STATE_CRITICALSTRIKE,
            State.STATE_DODGE,
            State.STATE_EVADE,
            State.STATE_FENRIS_RAGE,
            State.STATE_FIREMASTERY,
            State.STATE_INCREASEDSPEED,
            State.STATE_INCREASEDSTAMINA,
            State.STATE_IRONSKIN,
            State.STATE_LIGHTNINGMASTERY,
            State.STATE_MACEMASTERY,
            State.STATE_NATURALRESISTANCE,
            State.STATE_PENETRATE,
            State.STATE_PIERCE,
            State.STATE_POLEARMMASTERY,
            State.STATE_SPEARMASTERY,
            State.STATE_SWORDMASTERY,
            State.STATE_THROWINGMASTERY,
            State.STATE_WARMTH,
            State.STATE_WEAPONBLOCK
        };
        public static readonly List<State> AuraStates = new List<State> {
            State.STATE_BARBS,
            State.STATE_BLESSEDAIM,
            State.STATE_CLEANSING,
            State.STATE_CONCENTRATION,
            State.STATE_CONVICTION,
            State.STATE_DEFIANCE,
            State.STATE_FANATICISM,
            State.STATE_HOLYFIRE,
            State.STATE_HOLYSHOCK,
            State.STATE_HOLYWIND,
            State.STATE_MEDITATION,
            State.STATE_MIGHT,
            State.STATE_OAKSAGE,
            State.STATE_PRAYER,
            State.STATE_REDEMPTION,
            State.STATE_RESISTCOLD,
            State.STATE_RESISTFIRE,
            State.STATE_RESISTLIGHTNING,
            State.STATE_RESISTALL,
            State.STATE_SANCTUARY,
            State.STATE_STAMINA,
            State.STATE_THORNS,
            State.STATE_STAMINA,
            State.STATE_WOLVERINE
        };
        public static readonly List<State> BuffStates = new List<State> {
            State.STATE_ARMAGEDDON,
            State.STATE_BATTLECOMMAND,
            State.STATE_BATTLEORDERS,
            State.STATE_BEAR,
            State.STATE_BERSERK,
            State.STATE_BLADESHIELD,
            State.STATE_BLAZE,
            State.STATE_BONEARMOR,
            State.STATE_CHILLINGARMOR,
            State.STATE_CLOAK_OF_SHADOWS,
            State.STATE_CLOAKED,
            State.STATE_CYCLONEARMOR,
            State.STATE_ENCHANT,
            State.STATE_ENERGYSHIELD,
            State.STATE_FERALRAGE,
            State.STATE_FRENZY,
            State.STATE_FROZENARMOR,
            State.STATE_HOLYSHIELD,
            State.STATE_HURRICANE,
            State.STATE_INFERNO,
            State.STATE_INNERSIGHT,
            State.STATE_QUICKNESS,
            State.STATE_SHADOWWARRIOR,
            State.STATE_SHIVERARMOR,
            State.STATE_SHOUT,
            State.STATE_SLOWMISSILES,
            State.STATE_THUNDERSTORM,
            State.STATE_VALKYRIE,
            State.STATE_VENOMCLAWS,
            State.STATE_WOLF,
            State.STATE_FADE
        };
        public static readonly List<State> DebuffStates = new List<State> {
            State.STATE_AMPLIFYDAMAGE,
            State.STATE_ATTRACT,
            State.STATE_CONFUSE,
            State.STATE_CONVERSION,
            State.STATE_DECREPIFY,
            State.STATE_DIMVISION,
            State.STATE_IRONMAIDEN,
            State.STATE_LIFETAP,
            State.STATE_LOWERRESIST,
            State.STATE_TERROR,
            State.STATE_WEAKEN,
            State.STATE_CONVICTED,
            State.STATE_CONVICTION,
            State.STATE_POISON,
            State.STATE_COLD,
            State.STATE_SLOWED,
            State.STATE_BLOOD_MANA,
            State.STATE_DEFENSE_CURSE
        };
    }
    public static class StateMasks
    {
        public static readonly uint[] gdwBitMasks = new uint[]
        {
        0x00000001, 0x00000002, 0x00000004, 0x00000008, 0x00000010, 0x00000020, 0x00000040, 0x00000080,
        0x00000100, 0x00000200, 0x00000400, 0x00000800, 0x00001000, 0x00002000, 0x00004000, 0x00008000,
        0x00010000, 0x00020000, 0x00040000, 0x00080000, 0x00100000, 0x00200000, 0x00400000, 0x00800000,
        0x01000000, 0x02000000, 0x04000000, 0x08000000, 0x10000000, 0x20000000, 0x40000000, 0x80000000,
        };
        enum StateMask
        {
            STATEMASK_NOSEND,
            STATEMASK_AURA,
            STATEMASK_HIDE,
            STATEMASK_TRANSFORM,
            STATEMASK_PGSV,
            STATEMASK_ACTIVE,
            STATEMASK_REMHIT,
            STATEMASK_DAMBLUE,
            STATEMASK_DAMRED,
            STATEMASK_ATTBLUE,
            STATEMASK_ATTRED,
            STATEMASK_CURSE,
            STATEMASK_CURABLE,
            STATEMASK_PLRSTAYDEATH,
            STATEMASK_MONSTAYDEATH,
            STATEMASK_BOSSSTAYDEATH,
            STATEMASK_DISGUISE,
            STATEMASK_RESTRICT,
            STATEMASK_BLUE,
            STATEMASK_ARMBLUE,
            STATEMASK_RFBLUE,
            STATEMASK_RCBLUE,
            STATEMASK_RLBLUE,
            STATEMASK_RPBLUE,
            STATEMASK_STAMBARBLUE,
            STATEMASK_ARMRED,
            STATEMASK_RFRED,
            STATEMASK_RCRED,
            STATEMASK_RLRED,
            STATEMASK_RPRED,
            STATEMASK_EXP,
            STATEMASK_SHATTER,
            STATEMASK_LIFE,
            STATEMASK_UDEAD,
            STATEMASK_GREEN,
            STATEMASK_NOOVERLAYS,
            STATEMASK_NOCLEAR,
            STATEMASK_BOSSINV,
            STATEMASK_MELEEONLY,
            STATEMASK_NOTONDEAD,
        };
    }
    public static class ResistColors
    {
        public static Dictionary<Resist, Color> ResistColor = new Dictionary<Resist, Color>
        {
            {Resist.PHYSICAL, Color.RosyBrown},
            {Resist.MAGIC, Color.DarkOrange},
            {Resist.FIRE, Color.Red},
            {Resist.LIGHTNING, Color.Yellow},
            {Resist.COLD, Color.CornflowerBlue},
            {Resist.POISON, Color.LimeGreen},
        };
    }

    public enum Resist
    {
        PHYSICAL = 0,
        MAGIC = 1,
        FIRE = 2,
        LIGHTNING = 3,
        COLD = 4,
        POISON = 5
    }
    public enum State
    {
        STATE_NONE = 0,
        STATE_FREEZE,
        STATE_POISON,
        STATE_RESISTFIRE,
        STATE_RESISTCOLD,
        STATE_RESISTLIGHTNING,
        STATE_RESISTMAGIC,
        STATE_PLAYERBODY,
        STATE_RESISTALL,
        STATE_AMPLIFYDAMAGE,
        STATE_FROZENARMOR,
        STATE_COLD,
        STATE_INFERNO,
        STATE_BLAZE,
        STATE_BONEARMOR,
        STATE_CONCENTRATE,
        STATE_ENCHANT,
        STATE_INNERSIGHT,
        STATE_SKILL_MOVE,
        STATE_WEAKEN,
        STATE_CHILLINGARMOR,
        STATE_STUNNED,
        STATE_SPIDERLAY,
        STATE_DIMVISION,
        STATE_SLOWED,
        STATE_FETISHAURA,
        STATE_SHOUT,
        STATE_TAUNT,
        STATE_CONVICTION,
        STATE_CONVICTED,
        STATE_ENERGYSHIELD,
        STATE_VENOMCLAWS,
        STATE_BATTLEORDERS,
        STATE_MIGHT,
        STATE_PRAYER,
        STATE_HOLYFIRE,
        STATE_THORNS,
        STATE_DEFIANCE,
        STATE_THUNDERSTORM,
        STATE_LIGHTNINGBOLT,
        STATE_BLESSEDAIM,
        STATE_STAMINA,
        STATE_CONCENTRATION,
        STATE_HOLYWIND,
        STATE_HOLYWINDCOLD,
        STATE_CLEANSING,
        STATE_HOLYSHOCK,
        STATE_SANCTUARY,
        STATE_MEDITATION,
        STATE_FANATICISM,
        STATE_REDEMPTION,
        STATE_BATTLECOMMAND,
        STATE_PREVENTHEAL,
        STATE_CONVERSION,
        STATE_UNINTERRUPTABLE,
        STATE_IRONMAIDEN,
        STATE_TERROR,
        STATE_ATTRACT,
        STATE_LIFETAP,
        STATE_CONFUSE,
        STATE_DECREPIFY,
        STATE_LOWERRESIST,
        STATE_OPENWOUNDS,
        STATE_DOPPLEZON,
        STATE_CRITICALSTRIKE,
        STATE_DODGE,
        STATE_AVOID,
        STATE_PENETRATE,
        STATE_EVADE,
        STATE_PIERCE,
        STATE_WARMTH,
        STATE_FIREMASTERY,
        STATE_LIGHTNINGMASTERY,
        STATE_COLDMASTERY,
        STATE_SWORDMASTERY,
        STATE_AXEMASTERY,
        STATE_MACEMASTERY,
        STATE_POLEARMMASTERY,
        STATE_THROWINGMASTERY,
        STATE_SPEARMASTERY,
        STATE_INCREASEDSTAMINA,
        STATE_IRONSKIN,
        STATE_INCREASEDSPEED,
        STATE_NATURALRESISTANCE,
        STATE_FINGERMAGECURSE,
        STATE_NOMANAREGEN,
        STATE_JUSTHIT,
        STATE_SLOWMISSILES,
        STATE_SHIVERARMOR,
        STATE_BATTLECRY,
        STATE_BLUE,
        STATE_RED,
        STATE_DEATH_DELAY,
        STATE_VALKYRIE,
        STATE_FRENZY,
        STATE_BERSERK,
        STATE_REVIVE,
        STATE_ITEMFULLSET,
        STATE_SOURCEUNIT,
        STATE_REDEEMED,
        STATE_HEALTHPOT,
        STATE_HOLYSHIELD,
        STATE_JUST_PORTALED,
        STATE_MONFRENZY,
        STATE_CORPSE_NODRAW,
        STATE_ALIGNMENT,
        STATE_MANAPOT,
        STATE_SHATTER,
        STATE_SYNC_WARPED,
        STATE_CONVERSION_SAVE,
        STATE_PREGNANT,
        STATE_111,
        STATE_RABIES,
        STATE_DEFENSE_CURSE,
        STATE_BLOOD_MANA,
        STATE_BURNING,
        STATE_DRAGONFLIGHT,
        STATE_MAUL,
        STATE_CORPSE_NOSELECT,
        STATE_SHADOWWARRIOR,
        STATE_FERALRAGE,
        STATE_SKILLDELAY,
        STATE_PROGRESSIVE_DAMAGE,
        STATE_PROGRESSIVE_STEAL,
        STATE_PROGRESSIVE_OTHER,
        STATE_PROGRESSIVE_FIRE,
        STATE_PROGRESSIVE_COLD,
        STATE_PROGRESSIVE_LIGHTNING,
        STATE_SHRINE_ARMOR,
        STATE_SHRINE_COMBAT,
        STATE_SHRINE_RESIST_LIGHTNING,
        STATE_SHRINE_RESIST_FIRE,
        STATE_SHRINE_RESIST_COLD,
        STATE_SHRINE_RESIST_POISON,
        STATE_SHRINE_SKILL,
        STATE_SHRINE_MANA_REGEN,
        STATE_SHRINE_STAMINA,
        STATE_SHRINE_EXPERIENCE,
        STATE_FENRIS_RAGE,
        STATE_WOLF,
        STATE_BEAR,
        STATE_BLOODLUST,
        STATE_CHANGECLASS,
        STATE_ATTACHED,
        STATE_HURRICANE,
        STATE_ARMAGEDDON,
        STATE_INVIS,
        STATE_BARBS,
        STATE_WOLVERINE,
        STATE_OAKSAGE,
        STATE_VINE_BEAST,
        STATE_CYCLONEARMOR,
        STATE_CLAWMASTERY,
        STATE_CLOAK_OF_SHADOWS,
        STATE_RECYCLED,
        STATE_WEAPONBLOCK,
        STATE_CLOAKED,
        STATE_QUICKNESS,
        STATE_BLADESHIELD,
        STATE_FADE,
        STATE_SUMMONRESIST,
        STATE_OAKSAGECONTROL,
        STATE_WOLVERINECONTROL,
        STATE_BARBSCONTROL,
        STATE_DEBUGCONTROL,
        STATE_ITEMSET1,
        STATE_ITEMSET2,
        STATE_ITEMSET3,
        STATE_ITEMSET4,
        STATE_ITEMSET5,
        STATE_ITEMSET6,
        STATE_RUNEWORD,
        STATE_RESTINPEACE,
        STATE_CORPSEEXP,
        STATE_WHIRLWIND,
        STATE_FULLSETGENERIC,
        STATE_MONSTERSET,
        STATE_DELERIUM,
        STATE_ANTIDOTE,
        STATE_THAWING,
        STATE_STAMINAPOT,
        STATE_PASSIVE_RESISTFIRE,
        STATE_PASSIVE_RESISTCOLD,
        STATE_PASSIVE_RESISTLTNG,
        STATE_UBERMINION,
    };

    public enum Stat : short
    {
        Invalid = -1,
        Strength = 0,
        Energy,
        Dexterity,
        Vitality,
        StatPoints,
        SkillPoints,
        Life,
        MaxLife,
        Mana,
        MaxMana,
        Stamina,
        MaxStamina,
        Level,
        Experience,
        Gold,
        StashGold,
        ArmorPercent,
        MaxDamagePercent,
        MinDamagePercent,
        AttackRating,
        ChanceToBlock,
        MinDamage,
        MaxDamage,
        SecondMinDamage,
        SecMaxDamage,
        DamagePercent,
        ManaRecovery,
        ManaRecoveryBonus,
        StaminaRecoveryBonus,
        LastExp,
        NextExp,
        Defense,
        DefenseVsMissiles,
        DefenseVsHth,
        NormalDamageReduction,
        MagicDamageReduction,
        DamageReduced,
        MagicResist,
        MaxMagicResist,
        FireResist,
        MaxFireResist,
        LightningResist,
        MaxLightningResist,
        ColdResist,
        MaxColdResist,
        PoisonResist,
        MaxPoisonResist,
        DamageAura,
        FireMinDamage,
        FireMaxDamage,
        LightningMinDamage,
        LightningMaxDamage,
        MagicMinDamage,
        MagicMaxDamage,
        ColdMinDamage,
        ColdMaxDamage,
        ColdLength,
        PoisonMinDamage,
        PoisonMaxDamage,
        PoisonLength,
        LifeSteal,
        LifeStealMax,
        ManaSteal,
        ManaStealMax,
        StaminaDrainMinDamage,
        StaminaDrainMaxDamage,
        StunLength,
        VelocityPercent,
        AttackRate,
        OtherAnimRate,
        Quantity,
        Value,
        Durability,
        MaxDurability,
        HPRegen,
        MaxDurabilityPercent,
        MaxHPPercent,
        MaxManaPercent,
        AttackerTakesDamage,
        GoldFind,
        MagicFind,
        Knockback,
        TimeDuration,
        AddClassSkills,
        Unused84,
        AddExperience,
        HealAfterKill,
        ReducePrices,
        DoubleHerbDuration,
        LightRadius,
        LightColor,
        RequirementPercent,
        LevelRequire,
        IncreasedAttackSpeed,
        LevelRequirePercent,
        LastBlockFrame,
        FasterRunWalk,
        NonClassSkill,
        State,
        FasterHitRecovery,
        PlayerCount,
        PoisonOverrideLength,
        FasterBlockRate,
        BypassUndead,
        BypassDemons,
        FasterCastRate,
        BypassBeasts,
        SingleSkill,
        SlainMonstersRestInPeace,
        CurseResistance,
        PoisonLengthResist,
        NormalDamage,
        Howl,
        Stupidity,
        DamageTakenGoesToMana,
        IgnoreTargetsAR,
        FractionalTargetAC,
        PreventMonsterHeal,
        HalfFreezeDuration,
        AttackRatingPercent,
        DamageTargetAC,
        DemonDamagePercent,
        UndeadDamagePercent,
        DemonAttackRating,
        UndeadAttackRating,
        Throwable,
        ElemSkills,
        AllSkills,
        AttackerTakesLightDamage,
        IronMaidenLevel,
        LifeTapLevel,
        ThornsPercent,
        BoneArmor,
        BoneArmorMax,
        Freeze,
        OpenWounds,
        CrushingBlow,
        KickDamage,
        ManaAfterKill,
        HealAfterDemonKill,
        ExtraBlood,
        DeadlyStrike,
        AbsorbFirePercent,
        AbsorbFire,
        AbsorbLightningPercent,
        AbsorbLightning,
        AbsorbMagicPercent,
        AbsorbMagic,
        AbsorbColdPercent,
        AbsorbCold,
        Slow,
        Aura,
        Indestructible,
        CannotBeFrozen,
        StaminaDrainPercent,
        Reanimate,
        Pierce,
        MagicAarow,
        ExplosiveAarow,
        ThrowMinDamage,
        ThrowMaxDamage,
        SkillHandofAthena,
        SkillStaminaPercent,
        SkillPassiveStaminaPercent,
        SkillConcentration,
        SkillEnchant,
        SkillPierce,
        SkillConviction,
        SkillChillingArmor,
        SkillFrenzy,
        SkillDecrepify,
        SkillArmorPercent,
        Alignment,
        Target0,
        Target1,
        GoldLost,
        ConverisonLevel,
        ConverisonMaxHP,
        UnitDooverlay,
        AttackVsMonType,
        DamageVsMonType,
        Fade,
        ArmorOverridePercent,
        Unused183,
        Unused184,
        Unused185,
        Unused186,
        Unused187,
        AddSkillTab,
        Unused189,
        Unused190,
        Unused191,
        Unused192,
        Unused193,
        NumSockets,
        SkillOnAttack,
        SkillOnKill,
        SkillOnDeath,
        SkillOnHit,
        SkillOnLevelUp,
        Unused200,
        SkillOnGetHit,
        Unused202,
        Unused203,
        ItemChargedSkill,
        Unused205,
        Unused206,
        Unused207,
        Unused208,
        Unused209,
        Unused210,
        Unused211,
        Unused212,
        Unused213,
        ArmorPerLevel,
        ArmorPercentPerLevel,
        LifePerLevel,
        ManaPerLevel,
        MaxDamagePerLevel,
        MaxDamagePercentPerLevel,
        StrengthPerLevel,
        DexterityPerLevel,
        EnergyPerLevel,
        VitalityPerLevel,
        AttackRatingPerLevel,
        AttackRatingPercentPerLevel,
        ColdDamageMaxPerLevel,
        FireDamageMaxPerLevel,
        LightningDamageMaxPerLevel,
        PoisonDamageMaxPerLevel,
        ResistColdPerLevel,
        ResistFirePerLevel,
        ResistLightningPerLevel,
        ResistPoisonPerLevel,
        AbsorbColdPerLevel,
        AbsorbFirePerLevel,
        AbsorbLightningPerLevel,
        AbsorbPoisonPerLevel,
        ThornsPerLevel,
        FindGoldPerLevel,
        MagicFindPerLevel,
        RegenStaminaPerLevel,
        StaminaPerLevel,
        DamageDemonPerLevel,
        DamageUndeadPerLevel,
        AttackRatingDemonPerLevel,
        AttackRatingUndeadPerLevel,
        CrushingBlowPerLevel,
        OpenWoundsPerLevel,
        KickDamagePerLevel,
        DeadlyStrikePerLevel,
        FindGemsPerLevel,
        ReplenishDurability,
        ReplenishQuantity,
        ExtraStack,
        FindItem,
        SlashDamage,
        SlashDamagePercent,
        CrushDamage,
        CrushDamagePercent,
        ThrustDamage,
        ThrustDamagePercent,
        AbsorbSlash,
        AbsorbCrush,
        AbsorbThrust,
        AbsorbSlashPercent,
        AbsorbCrushPercent,
        AbsorbThrustPercent,
        ArmorByTime,
        ArmorPercentByTime,
        LifeByTime,
        ManaByTime,
        MaxDamageByTime,
        MaxDamagePercentByTime,
        StrengthByTime,
        DexterityByTime,
        EnergyByTime,
        VitalityByTime,
        AttackRatingByTime,
        AttackRatingPercentByTime,
        ColdDamageMaxByTime,
        FireDamageMaxByTime,
        LightningDamageMaxByTime,
        PoisonDamageMaxByTime,
        ResistColdByTime,
        ResistFireByTime,
        ResistLightningByTime,
        ResistPoisonByTime,
        AbsorbColdByTime,
        AbsorbFireByTime,
        AbsorbLightningByTime,
        AbsorbPoisonByTime,
        FindGoldByTime,
        MagicFindByTime,
        RegenStaminaByTime,
        StaminaByTime,
        DamageDemonByTime,
        DamageUndeadByTime,
        AttackRatingDemonByTime,
        AttackRatingUndeadByTime,
        CrushingBlowByTime,
        OpenWoundsByTime,
        KickDamageByTime,
        DeadlyStrikeByTime,
        FindGemsByTime,
        PierceCold,
        PierceFire,
        PierceLightning,
        PiercePoison,
        DamageVsMonster,
        DamagePercentVsMonster,
        AttackRatingVsMonster,
        AttackRatingPercentVsMonster,
        AcVsMonster,
        AcPercentVsMonster,
        FireLength,
        BurningMin,
        BurningMax,
        ProgressiveDamage,
        ProgressiveSteal,
        ProgressiveOther,
        ProgressiveFire,
        ProgressiveCold,
        ProgressiveLightning,
        ExtraCharges,
        ProgressiveAttackRating,
        PoisonCount,
        DamageFrameRate,
        PierceIdx,
        FireSkillDamage,
        LightningSkillDamage,
        ColdSkillDamage,
        PoisonSkillDamage,
        EnemyFireResist,
        EnemyLightningResist,
        EnemyColdResist,
        EnemyPoisonResist,
        PassiveCriticalStrike,
        PassiveDodge,
        PassiveAvoid,
        PassiveEvade,
        PassiveWarmth,
        PassiveMasteryMeleeAttackRating,
        PassiveMasteryMeleeDamage,
        PassiveMasteryMeleeCritical,
        PassiveMasteryThrowAttackRating,
        PassiveMasteryThrowDamage,
        PassiveMasteryThrowCritical,
        PassiveWeaponBlock,
        SummonResist,
        ModifierListSkill,
        ModifierListLevel,
        LastSentHPPercent,
        SourceUnitType,
        SourceUnitID,
        ShortParam1,
        QuestItemDifficulty,
        PassiveMagicMastery,
        PassiveMagicPierce,
    };
}
