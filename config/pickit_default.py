from typing import Callable, Union

from pickit.pickit_item import PickitItem
from pickit.types import Item, Options, Quality, ItemMode, Flag, Stat, SkillTree, Action, EthOption

class PickitConfig:
    # Low-priority consumable items to pick up when low on them
    ConsumableItems: dict[
        Item,
        Union[Action, tuple[Action, Options], bool]] = {}

    # Basic items without quality, such as runes, gems, and potions
    BasicItems: dict[
        Item,
        Union[Action, tuple[Action, Options], bool]] = {}
    
    # Magic items (items with one of the magic qualities: unique, set, rare, or magic)
    UnidentifiedItems: dict[
        (Item, Quality),
        Union[Action, tuple[Action, Options], bool]] = {}

    # Items to identify and determine pickit based on identified stats
    IdentifiedItems: dict[
        (Item, Quality),
        list[Callable[[PickitItem], Union[Action, tuple[Action, Options], bool]]]] = {}

    # These are normal white or grey, eth or non-eth items that can be socketed and/or superior
    NormalItems: dict[
        Item,
        list[Callable[[PickitItem], Union[Action, tuple[Action, Options], bool]]]] = {}

    def __init__(self):
        # Potions, etc (won't pick up more than needed)
        self.ConsumableItems = {
            Item.FullRejuvenationPotion: Action.Keep,
            Item.RejuvenationPotion: Action.Keep,
            # Item.SuperHealingPotion: Action.Keep,
            # Item.SuperManaPotion: Action.Keep,
            # Item.GreaterHealingPotion: Action.Keep,
            # Item.GreaterManaPotion: Action.Keep,
        }

        # Runes, Keys, etc
        self.BasicItems = {
            Item.KeyOfTerror: Action.Keep,
            Item.KeyOfHate: Action.Keep,
            Item.KeyOfDestruction: Action.Keep,
            
            # You can change the max quantity value from 3 to whatever you
            # want. Quantities picked up will be tracked based on the number
            # picked up in the current bot session.
            Item.TwistedEssenceOfSuffering: (Action.Keep, Options(max_quantity=3)),
            Item.ChargedEssenceOfHatred: (Action.Keep, Options(max_quantity=3)),
            Item.BurningEssenceOfTerror: (Action.Keep, Options(max_quantity=3)),
            Item.FesteringEssenceOfDestruction: (Action.Keep, Options(max_quantity=3)),

            # # You can change the "Action" to "Action.Keep" to disable a rule,
            # or you can just comment it out by putting a '#' at the beginning of
            # the line, like this:
            # Item.ElRune: (Action.Keep, Options(max_quantity=3)),
            # Item.EldRune: (Action.Keep, Options(max_quantity=3)),
            # Item.TirRune: (Action.Keep, Options(max_quantity=3)),
            # Item.NefRune: (Action.Keep, Options(max_quantity=3)),
            # Item.EthRune: (Action.Keep, Options(max_quantity=3)),
            # Item.IthRune: (Action.Keep, Options(max_quantity=3)),
            # Item.TalRune: (Action.Keep, Options(max_quantity=3)),
            # Item.RalRune: (Action.Keep, Options(max_quantity=3)),
            # Item.OrtRune: (Action.Keep, Options(max_quantity=3)),
            # Item.ThulRune: (Action.Keep, Options(max_quantity=3)),
            # Item.AmnRune: (Action.Keep, Options(max_quantity=3)),
            # Item.SolRune: (Action.Keep, Options(max_quantity=3)),
            # Item.ShaelRune: (Action.Keep, Options(max_quantity=3)),
            # Item.DolRune: (Action.Keep, Options(max_quantity=3)),
            # Item.HelRune: (Action.Keep, Options(max_quantity=3)),
            # Item.IoRune: (Action.Keep, Options(max_quantity=3)),
            # Item.LumRune: (Action.Keep, Options(max_quantity=3)),
            # Item.KoRune: (Action.Keep, Options(max_quantity=3)),
            # Item.FalRune: (Action.Keep, Options(max_quantity=3)),
            Item.LemRune: Action.Keep,
            Item.PulRune: Action.Keep,
            Item.UmRune: Action.Keep,
            Item.MalRune: Action.Keep,
            Item.IstRune: Action.Keep,
            Item.GulRune: Action.Keep,
            Item.VexRune: Action.KeepAndNotify,
            Item.OhmRune: Action.KeepAndNotify,
            Item.LoRune: Action.KeepAndNotify,
            Item.SurRune: Action.KeepAndNotify,
            Item.BerRune: Action.KeepAndNotify,
            Item.JahRune: Action.KeepAndNotify,
            Item.ChamRune: Action.KeepAndNotify,
            Item.ZodRune: Action.KeepAndNotify,

            # Item.ChippedAmethyst: (Action.Keep, Options(max_quantity=5)),
            # Item.ChippedTopaz: (Action.Keep, Options(max_quantity=5)),
            # Item.ChippedSapphire: (Action.Keep, Options(max_quantity=5)),
            # Item.ChippedEmerald: (Action.Keep, Options(max_quantity=5)),
            # Item.ChippedRuby: (Action.Keep, Options(max_quantity=5)),
            # Item.ChippedDiamond: (Action.Keep, Options(max_quantity=5)),

            # Item.FlawedAmethyst: (Action.Keep, Options(max_quantity=5)),
            # Item.FlawedTopaz: (Action.Keep, Options(max_quantity=5)),
            # Item.FlawedSapphire: (Action.Keep, Options(max_quantity=5)),
            # Item.FlawedEmerald: (Action.Keep, Options(max_quantity=5)),
            # Item.FlawedRuby: (Action.Keep, Options(max_quantity=5)),
            # Item.FlawedDiamond: (Action.Keep, Options(max_quantity=5)),

            # Item.Amethyst: (Action.Keep, Options(max_quantity=5)),
            # Item.Topaz: (Action.Keep, Options(max_quantity=5)),
            # Item.Sapphire: (Action.Keep, Options(max_quantity=5)),
            # Item.Emerald: (Action.Keep, Options(max_quantity=5)),
            # Item.Ruby: (Action.Keep, Options(max_quantity=5)),
            # Item.Diamond: (Action.Keep, Options(max_quantity=5)),

            # Item.FlawlessAmethyst: (Action.Keep, Options(max_quantity=5)),
            # Item.FlawlessTopaz: (Action.Keep, Options(max_quantity=5)),
            # Item.FlawlessSapphire: (Action.Keep, Options(max_quantity=5)),
            # Item.FlawlessEmerald: (Action.Keep, Options(max_quantity=5)),
            # Item.FlawlessRuby: (Action.Keep, Options(max_quantity=5)),
            # Item.FlawlessDiamond: (Action.Keep, Options(max_quantity=5)),

            Item.PerfectAmethyst: Action.Keep,
            Item.PerfectTopaz: Action.Keep,
            Item.PerfectSapphire: Action.Keep,
            Item.PerfectEmerald: Action.Keep,
            Item.PerfectRuby: Action.Keep,
            Item.PerfectDiamond: Action.Keep,
        }

        # If you have an item listed below, it will be identified if it isn't already,
        # and these rules will be applied to it. If any of the rules in the list match
        # the item, the item will be stashed. The rules should be functions that take
        # in a PickitItem and return a boolean.
        self.IdentifiedItems = {
            # Unique Rings
            (Item.Ring, Quality.Unique): [
                lambda item: item.check(Stat.AllSkills, ">=", 1) and item.check(Stat.MaxMana, ">=", 20), # SoJ
                lambda item: item.check(Stat.AllSkills, ">=", 1) and item.check(Stat.LifeSteal, ">=", 3), # BK Ring
                lambda item: item.check(Stat.AbsorbLightningPercent, ">=", 15), # Wisp Projector
                lambda item: item.check(Stat.Dexterity, ">=", 20) and item.check(Stat.AttackRating, ">=", 250), # Raven Frost
                lambda item: item.check(Stat.MagicDamageReduction, ">=", 15), # Dwarf Star
                lambda item: item.check(Stat.MagicFind, ">=", 30) and item.check(Stat.AttackRating, ">=", 75), # Nagel
            ],
            # Unique Amulets
            (Item.Amulet, Quality.Unique): [
                lambda item: item.check(Stat.AllSkills, ">=", 2) and item.check(Stat.AllResist, ">=", 20), # Mara's Kaleidoscope
                lambda item: item.check(Stat.AllSkills, ">=", 1) and item.check(Stat.DeadlyStrikePerLevel, ">=", 1), # Highlord's Wrath
            ],
            # Magic Grand Charms
            (Item.GrandCharm, Quality.Magic): [
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
            # Magic Small Charms
            (Item.SmallCharm, Quality.Magic): [
                lambda item: item.check(Stat.MaxLife, ">=", 20) and (item.check(Stat.FireResist, ">=", 10) or item.check(Stat.LightningResist, ">=", 10)),
                lambda item: item.check(Stat.MagicFind, ">=", 7) and (item.check(Stat.MaxDamage, ">=", 3) or item.check(Stat.FasterHitRecovery, ">=", 5)),
                lambda item: item.check(Stat.AllResist, ">=", 5), # 5@
                lambda item: item.check(Stat.MagicFind, ">=", 7), # 7 MF
                lambda item: item.check(Stat.MaxLife, ">=", 20), # 20 Life
                lambda item: item.check(Stat.MaxLife, ">=", 18) and item.check(Stat.MaxMana, ">=", 17), # 18+ life/17 mana SC
                lambda item: item.check(Stat.MaxLife, ">=", 15) and item.check(Stat.MaxDamage, ">=", 3), # 15+ life/3max SC
                lambda item: item.check(Stat.FasterHitRecovery, ">=", 5) and item.check(Stat.FireResist, ">=", 11), # 5fhr/11fr SC
                lambda item: item.check(Stat.FasterHitRecovery, ">=", 5) and item.check(Stat.AllResist, ">=", 3), # 5fhr/3+@ SC
            ],
            # Magic Jewels
            (Item.Jewel, Quality.Magic): [
                lambda item: item.check(Stat.IncreasedAttackSpeed, ">=", 15) and item.check(Stat.AllResist, ">=", 10), # IAS/@ jewel
                lambda item: item.check(Stat.IncreasedAttackSpeed, ">=", 15) and item.check(Stat.FireResist, ">=", 25), # IAS/FR jewel
                lambda item: item.check(Stat.IncreasedAttackSpeed, ">=", 15) and item.check(Stat.MaxDamage, ">=", 10), # IAS/max jewel
                lambda item: item.check(Stat.IncreasedAttackSpeed, ">=", 15) and item.check(Stat.MaxDamagePercent, ">=", 30), # ED/IAS jewel (I think this is the right stat...)
                lambda item: item.check(Stat.AllResist, ">=", 15), # 15@ jewel
            ],
        }

        # Unidentified unique, set, rare, magic utems (won't ID unless defined in IdentifiedItems)
        self.UnidentifiedItems = {
            # Unique charms, jewelry, jewels
            (Item.Amulet, Quality.Unique): Action.Keep,
            (Item.GrandCharm, Quality.Unique): Action.Keep,
            (Item.Jewel, Quality.Unique): Action.Keep,
            (Item.LargeCharm, Quality.Unique): Action.Keep,
            (Item.Ring, Quality.Unique): Action.Keep,
            (Item.SmallCharm, Quality.Unique): Action.Keep,
            
            # Rare jewelry, jewels
            # (Item.Amulet, Quality.Rare): Action.Keep,
            # (Item.Ring, Quality.Rare): Action.Keep,
            # (Item.Jewel, Quality.Rare): Action.Keep,
            
            # Magic charms, jewels
            (Item.GrandCharm, Quality.Magic): Action.Keep,
            (Item.SmallCharm, Quality.Magic): Action.Keep,
            # (Item.Amulet, Quality.Magic): Action.Keep,
            # (Item.Jewel, Quality.Magic): Action.Keep,
            # (Item.LargeCharm, Quality.Magic): Action.Keep,
            # (Item.Ring, Quality.Magic): Action.Keep,

            # Unique body armor
            (Item.BalrogSkin, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            (Item.DuskShroud, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            (Item.SacredArmor, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            (Item.SerpentskinArmor, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            (Item.TemplarCoat, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            # (Item.AncientArmor, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            # (Item.ChaosArmor, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            # (Item.Cuirass, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            # (Item.DemonhideArmor, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            # (Item.EmbossedPlate, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            # (Item.GhostArmor, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            # (Item.KrakenShell, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            # (Item.MagePlate, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            # (Item.MeshArmor, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            # (Item.OrnatePlate, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            # (Item.RussetArmor, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            # (Item.StuddedLeather, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            # (Item.WireFleece, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            
            # Unique belts
            (Item.MithrilCoil, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            (Item.SpiderwebSash, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            (Item.WarBelt, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            # (Item.BattleBelt, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            # (Item.Belt, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            # (Item.HeavyBelt, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            # (Item.MeshBelt, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            # (Item.Sash, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            # (Item.SharkskinBelt, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            # (Item.VampirefangBelt, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            
            # Unique boots
            (Item.BattleBoots, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            (Item.BoneweaveBoots, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            (Item.MyrmidonGreaves, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            (Item.ScarabshellBoots, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            # (Item.Boots, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            # (Item.DemonhideBoots, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            # (Item.LightPlatedBoots, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            # (Item.MeshBoots, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            # (Item.SharkskinBoots, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            # (Item.WarBoots, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            
            # Unique gloves
            (Item.OgreGauntlets, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            (Item.VampireboneGloves, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            # (Item.BattleGauntlets, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            # (Item.ChainGloves, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            # (Item.DemonhideGloves, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            # (Item.Gauntlets, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            # (Item.HeavyBracers, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            # (Item.HeavyGloves, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            # (Item.LightGauntlets, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            # (Item.SharkskinGloves, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            # (Item.Vambraces, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            # (Item.WarGauntlets, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            
            # Unique helms
            (Item.BoneVisage, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            (Item.Corona, Quality.Unique): (Action.KeepAndNotify, Options(eth = EthOption.Any)),
            (Item.DemonHead, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            (Item.Diadem, Quality.Unique): (Action.KeepAndNotify, Options(eth = EthOption.Any)),
            (Item.GrandCrown, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            (Item.GrimHelm, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            (Item.Shako, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            (Item.SpiredHelm, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            (Item.Tiara, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            # (Item.Armet, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            # (Item.Basinet, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            # (Item.Casque, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            # (Item.DeathMask, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            # (Item.Sallet, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            # (Item.SkullCap, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            # (Item.WarHat, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            # (Item.WingedHelm, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            
            # Unique Barbarian helms
            (Item.SlayerGuard, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            (Item.FuryVisor, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            
            # Unique Druid helms
            (Item.EarthSpirit, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            (Item.SkySpirit, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            # (Item.BloodSpirit, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            # (Item.TotemicMask, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            
            # Unique Necromancer shields
            (Item.SuccubusSkull, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            (Item.BloodlordSkull, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            (Item.HierophantTrophy, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            
            # Unique wands
            (Item.BurntWand, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            (Item.UnearthedWand, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            # (Item.GrimWand, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            # (Item.LichWand, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            # (Item.TombWand, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            
            # Unique shields
            (Item.Monarch, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            (Item.Pavise, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            # (Item.Aegis, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            # (Item.BarbedShield, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            # (Item.BladeBarrier, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            # (Item.Buckler, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            # (Item.Defender, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            # (Item.GrimShield, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            # (Item.Luna, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            # (Item.RoundShield, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            # (Item.Scutum, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            # (Item.TrollNest, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            
            # Unique weapons
            (Item.ArchonStaff, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            (Item.CrypticAxe, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            (Item.EttinAxe, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            (Item.HydraBow, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            (Item.LegendaryMallet, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            (Item.MightyScepter, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            (Item.QuarterStaff, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            (Item.Scourge, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            (Item.Thresher, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            (Item.WingedAxe, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            (Item.WingedKnife, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            # (Item.BoneKnife, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            # (Item.Dagger, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            # (Item.DivineScepter, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            # (Item.ElderStaff, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            # (Item.FlyingAxe, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            # (Item.OgreAxe, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            # (Item.PhaseBlade, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            # (Item.ThunderMaul, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            # (Item.Tulwar, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            
            # Unique Paladin shields
            (Item.GildedShield, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            (Item.ZakarumShield, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            # (Item.DragonShield, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            # (Item.SacredRondache, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            # (Item.Ward, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            
            # Unique Sorceress orbs
            (Item.DimensionalShard, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            (Item.EldritchOrb, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            # (Item.SwirlingCrystal, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            
            # Unique Amazon bows/javelins
            (Item.CeremonialJavelin, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            # (Item.MatriarchalJavelin, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            # (Item.CeremonialBow, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            # (Item.MatriarchalBow, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            
            # Unique Assassin claws
            # (Item.BattleCestus, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            # (Item.GreaterTalons, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            # (Item.WristSword, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            # (Item.FeralClaws, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            
            # Set Items
            # (Item.Amulet, Quality.Set): Action.Keep,
            # (Item.Ring, Quality.Set): Action.Keep,
            
            # Aldur's set
            # (Item.BattleBoots, Quality.Set): Action.Keep,
            # (Item.HuntersGuise, Quality.Set): Action.Keep,
            # (Item.ShadowPlate, Quality.Set): Action.Keep,

            # BK set
            # (Item.MythicalSword, Quality.Set): Action.Keep,
            # (Item.ColossusBlade, Quality.Set): Action.Keep,

            # Griswold's set
            (Item.Caduceus, Quality.Set): Action.Keep,
            # (Item.Corona, Quality.Set): Action.Keep,
            # (Item.OrnatePlate, Quality.Set): Action.Keep,
            # (Item.VortexShield, Quality.Set): Action.Keep,

            # (Item.WingedHelm, Quality.Set): Action.Keep,
            # (Item.RoundShield, Quality.Set): Action.Keep,

            # IK set
            (Item.SacredArmor, Quality.Set): Action.Keep,
            # (Item.AvengerGuard, Quality.Set): Action.Keep,
            # (Item.WarGauntlets, Quality.Set): Action.Keep,
            # (Item.WarBoots, Quality.Set): Action.Keep,
            # (Item.OgreMaul, Quality.Set): Action.Keep,
            # (Item.WarBelt, Quality.Set): Action.Keep,

            # (Item.BrambleMitts, Quality.Set): Action.Keep,

            # Mav's set
            # (Item.GrandMatronBow, Quality.Set): Action.Keep,
            # (Item.Diadem, Quality.Set): Action.Keep,
            # (Item.KrakenShell, Quality.Set): Action.Keep,
            # (Item.BattleGauntlets, Quality.Set): Action.Keep,
            # (Item.SharkskinBelt, Quality.Set): Action.Keep,

            # Nat's set
            # (Item.MeshBoots, Quality.Set): Action.Keep,
            # (Item.LoricatedMail, Quality.Set): Action.Keep,
            # (Item.ScissorsSuwayyah, Quality.Set): Action.Keep,
            # (Item.GrimHelm, Quality.Set): Action.Keep,

            # Tal's set
            (Item.LacqueredPlate, Quality.Set): Action.KeepAndNotify,
            # (Item.SwirlingCrystal, Quality.Set): Action.Keep,
            # (Item.MeshBelt, Quality.Set): Action.Keep,
            # (Item.DeathMask, Quality.Set): Action.Keep,
            
            # Trang's set
            (Item.TrollBelt, Quality.Set): Action.Keep,
            # (Item.HeavyBracers, Quality.Set): Action.Keep,
            # (Item.CantorTrophy, Quality.Set): Action.Keep,
            # (Item.BoneVisage, Quality.Set): Action.Keep,
            # (Item.ChaosArmor, Quality.Set): Action.Keep,
            
        }

        # If you have an item listed below, these rules will be applied to it. If any
        # of the rules in the list match the item, the item will be stashed. The rules
        # should be functions that take in a PickitItem and return a boolean.
        self.NormalItems = {
            # Non-eth Enigma/CoH/Fortitude bases
            Item.ArchonPlate: [lambda item: not item.is_ethereal and (item.sockets in [0, 3, 4]) and item.quality == Quality.Superior],
            Item.DuskShroud: [lambda item: not item.is_ethereal and (item.sockets in [0, 3, 4]) and item.quality == Quality.Superior],
            Item.MagePlate: [lambda item: not item.is_ethereal and (item.sockets in [0, 3]) and item.quality == Quality.Superior],
            
            # Eth items for merc Fortitude/Treachery
            Item.ArchonPlate: [lambda item: item.is_ethereal and (item.sockets in [0, 3, 4]) and item.quality == Quality.Superior],
            Item.LacqueredPlate: [lambda item: item.is_ethereal and (item.sockets in [0, 3, 4]) and item.quality == Quality.Superior],
            Item.SacredArmor: [lambda item: item.is_ethereal and (item.sockets in [0, 3, 4]) and item.quality == Quality.Superior],

            # Eth polearms
            Item.Thresher: [
                lambda item: item.is_ethereal and item.sockets and item.quality <= Quality.Normal and item.sockets in [0, 4],
                lambda item: item.is_ethereal and item.sockets and item.quality == Quality.Superior and item.sockets == 4,
            ],
            Item.GreatPoleaxe: [
                lambda item: item.is_ethereal and item.sockets and item.quality <= Quality.Normal and item.sockets in [0, 4],
                lambda item: item.is_ethereal and item.sockets and item.quality == Quality.Superior and item.sockets == 4,
            ],
            Item.GiantThresher: [
                lambda item: item.is_ethereal and item.sockets and item.quality <= Quality.Normal and item.sockets in [0, 4],
                lambda item: item.is_ethereal and item.sockets and item.quality == Quality.Superior and item.sockets == 4,
            ],
            Item.CrypticAxe: [
                lambda item: item.is_ethereal and item.sockets and item.quality <= Quality.Normal and item.sockets in [0, 4],
                lambda item: item.is_ethereal and item.sockets and item.quality == Quality.Superior and item.sockets == 4,
            ],
            Item.Thresher: [
                lambda item: item.is_ethereal and item.sockets and item.quality <= Quality.Normal and item.sockets in [0, 4],
                lambda item: item.is_ethereal and item.sockets and item.quality == Quality.Superior and item.sockets == 4,
            ],
            Item.ColossusVoulge: [lambda item: item.is_ethereal and item.sockets == 4],

            # Other eth weapons
            Item.ColossusBlade: [lambda item: item.is_ethereal and item.sockets in [0, 6]],
            Item.WarPike: [lambda item: item.is_ethereal and item.sockets in [0, 6]],

            # Non-eth weapons
            Item.ColossusSword: [lambda item: item.sockets == 5 and item.check(Stat.MaxDamagePercent, ">", 0)],
            Item.PhaseBlade: [
                lambda item: item.sockets == 5,
                lambda item: item.sockets == 5 and item.check(Stat.MaxDamagePercent, ">", 0),
                lambda item: item.sockets in [0, 5, 6] and item.check(Stat.MaxDamagePercent, ">=", 15),
            ],
        }

pickit_config = PickitConfig()

print("Loaded default pickit config")
