from typing import Callable

from item.pickit_item import PickitItem
from item.types import ItemType, ItemQuality, ItemMode, ItemFlag, Stat, SkillTree, PickitType

class PickitConfig:
    # Low-priority consumable items to pick up when low on them
    ConsumableItems: dict[ItemType, PickitType] = {}

    # Basic items without quality, such as runes, gems, and potions
    BasicItems: dict[ItemType, PickitType] = {}
    
    # Magic items (items with one of the magic qualities: unique, set, rare, or magic)
    MagicItems: dict[(ItemType, ItemQuality), PickitType] = {}

    # Items to identify and determine pickit based on identified stats
    IdentifiedItems: dict[(ItemType, ItemQuality), list[Callable[[PickitItem], bool]]] = {}

    # These are normal white or grey, eth or non-eth items that can be socketed and/or superior
    NormalItems: dict[ItemType, list[Callable[[PickitItem], bool]]] = {}

    def __init__(self):
        self.ConsumableItems = {
            ItemType.FullRejuvenationPotion: PickitType.Keep,
            ItemType.RejuvenationPotion: PickitType.Keep,
            ItemType.SuperHealingPotion: PickitType.DontKeep,
            ItemType.SuperManaPotion: PickitType.DontKeep,
            ItemType.GreaterHealingPotion: PickitType.DontKeep,
            ItemType.GreaterManaPotion: PickitType.DontKeep,
        }

        self.BasicItems = {
            ItemType.KeyOfTerror: PickitType.Keep,
            ItemType.KeyOfHate: PickitType.Keep,
            ItemType.KeyOfDestruction: PickitType.Keep,
            
            ItemType.TwistedEssenceOfSuffering: PickitType.Keep,
            ItemType.ChargedEssenceOfHatred: PickitType.Keep,
            ItemType.BurningEssenceOfTerror: PickitType.Keep,
            ItemType.FesteringEssenceOfDestruction: PickitType.Keep,

            ItemType.ElRune: PickitType.DontKeep,
            ItemType.EldRune: PickitType.DontKeep,
            ItemType.TirRune: PickitType.DontKeep,
            ItemType.NefRune: PickitType.DontKeep,
            ItemType.EthRune: PickitType.DontKeep,
            ItemType.IthRune: PickitType.DontKeep,
            ItemType.TalRune: PickitType.DontKeep,
            ItemType.RalRune: PickitType.DontKeep,
            ItemType.OrtRune: PickitType.DontKeep,
            ItemType.ThulRune: PickitType.DontKeep,
            ItemType.AmnRune: PickitType.DontKeep,
            ItemType.SolRune: PickitType.DontKeep,
            ItemType.ShaelRune: PickitType.DontKeep,
            ItemType.DolRune: PickitType.DontKeep,
            ItemType.HelRune: PickitType.DontKeep,
            ItemType.IoRune: PickitType.DontKeep,
            ItemType.LumRune: PickitType.DontKeep,
            ItemType.KoRune: PickitType.DontKeep,
            ItemType.FalRune: PickitType.DontKeep,
            ItemType.LemRune: PickitType.Keep,
            ItemType.PulRune: PickitType.Keep,
            ItemType.UmRune: PickitType.Keep,
            ItemType.MalRune: PickitType.Keep,
            ItemType.IstRune: PickitType.Keep,
            ItemType.GulRune: PickitType.Keep,
            ItemType.VexRune: PickitType.KeepAndNotify,
            ItemType.OhmRune: PickitType.KeepAndNotify,
            ItemType.LoRune: PickitType.KeepAndNotify,
            ItemType.SurRune: PickitType.KeepAndNotify,
            ItemType.BerRune: PickitType.KeepAndNotify,
            ItemType.JahRune: PickitType.KeepAndNotify,
            ItemType.ChamRune: PickitType.KeepAndNotify,
            ItemType.ZodRune: PickitType.KeepAndNotify,

            ItemType.ChippedAmethyst: PickitType.DontKeep,
            ItemType.ChippedTopaz: PickitType.DontKeep,
            ItemType.ChippedSapphire: PickitType.DontKeep,
            ItemType.ChippedEmerald: PickitType.DontKeep,
            ItemType.ChippedRuby: PickitType.DontKeep,
            ItemType.ChippedDiamond: PickitType.DontKeep,

            ItemType.FlawedAmethyst: PickitType.DontKeep,
            ItemType.FlawedTopaz: PickitType.DontKeep,
            ItemType.FlawedSapphire: PickitType.DontKeep,
            ItemType.FlawedEmerald: PickitType.DontKeep,
            ItemType.FlawedRuby: PickitType.DontKeep,
            ItemType.FlawedDiamond: PickitType.DontKeep,

            ItemType.Amethyst: PickitType.DontKeep,
            ItemType.Topaz: PickitType.DontKeep,
            ItemType.Sapphire: PickitType.DontKeep,
            ItemType.Emerald: PickitType.DontKeep,
            ItemType.Ruby: PickitType.DontKeep,
            ItemType.Diamond: PickitType.DontKeep,

            ItemType.FlawlessAmethyst: PickitType.DontKeep,
            ItemType.FlawlessTopaz: PickitType.DontKeep,
            ItemType.FlawlessSapphire: PickitType.DontKeep,
            ItemType.FlawlessEmerald: PickitType.DontKeep,
            ItemType.FlawlessRuby: PickitType.DontKeep,
            ItemType.FlawlessDiamond: PickitType.DontKeep,

            ItemType.PerfectAmethyst: PickitType.Keep,
            ItemType.PerfectTopaz: PickitType.Keep,
            ItemType.PerfectSapphire: PickitType.Keep,
            ItemType.PerfectEmerald: PickitType.Keep,
            ItemType.PerfectRuby: PickitType.Keep,
            ItemType.PerfectDiamond: PickitType.Keep,
        }

        self.MagicItems = {
            (ItemType.GrandCharm, ItemQuality.Unique): PickitType.Keep,
            (ItemType.SmallCharm, ItemQuality.Unique): PickitType.Keep,
            (ItemType.Amulet, ItemQuality.Unique): PickitType.Keep,
            (ItemType.Ring, ItemQuality.Unique): PickitType.Keep,
            (ItemType.Jewel, ItemQuality.Unique): PickitType.Keep,

            (ItemType.DemonhideArmor, ItemQuality.Unique): PickitType.DontKeep,
            (ItemType.ChaosArmor, ItemQuality.Unique): PickitType.DontKeep,
            (ItemType.StuddedLeather, ItemQuality.Unique): PickitType.DontKeep,
            (ItemType.AncientArmor, ItemQuality.Unique): PickitType.DontKeep,
            (ItemType.GhostArmor, ItemQuality.Unique): PickitType.DontKeep,
            (ItemType.MagePlate, ItemQuality.Unique): PickitType.DontKeep,
            (ItemType.OrnatePlate, ItemQuality.Unique): PickitType.DontKeep,
            (ItemType.WireFleece, ItemQuality.Unique): PickitType.DontKeep,
            (ItemType.KrakenShell, ItemQuality.Unique): PickitType.DontKeep,
            (ItemType.BalrogSkin, ItemQuality.Unique): PickitType.Keep,
            (ItemType.SacredArmor, ItemQuality.Unique): PickitType.Keep,
            (ItemType.Cuirass, ItemQuality.Unique): PickitType.DontKeep,
            (ItemType.TemplarCoat, ItemQuality.Unique): PickitType.Keep,
            (ItemType.DuskShroud, ItemQuality.Unique): PickitType.Keep,
            (ItemType.MeshArmor, ItemQuality.Unique): PickitType.DontKeep,
            (ItemType.SerpentskinArmor, ItemQuality.Unique): PickitType.Keep,
            (ItemType.RussetArmor, ItemQuality.Unique): PickitType.DontKeep,
            (ItemType.EmbossedPlate, ItemQuality.Unique): PickitType.DontKeep,
            (ItemType.Sash, ItemQuality.Unique): PickitType.DontKeep,
            (ItemType.Belt, ItemQuality.Unique): PickitType.DontKeep,
            (ItemType.MeshBelt, ItemQuality.Unique): PickitType.DontKeep,
            (ItemType.VampirefangBelt, ItemQuality.Unique): PickitType.DontKeep,
            (ItemType.HeavyBelt, ItemQuality.Unique): PickitType.DontKeep,
            (ItemType.SharkskinBelt, ItemQuality.Unique): PickitType.DontKeep,
            (ItemType.BattleBelt, ItemQuality.Unique): PickitType.DontKeep,
            (ItemType.WarBelt, ItemQuality.Unique): PickitType.Keep,
            (ItemType.SpiderwebSash, ItemQuality.Unique): PickitType.Keep,
            (ItemType.MithrilCoil, ItemQuality.Unique): PickitType.Keep,
            (ItemType.DemonhideBoots, ItemQuality.Unique): PickitType.DontKeep,
            (ItemType.LightPlatedBoots, ItemQuality.Unique): PickitType.DontKeep,
            (ItemType.BoneweaveBoots, ItemQuality.Unique): PickitType.Keep,
            (ItemType.MeshBoots, ItemQuality.Unique): PickitType.DontKeep,
            (ItemType.SharkskinBoots, ItemQuality.Unique): PickitType.DontKeep,
            (ItemType.MyrmidonGreaves, ItemQuality.Unique): PickitType.Keep,
            (ItemType.WarBoots, ItemQuality.Unique): PickitType.DontKeep,
            (ItemType.BattleBoots, ItemQuality.Unique): PickitType.Keep,
            (ItemType.ScarabshellBoots, ItemQuality.Unique): PickitType.Keep,
            (ItemType.Boots, ItemQuality.Unique): PickitType.DontKeep,
            (ItemType.HeavyGloves, ItemQuality.Unique): PickitType.DontKeep,
            (ItemType.ChainGloves, ItemQuality.Unique): PickitType.DontKeep,
            (ItemType.VampireboneGloves, ItemQuality.Unique): PickitType.Keep,
            (ItemType.Gauntlets, ItemQuality.Unique): PickitType.DontKeep,
            (ItemType.LightGauntlets, ItemQuality.Unique): PickitType.DontKeep,
            (ItemType.OgreGauntlets, ItemQuality.Unique): PickitType.Keep,
            (ItemType.Vambraces, ItemQuality.Unique): PickitType.DontKeep,
            (ItemType.DemonhideGloves, ItemQuality.Unique): PickitType.DontKeep,
            (ItemType.HeavyBracers, ItemQuality.Unique): PickitType.DontKeep,
            (ItemType.SharkskinGloves, ItemQuality.Unique): PickitType.DontKeep,
            (ItemType.BattleGauntlets, ItemQuality.Unique): PickitType.DontKeep,
            (ItemType.WarGauntlets, ItemQuality.Unique): PickitType.DontKeep,
            (ItemType.SkullCap, ItemQuality.Unique): PickitType.DontKeep,
            (ItemType.WarHat, ItemQuality.Unique): PickitType.DontKeep,
            (ItemType.GrandCrown, ItemQuality.Unique): PickitType.Keep,
            (ItemType.BoneVisage, ItemQuality.Unique): PickitType.Keep,
            (ItemType.SpiredHelm, ItemQuality.Unique): PickitType.Keep,
            (ItemType.DemonHead, ItemQuality.Unique): PickitType.Keep,
            (ItemType.Corona, ItemQuality.Unique): PickitType.KeepAndNotify,
            (ItemType.Diadem, ItemQuality.Unique): PickitType.KeepAndNotify,
            (ItemType.Shako, ItemQuality.Unique): PickitType.Keep,
            (ItemType.Tiara, ItemQuality.Unique): PickitType.Keep,
            (ItemType.Casque, ItemQuality.Unique): PickitType.DontKeep,
            (ItemType.GrimHelm, ItemQuality.Unique): PickitType.Keep,
            (ItemType.WingedHelm, ItemQuality.Unique): PickitType.DontKeep,
            (ItemType.Basinet, ItemQuality.Unique): PickitType.DontKeep,
            (ItemType.Armet, ItemQuality.Unique): PickitType.DontKeep,
            (ItemType.DeathMask, ItemQuality.Unique): PickitType.DontKeep,
            (ItemType.Sallet, ItemQuality.Unique): PickitType.DontKeep,
            (ItemType.SlayerGuard, ItemQuality.Unique): PickitType.Keep,
            (ItemType.FuryVisor, ItemQuality.Unique): PickitType.Keep,
            (ItemType.BloodSpirit, ItemQuality.Unique): PickitType.DontKeep,
            (ItemType.TotemicMask, ItemQuality.Unique): PickitType.DontKeep,
            (ItemType.EarthSpirit, ItemQuality.Unique): PickitType.Keep,
            (ItemType.SkySpirit, ItemQuality.Unique): PickitType.Keep,
            (ItemType.SuccubusSkull, ItemQuality.Unique): PickitType.Keep,
            (ItemType.BloodlordSkull, ItemQuality.Unique): PickitType.Keep,
            (ItemType.HierophantTrophy, ItemQuality.Unique): PickitType.Keep,
            (ItemType.GrimWand, ItemQuality.Unique): PickitType.DontKeep,
            (ItemType.TombWand, ItemQuality.Unique): PickitType.DontKeep,
            (ItemType.BurntWand, ItemQuality.Unique): PickitType.Keep,
            (ItemType.LichWand, ItemQuality.Unique): PickitType.DontKeep,
            (ItemType.UnearthedWand, ItemQuality.Unique): PickitType.Keep,
            (ItemType.Buckler, ItemQuality.Unique): PickitType.DontKeep,
            (ItemType.Defender, ItemQuality.Unique): PickitType.DontKeep,
            (ItemType.RoundShield, ItemQuality.Unique): PickitType.DontKeep,
            (ItemType.GrimShield, ItemQuality.Unique): PickitType.DontKeep,
            (ItemType.TrollNest, ItemQuality.Unique): PickitType.DontKeep,
            (ItemType.Monarch, ItemQuality.Unique): PickitType.Keep,
            (ItemType.Luna, ItemQuality.Unique): PickitType.DontKeep,
            (ItemType.BarbedShield, ItemQuality.Unique): PickitType.DontKeep,
            (ItemType.BladeBarrier, ItemQuality.Unique): PickitType.DontKeep,
            (ItemType.Scutum, ItemQuality.Unique): PickitType.DontKeep,
            (ItemType.Aegis, ItemQuality.Unique): PickitType.DontKeep,
            (ItemType.TrollNest, ItemQuality.Unique): PickitType.DontKeep,
            (ItemType.DragonShield, ItemQuality.Unique): PickitType.DontKeep,
            (ItemType.Ward, ItemQuality.Unique): PickitType.DontKeep,
            (ItemType.ZakarumShield, ItemQuality.Unique): PickitType.Keep,
            (ItemType.SacredRondache, ItemQuality.Unique): PickitType.DontKeep,
            (ItemType.GildedShield, ItemQuality.Unique): PickitType.Keep,
            (ItemType.WingedAxe, ItemQuality.Unique): PickitType.Keep,
            (ItemType.WingedKnife, ItemQuality.Unique): PickitType.Keep,
            (ItemType.FlyingAxe, ItemQuality.Unique): PickitType.DontKeep,
            (ItemType.Scourge, ItemQuality.Unique): PickitType.Keep,
            (ItemType.BoneKnife, ItemQuality.Unique): PickitType.DontKeep,
            (ItemType.Dagger, ItemQuality.Unique): PickitType.DontKeep,
            (ItemType.ThunderMaul, ItemQuality.Unique): PickitType.DontKeep,
            (ItemType.LegendaryMallet, ItemQuality.Unique): PickitType.Keep,
            (ItemType.Tulwar, ItemQuality.Unique): PickitType.DontKeep,
            (ItemType.PhaseBlade, ItemQuality.Unique): PickitType.DontKeep,
            (ItemType.ElderStaff, ItemQuality.Unique): PickitType.DontKeep,
            (ItemType.ArchonStaff, ItemQuality.Unique): PickitType.Keep,
            (ItemType.QuarterStaff, ItemQuality.Unique): PickitType.Keep,
            (ItemType.DivineScepter, ItemQuality.Unique): PickitType.DontKeep,
            (ItemType.MightyScepter, ItemQuality.Unique): PickitType.Keep,
            (ItemType.EttinAxe, ItemQuality.Unique): PickitType.Keep,
            (ItemType.DimensionalShard, ItemQuality.Unique): PickitType.Keep,
            (ItemType.EldritchOrb, ItemQuality.Unique): PickitType.Keep,
            (ItemType.SwirlingCrystal, ItemQuality.Unique): PickitType.DontKeep,
            (ItemType.Thresher, ItemQuality.Unique): PickitType.Keep,
            (ItemType.CrypticAxe, ItemQuality.Unique): PickitType.Keep,
            (ItemType.OgreAxe, ItemQuality.Unique): PickitType.DontKeep,
            (ItemType.MatriarchalJavelin, ItemQuality.Unique): PickitType.DontKeep,
            (ItemType.CeremonialJavelin, ItemQuality.Unique): PickitType.Keep,
            (ItemType.HydraBow, ItemQuality.Unique): PickitType.Keep,
            (ItemType.CeremonialBow, ItemQuality.Unique): PickitType.DontKeep,
            (ItemType.MatriarchalBow, ItemQuality.Unique): PickitType.DontKeep,
            (ItemType.BattleCestus, ItemQuality.Unique): PickitType.DontKeep,
            (ItemType.GreaterTalons, ItemQuality.Unique): PickitType.DontKeep,
            (ItemType.WristSword, ItemQuality.Unique): PickitType.DontKeep,
            (ItemType.FeralClaws, ItemQuality.Unique): PickitType.DontKeep,
            
            # Set Items
            (ItemType.Amulet, ItemQuality.Set): PickitType.DontKeep,
            (ItemType.Ring, ItemQuality.Set): PickitType.DontKeep,
            (ItemType.BattleBoots, ItemQuality.Set): PickitType.DontKeep,
            (ItemType.HuntersGuise, ItemQuality.Set): PickitType.DontKeep,
            (ItemType.ShadowPlate, ItemQuality.Set): PickitType.DontKeep,
            (ItemType.MythicalSword, ItemQuality.Set): PickitType.DontKeep,
            (ItemType.OrnatePlate, ItemQuality.Set): PickitType.DontKeep,
            (ItemType.Caduceus, ItemQuality.Set): PickitType.Keep,
            (ItemType.VortexShield, ItemQuality.Set): PickitType.DontKeep,
            (ItemType.OrnatePlate, ItemQuality.Set): PickitType.DontKeep,
            (ItemType.WingedHelm, ItemQuality.Set): PickitType.DontKeep,
            (ItemType.RoundShield, ItemQuality.Set): PickitType.DontKeep,
            (ItemType.SacredArmor, ItemQuality.Set): PickitType.Keep,
            (ItemType.AvengerGuard, ItemQuality.Set): PickitType.DontKeep,
            (ItemType.WarGauntlets, ItemQuality.Set): PickitType.DontKeep,
            (ItemType.WarBoots, ItemQuality.Set): PickitType.DontKeep,
            (ItemType.OgreMaul, ItemQuality.Set): PickitType.DontKeep,
            (ItemType.WarBelt, ItemQuality.Set): PickitType.DontKeep,
            (ItemType.BrambleMitts, ItemQuality.Set): PickitType.DontKeep,
            (ItemType.GrandMatronBow, ItemQuality.Set): PickitType.DontKeep,
            (ItemType.Diadem, ItemQuality.Set): PickitType.DontKeep,
            (ItemType.KrakenShell, ItemQuality.Set): PickitType.DontKeep,
            (ItemType.BattleGauntlets, ItemQuality.Set): PickitType.DontKeep,
            (ItemType.SharkskinBelt, ItemQuality.Set): PickitType.DontKeep,
            (ItemType.MeshBoots, ItemQuality.Set): PickitType.DontKeep,
            (ItemType.LoricatedMail, ItemQuality.Set): PickitType.DontKeep,
            (ItemType.ScissorsSuwayyah, ItemQuality.Set): PickitType.DontKeep,
            (ItemType.GrimHelm, ItemQuality.Set): PickitType.DontKeep,
            (ItemType.SwirlingCrystal, ItemQuality.Set): PickitType.DontKeep,
            (ItemType.MeshBelt, ItemQuality.Set): PickitType.DontKeep,
            (ItemType.LacqueredPlate, ItemQuality.Set): PickitType.KeepAndNotify,
            (ItemType.DeathMask, ItemQuality.Set): PickitType.DontKeep,
            (ItemType.HeavyBracers, ItemQuality.Set): PickitType.DontKeep,
            (ItemType.TrollBelt, ItemQuality.Set): PickitType.Keep,
            (ItemType.CantorTrophy, ItemQuality.Set): PickitType.DontKeep,
            (ItemType.BoneVisage, ItemQuality.Set): PickitType.DontKeep,
            (ItemType.ChaosArmor, ItemQuality.Set): PickitType.DontKeep,
            (ItemType.ChainGloves, ItemQuality.Set): PickitType.DontKeep,
            
            # Magic Items
            (ItemType.GrandCharm, ItemQuality.Magic): PickitType.Keep,
            (ItemType.LargeCharm, ItemQuality.Magic): PickitType.DontKeep,
            (ItemType.SmallCharm, ItemQuality.Magic): PickitType.Keep,
            (ItemType.Jewel, ItemQuality.Magic): PickitType.DontKeep,
            (ItemType.Monarch, ItemQuality.Magic): PickitType.DontKeep,
            
            # Rare Items
            (ItemType.Jewel, ItemQuality.Unique): PickitType.DontKeep,
        }

        # If you have an item listed below, these rules will be applied to it. If any
        # of the rules in the list match the item, the item will be stashed. The rules
        # should be functions that take in a PickitItem and return a boolean.
        self.NormalItems = {
            # Non-eth Enigma/CoH/Fortitude bases
            ItemType.ArchonPlate: [lambda item: not item.is_ethereal and (item.sockets in [0, 3, 4]) and item.check(Stat.EnhancedDefense, ">=", 14)],
            ItemType.DuskShroud: [lambda item: not item.is_ethereal and (item.sockets in [0, 3, 4]) and item.check(Stat.EnhancedDefense, ">=", 15)],
            ItemType.MagePlate: [lambda item: not item.is_ethereal and (item.sockets in [0, 3]) and item.check(Stat.EnhancedDefense, ">=", 10)],
            
            # Eth items for merc Fortitude/Treachery
            ItemType.ArchonPlate: [lambda item: item.is_ethereal and (item.sockets in [0, 3, 4]) and item.check(Stat.EnhancedDefense, ">=", 10)],
            ItemType.LacqueredPlate: [lambda item: item.is_ethereal and (item.sockets in [0, 3, 4]) and item.check(Stat.EnhancedDefense, ">=", 10)],
            ItemType.SacredArmor: [lambda item: item.is_ethereal and (item.sockets in [0, 3, 4]) and item.check(Stat.EnhancedDefense, ">=", 10)],

            # Eth polearms
            ItemType.Thresher: [
                lambda item: item.is_ethereal and item.sockets and item.quality <= ItemQuality.Normal and item.sockets in [0, 4],
                lambda item: item.is_ethereal and item.sockets and item.quality == ItemQuality.Superior and item.sockets == 4,
            ],
            ItemType.GreatPoleaxe: [
                lambda item: item.is_ethereal and item.sockets and item.quality <= ItemQuality.Normal and item.sockets in [0, 4],
                lambda item: item.is_ethereal and item.sockets and item.quality == ItemQuality.Superior and item.sockets == 4,
            ],
            ItemType.GiantThresher: [
                lambda item: item.is_ethereal and item.sockets and item.quality <= ItemQuality.Normal and item.sockets in [0, 4],
                lambda item: item.is_ethereal and item.sockets and item.quality == ItemQuality.Superior and item.sockets == 4,
            ],
            ItemType.CrypticAxe: [
                lambda item: item.is_ethereal and item.sockets and item.quality <= ItemQuality.Normal and item.sockets in [0, 4],
                lambda item: item.is_ethereal and item.sockets and item.quality == ItemQuality.Superior and item.sockets == 4,
            ],
            ItemType.Thresher: [
                lambda item: item.is_ethereal and item.sockets and item.quality <= ItemQuality.Normal and item.sockets in [0, 4],
                lambda item: item.is_ethereal and item.sockets and item.quality == ItemQuality.Superior and item.sockets == 4,
            ],
            ItemType.ColossusVoulge: [lambda item: item.is_ethereal and item.sockets == 4],

            # Other eth weapons
            ItemType.ColossusBlade: [lambda item: item.is_ethereal and item.sockets in [0, 6]],
            ItemType.WarPike: [lambda item: item.is_ethereal and item.sockets in [0, 6]],

            # Non-eth weapons
            ItemType.ColossusSword: [lambda item: item.sockets == 5 and item.check(Stat.EnhancedDamage, ">", 0)],
            ItemType.PhaseBlade: [
                lambda item: item.sockets == 5,
                lambda item: item.sockets == 5 and item.check(Stat.EnhancedDamage, ">", 0),
                lambda item: item.sockets in [0, 5, 6] and item.check(Stat.EnhancedDamage, ">=", 15),
            ],
        }

        # If you have an item listed below, it will be identified if it isn't already,
        # and these rules will be applied to it. If any of the rules in the list match
        # the item, the item will be stashed. The rules should be functions that take
        # in a PickitItem and return a boolean.
        self.IdentifiedItems = {
            (ItemType.GrandCharm, ItemQuality.Magic): [
                lambda item: item.check(Stat.MaxDamage, ">=", 10) and item.check(Stat.MaxLife, ">=", 20),
                lambda item: item.check(Stat.AddSkillTab, "==", SkillTree.PaladinCombatSkills),
                lambda item: item.check(Stat.AddSkillTab, "==", SkillTree.SorceressCold),
                lambda item: item.check(Stat.AddSkillTab, "==", SkillTree.SorceressFire),
                lambda item: item.check(Stat.AddSkillTab, "==", SkillTree.SorceressLightning),
                lambda item: item.check(Stat.AddSkillTab, "==", SkillTree.AmazonJavelinAndSpear) and item.check(Stat.MaxLife, ">=", 20),
                lambda item: item.check(Stat.AddSkillTab, "==", SkillTree.NecromancerPoisonAndBone) and item.check(Stat.MaxLife, ">=", 20),
                lambda item: item.check(Stat.AddSkillTab, "==", SkillTree.NecromancerSummoning) and item.check(Stat.MaxLife, ">=", 30),
                lambda item: item.check(Stat.AddSkillTab, "==", SkillTree.BarbarianWarcries) and item.check(Stat.MaxLife, ">=", 30),
                lambda item: item.check(Stat.AddSkillTab, "==", SkillTree.BarbarianWarcries) and item.check(Stat.GoldFind, ">=", 20),
                lambda item: item.check(Stat.AddSkillTab, "==", SkillTree.DruidElemental) and item.check(Stat.MaxLife, ">=", 20),
                lambda item: item.check(Stat.AddSkillTab, "==", SkillTree.AssassinTraps) and item.check(Stat.MaxLife, ">=", 20),
            ],
            (ItemType.SmallCharm, ItemQuality.Magic): [
                lambda item: item.check(Stat.MaxLife, ">=", 20) and (item.check(Stat.FireResist, ">=", 10) or item.check(Stat.LightningResist, ">=", 10)),
                lambda item: item.check(Stat.MagicFind, ">=", 7) and (item.check(Stat.MaxDamage, ">=", 3) or item.check(Stat.FasterHitRecovery, ">=", 10)),
                lambda item: item.check(Stat.AllResist, ">=", 5), # 5@
                lambda item: item.check(Stat.MagicFind, ">=", 7), # 7 MF
                lambda item: item.check(Stat.MaxLife, ">=", 20), # 20 Life
                lambda item: item.check(Stat.MaxLife, ">=", 18) and item.check(Stat.MaxMana, ">=", 17), # 18+ life/17 mana SC
                lambda item: item.check(Stat.MaxLife, ">=", 15) and item.check(Stat.MaxDamage, ">=", 3), # 15+ life/3max SC
            ],
            (ItemType.Ring, ItemQuality.Unique): [
                # Unique Rings
                lambda item: item.check(Stat.AllSkills, ">=", 1) and item.check(Stat.MaxMana, ">=", 20), # SoJ
                lambda item: item.check(Stat.AllSkills, ">=", 1) and item.check(Stat.LifeSteal, ">=", 3), # BK Ring
                lambda item: item.check(Stat.AbsorbLightningPercent, ">=", 15), # Wisp Projector
                lambda item: item.check(Stat.Dexterity, ">=", 20) and item.check(Stat.AttackRating, ">=", 250), # Raven Frost
                lambda item: item.check(Stat.MagicDamageReduction, ">=", 15), # Dwarf Star
                lambda item: item.check(Stat.MagicFind, ">=", 30) and item.check(Stat.AttackRating, ">=", 75), # Nagel
            ],
            (ItemType.Amulet, ItemQuality.Unique): [
                # Unique Amulets
                lambda item: item.check(Stat.AllSkills, ">=", 2) and item.check(Stat.AllResist, ">=", 20), # Mara's Kaleidoscope
                lambda item: item.check(Stat.AllSkills, ">=", 1) and item.check(Stat.LightningResist, ">=", 25), # Highlord's Wrath
            ],
        }

pickit_config = PickitConfig()
