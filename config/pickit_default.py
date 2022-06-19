from typing import Callable, Union

from pickit.pickit_item import PickitItem
from pickit.item_types import Item, ItemClass, Options, Quality, ItemMode, Flag, Stat, SkillTree, Action, EthOption

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
        (Union[Item, ItemClass], Quality),
        Union[Action, tuple[Action, Options], bool]] = {}

    # Items to identify and determine pickit based on identified stats
    IdentifiedItems: dict[
        (Union[Item, ItemClass], Quality),
        list[Callable[[PickitItem], Union[Action, tuple[Action, Options], bool]]]] = {}

    # These are normal white or grey, eth or non-eth items that can be socketed and/or superior
    NormalItems: dict[
        Union[Item, ItemClass],
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
            # Item.Gold: Action.Keep,
            Item.KeyOfTerror: Action.Keep,
            Item.KeyOfHate: Action.Keep,
            Item.KeyOfDestruction: Action.Keep,
            
            # You can change the max quantity value from 3 to whatever you
            # want. Quantities picked up will be tracked based on the number
            # picked up in the current bot session.
            # Item.TwistedEssenceOfSuffering: (Action.Keep, Options(max_quantity=4)),
            # Item.ChargedEssenceOfHatred: (Action.Keep, Options(max_quantity=4)),
            Item.BurningEssenceOfTerror: (Action.Keep, Options(max_quantity=4)),
            Item.FesteringEssenceOfDestruction: (Action.Keep, Options(max_quantity=4)),

            # # You can change the "Action" to "Action.Keep" to disable a rule,
            # or you can just comment it out by putting a '#' at the beginning of
            # the line, like this:
            # Item.ElRune: (Action.Keep, Options(max_quantity=5)),
            # Item.EldRune: (Action.Keep, Options(max_quantity=5)),
            # Item.TirRune: (Action.Keep, Options(max_quantity=5)),
            # Item.NefRune: (Action.Keep, Options(max_quantity=5)),
            # Item.EthRune: (Action.Keep, Options(max_quantity=5)),
            # Item.IthRune: (Action.Keep, Options(max_quantity=5)),
            # Item.TalRune: (Action.Keep, Options(max_quantity=5)),
            Item.RalRune: (Action.Keep, Options(max_quantity=15)),
            # Item.OrtRune: (Action.Keep, Options(max_quantity=5)),
            # Item.ThulRune: (Action.Keep, Options(max_quantity=5)),
            # Item.AmnRune: (Action.Keep, Options(max_quantity=5)),
            # Item.SolRune: (Action.Keep, Options(max_quantity=10)),
            # Item.ShaelRune: (Action.Keep, Options(max_quantity=5)),
            # Item.DolRune: (Action.Keep, Options(max_quantity=5)),
            # Item.HelRune: (Action.Keep, Options(max_quantity=5)),
            # Item.IoRune: (Action.Keep, Options(max_quantity=5)),
            # Item.LumRune: Action.Keep,
            # Item.KoRune: Action.Keep,
            # Item.FalRune: Action.Keep,
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

            # Item.ChippedTopaz: (Action.Keep, Options(max_quantity=5)),
            # Item.ChippedAmethyst: (Action.Keep, Options(max_quantity=5)),
            # Item.ChippedSapphire: (Action.Keep, Options(max_quantity=5)),
            # Item.ChippedRuby: (Action.Keep, Options(max_quantity=5)),
            # Item.ChippedEmerald: (Action.Keep, Options(max_quantity=5)),
            # Item.ChippedDiamond: (Action.Keep, Options(max_quantity=5)),
            # Item.ChippedSkull: (Action.Keep, Options(max_quantity=5)),

            # Item.FlawedTopaz: (Action.Keep, Options(max_quantity=5)),
            # Item.FlawedAmethyst: (Action.Keep, Options(max_quantity=5)),
            # Item.FlawedSapphire: (Action.Keep, Options(max_quantity=5)),
            # Item.FlawedRuby: (Action.Keep, Options(max_quantity=5)),
            # Item.FlawedEmerald: (Action.Keep, Options(max_quantity=5)),
            # Item.FlawedDiamond: (Action.Keep, Options(max_quantity=5)),
            # Item.FlawedSkull: (Action.Keep, Options(max_quantity=5)),

            # Item.Topaz: (Action.Keep, Options(max_quantity=5)),
            # Item.Amethyst: (Action.Keep, Options(max_quantity=5)),
            # Item.Sapphire: (Action.Keep, Options(max_quantity=5)),
            # Item.Ruby: (Action.Keep, Options(max_quantity=5)),
            # Item.Emerald: (Action.Keep, Options(max_quantity=5)),
            # Item.Diamond: (Action.Keep, Options(max_quantity=5)),
            # Item.Skull: (Action.Keep, Options(max_quantity=5)),

            # Item.FlawlessTopaz: (Action.Keep, Options(max_quantity=5)),
            Item.FlawlessAmethyst: (Action.Keep, Options(max_quantity=30)),
            # Item.FlawlessSapphire: (Action.Keep, Options(max_quantity=5)),
            # Item.FlawlessRuby: (Action.Keep, Options(max_quantity=30)),
            # Item.FlawlessEmerald: (Action.Keep, Options(max_quantity=2)),
            # Item.FlawlessDiamond: (Action.Keep, Options(max_quantity=5)),
            # Item.FlawlessSkull: (Action.Keep, Options(max_quantity=5)),

            Item.PerfectTopaz: Action.Keep,
            Item.PerfectAmethyst: Action.Keep,
            Item.PerfectSapphire: Action.Keep,
            Item.PerfectRuby: Action.Keep,
            Item.PerfectEmerald: Action.Keep,
            Item.PerfectDiamond: Action.Keep,
            Item.PerfectSkull: Action.Keep,
        }

        # If you have an item listed below, it will be identified if it isn't already,
        # and these rules will be applied to it. If any of the rules in the list match
        # the item, the item will be stashed. The rules should be functions that take
        # in a PickitItem and return a boolean.
        self.IdentifiedItems = {
            # Unique Rings
            (Item.Ring, Quality.Unique): [
                lambda item: Action.KeepAndNotify if item.check(Stat.AllSkills, ">=", 1) and item.check(Stat.MaxMana, ">=", 20) else Action.DontKeep, # SoJ
                lambda item: Action.KeepAndNotify if item.check(Stat.AllSkills, ">=", 1) and item.check(Stat.LifeSteal, ">=", 3) else Action.DontKeep, # BK Ring
                lambda item: Action.Keep if item.check(Stat.AbsorbLightningPercent, ">=", 15) else Action.DontKeep, # Wisp Projector
                lambda item: Action.Keep if item.check(Stat.Dexterity, ">=", 20) and item.check(Stat.AttackRating, ">=", 150) else Action.DontKeep, # Raven Frost
                # lambda item: Action.Keep if item.check(Stat.MagicDamageReduction, ">=", 15) else Action.DontKeep, # Dwarf Star
                lambda item: Action.Keep if item.check(Stat.PoisonResist, ">=", 30) and item.check(Stat.NormalDamageReduction, ">=", 11) else Action.DontKeep, # Nature's Peace
                lambda item: Action.Keep if item.check(Stat.MagicFind, ">=", 30) and item.check(Stat.AttackRating, ">=", 75) else Action.DontKeep, # Nagel
            ],
            # Unique Amulets
            (Item.Amulet, Quality.Unique): [
                lambda item: Action.KeepAndNotify if item.check(Stat.AllSkills, ">=", 2) and item.check(Stat.AllResist, ">=", 20) else Action.DontKeep, # Mara's Kaleidoscope
                lambda item: Action.Keep if item.check(Stat.AllSkills, ">=", 1) and item.check(Stat.DeadlyStrikePerLevel, ">=", 1) else Action.DontKeep, # Highlord's Wrath
                lambda item: Action.Keep if item.check(Stat.IronGolemCharges, ">=", 1) or item.check(Stat.Defense, ">=", 300) else Action.DontKeep, # Metalgrid
                # lambda item: item.check(Stat.AllResist, ">=", 1), # Saracen's
                # lambda item: item.check(Stat.Dexterity, ">=", 20), # Cat's Eye
                # lambda item: Action.Keep if item.check(Stat.LightRadius, "==", 4) else Action.DontKeep, # Atma's
            ],
            # Rainbow Facets
            (Item.Jewel, Quality.Unique): [
                lambda item: Action.Keep if item.get(Stat.FireSkillDamage) >= 5 and item.get(Stat.EnemyFireResist) >= 5 else Action.DontKeep,
                lambda item: Action.Keep if item.get(Stat.ColdSkillDamage) >= 5 and item.get(Stat.EnemyColdResist) >= 5 else Action.DontKeep,
                lambda item: Action.Keep if item.get(Stat.LightningSkillDamage) >= 5 and item.get(Stat.EnemyLightningResist) >= 5 else Action.DontKeep,
                lambda item: Action.Keep if item.get(Stat.PoisonSkillDamage) >= 5 and item.get(Stat.EnemyPoisonResist) >= 5 else Action.DontKeep,
            ],
            # Set Amulets
            (Item.Amulet, Quality.Set): [
                # lambda item: Action.Keep if item.check(Stat.LightningResist, "==", 33) else Action.DontKeep, # Tal Rasha's Adjudication
                # lambda item: item.check(Stat.PoisonResist, "==", 30), # Iratha's Collar
                # lambda item: item.check(Stat.LightRadius, "==", 3), # Angelic Wings
            ],
            # Magic Grand Charms
            (Item.GrandCharm, Quality.Magic): [
                lambda item: Action.Keep if item.check(Stat.MaxDamage, ">=", 10) and (item.check(Stat.MaxLife, ">=", 25) or item.check(Stat.FasterHitRecovery, ">=", 12) or item.check(Stat.Strength, ">=", 5)  or item.check(Stat.Dexterity, ">=", 5)) else Action.DontKeep,
                lambda item: Action.Keep if item.check(Stat.MaxDamage, ">=", 9) and (item.check(Stat.MaxLife, ">=", 36) or item.check(Stat.FasterHitRecovery, ">=", 12) or item.check(Stat.Strength, ">=", 5)  or item.check(Stat.Dexterity, ">=", 5)) else Action.DontKeep,
                lambda item: Action.Keep if item.check(Stat.AmazonJavelinAndSpear, ">=", 1) and (item.check(Stat.MaxLife, ">=", 10) or item.check(Stat.FasterHitRecovery, ">=", 12) or item.check(Stat.Strength, ">=", 5)  or item.check(Stat.Dexterity, ">=", 5)) else Action.DontKeep,
                lambda item: Action.Keep if item.check(Stat.NecromancerPoisonAndBone, ">=", 1) and (item.check(Stat.MaxLife, ">=", 20) or item.check(Stat.FasterHitRecovery, ">=", 12) or item.check(Stat.Strength, ">=", 5)  or item.check(Stat.Dexterity, ">=", 5)) else Action.DontKeep,
                lambda item: Action.Keep if item.check(Stat.NecromancerSummoning, ">=", 1) and (item.check(Stat.MaxLife, ">=", 20) or item.check(Stat.FasterHitRecovery, ">=", 12) or item.check(Stat.Strength, ">=", 5)  or item.check(Stat.Dexterity, ">=", 5)) else Action.DontKeep,
                lambda item: Action.Keep if item.check(Stat.BarbarianWarcries, ">=", 1) and (item.check(Stat.MaxLife, ">=", 20) or item.check(Stat.FasterHitRecovery, ">=", 12) or item.check(Stat.Strength, ">=", 5)  or item.check(Stat.Dexterity, ">=", 5)) else Action.DontKeep,
                lambda item: Action.Keep if item.check(Stat.BarbarianWarcries, ">=", 1) and item.check(Stat.GoldFind, ">=", 10) else Action.DontKeep,
                lambda item: Action.Keep if item.check(Stat.DruidElemental, ">=", 1) and (item.check(Stat.MaxLife, ">=", 10) or item.check(Stat.FasterHitRecovery, ">=", 12) or item.check(Stat.Strength, ">=", 5)  or item.check(Stat.Dexterity, ">=", 5)) else Action.DontKeep,
                lambda item: Action.Keep if item.check(Stat.AssassinTraps, ">=", 1) and (item.check(Stat.MaxLife, ">=", 10) or item.check(Stat.FasterHitRecovery, ">=", 12) or item.check(Stat.Strength, ">=", 5)  or item.check(Stat.Dexterity, ">=", 5)) else Action.DontKeep,
                lambda item: Action.Keep if item.check(Stat.PaladinCombatSkills, ">=", 1) and (item.check(Stat.MaxLife, ">=", 10) or item.check(Stat.FasterHitRecovery, ">=", 12) or item.check(Stat.Strength, ">=", 5)  or item.check(Stat.Dexterity, ">=", 5)) else Action.DontKeep,
                lambda item: Action.Keep if item.check(Stat.PaladinOffensiveAuras, ">=", 1) and (item.check(Stat.MaxLife, ">=", 30) or item.check(Stat.FasterHitRecovery, ">=", 12)) else Action.DontKeep,
                lambda item: Action.Keep if item.check(Stat.DruidSummoning, ">=", 1) and (item.check(Stat.MaxLife, ">=", 30) or item.check(Stat.FasterHitRecovery, ">=", 12)) else Action.DontKeep,

                # lambda item: item.check(Stat.AmazonBowAndCrossbow, ">=", 1),
                # lambda item: item.check(Stat.AmazonPassiveAndMagic, ">=", 1),
                # lambda item: item.check(Stat.AmazonJavelinAndSpear, ">=", 1),
                lambda item: item.check(Stat.SorceressFire, ">=", 1),
                lambda item: item.check(Stat.SorceressLightning, ">=", 1),
                lambda item: item.check(Stat.SorceressCold, ">=", 1),
                # lambda item: item.check(Stat.NecromancerCurses, ">=", 1),
                # lambda item: item.check(Stat.NecromancerPoisonAndBone, ">=", 1),
                # lambda item: item.check(Stat.NecromancerSummoning, ">=", 1),
                lambda item: item.check(Stat.PaladinCombatSkills, ">=", 1),
                # lambda item: item.check(Stat.PaladinOffensiveAuras, ">=", 1),
                # lambda item: item.check(Stat.PaladinDefensiveAuras, ">=", 1),
                # lambda item: item.check(Stat.BarbarianCombatSkills, ">=", 1),
                # lambda item: item.check(Stat.BarbarianMasteries, ">=", 1),
                lambda item: item.check(Stat.BarbarianWarcries, ">=", 1),
                # lambda item: item.check(Stat.DruidSummoning, ">=", 1),
                # lambda item: item.check(Stat.DruidShapeShifting, ">=", 1),
                # lambda item: item.check(Stat.DruidElemental, ">=", 1),
                # lambda item: item.check(Stat.AssassinTraps, ">=", 1),
                # lambda item: item.check(Stat.AssassinShadowDisciplines, ">=", 1),
                # lambda item: item.check(Stat.AssassinMartialArts, ">=", 1),
                
                # lambda item: item.check(Stat.MaxDamage, ">=", 10),
                lambda item: item.check(Stat.AllResist, ">=", 15),
                lambda item: item.check(Stat.MaxLife, ">=", 41), # For rerolling
            ],
            # Magic Small Charms
            (Item.SmallCharm, Quality.Magic): [
                lambda item: item.check(Stat.MaxLife, ">=", 10) and (item.check(Stat.FireResist, ">=", 8) or item.check(Stat.LightningResist, ">=", 8)),
                lambda item: item.check(Stat.MaxLife, ">=", 17) and (item.check(Stat.FireResist, ">=", 5) or item.check(Stat.LightningResist, ">=", 5)),
                lambda item: item.check(Stat.MagicFind, ">=", 6) and (item.check(Stat.MaxDamage, ">=", 3) or item.check(Stat.FasterHitRecovery, ">=", 5) or item.check(Stat.AllResist, ">=", 4)),
                lambda item: item.check(Stat.AllResist, ">=", 5), # 5@
                lambda item: item.check(Stat.MagicFind, ">=", 7), # 7 MF
                # lambda item: item.check(Stat.MaxLife, "==", 15), # 15 Life (lvl 17 req)
                lambda item: item.check(Stat.MaxLife, ">=", 20), # 20 Life
                lambda item: item.check(Stat.MaxLife, "==", 15), # 15 Life (LLD/alts)
                lambda item: item.get(Stat.MaxLife) + item.get(Stat.MaxMana) >= 30, # life + mana SC
                lambda item: item.check(Stat.MaxLife, ">=", 10) and item.check(Stat.MaxDamage, ">=", 3), # 10+ life/3max SC
                lambda item: item.check(Stat.FasterHitRecovery, ">=", 5) and item.check(Stat.FireResist, ">=", 6), # 5fhr/fr SC
                lambda item: item.check(Stat.FasterHitRecovery, ">=", 5) and item.check(Stat.LightningResist, ">=", 6), # 5fhr/lr SC
                lambda item: item.check(Stat.FasterHitRecovery, ">=", 5) and item.check(Stat.ColdResist, ">=", 6), # 5fhr/cr SC
                lambda item: item.check(Stat.FasterHitRecovery, ">=", 5) and item.check(Stat.PoisonResist, ">=", 6), # 5fhr/pr SC
                lambda item: item.check(Stat.FasterHitRecovery, ">=", 5) and item.check(Stat.AllResist, ">=", 3), # 5fhr/3+@ SC
                lambda item: item.check(Stat.FasterHitRecovery, ">=", 5) and item.check(Stat.MaxLife, ">=", 5), # 5fhr/5+ life SC
            ],
            # Magic Jewels
            (Item.Jewel, Quality.Magic): [
                lambda item: item.check(Stat.IncreasedAttackSpeed, ">=", 15) and item.check(Stat.AllResist, ">=", 5), # IAS/@ jewel
                lambda item: item.check(Stat.IncreasedAttackSpeed, ">=", 15) and item.check(Stat.FireResist, ">=", 20), # IAS/FR jewel
                lambda item: item.check(Stat.IncreasedAttackSpeed, ">=", 15) and item.check(Stat.MaxDamage, ">=", 5), # IAS/max jewel
                lambda item: item.check(Stat.IncreasedAttackSpeed, ">=", 15) and item.check(Stat.DemonDamagePercent, ">=", 10), # IAS/demon ED jewel
                lambda item: item.check(Stat.IncreasedAttackSpeed, ">=", 15) and item.check(Stat.EnhancedDamage, ">=", 10), # ED/IAS jewel (I think this is the right stat...)
                lambda item: item.check(Stat.AllResist, ">=", 15), # 15@ jewel
                lambda item: item.check(Stat.RequirementPercent, "==", -15) and (item.get(Stat.FireResist) + item.get(Stat.ColdResist) + item.get(Stat.LightningResist)) >= 25,
                lambda item: item.check(Stat.RequirementPercent, "==", -15) and (item.get(Stat.EnhancedDamage) >= 40 or item.get(Stat.MaxDamage) >= 12 or item.get(Stat.FasterHitRecovery) >= 7),
            ],
            # Rare Jewels
            # (Item.Jewel, Quality.Rare): [
            #     lambda item: item.check(Stat.RequirementPercent, "==", -15) and (item.get(Stat.FireResist) + item.get(Stat.ColdResist) + item.get(Stat.LightningResist)) >= 20,
            #     lambda item: item.check(Stat.RequirementPercent, "==", -15) and (item.get(Stat.EnhancedDamage) >= 10 or item.get(Stat.MaxDamage) >= 8 or item.get(Stat.FasterHitRecovery) >= 7),
                
            #     # lambda item: item.get(Stat.Strength) + item.get(Stat.Dexterity) >= 10,
            #     lambda item: item.check(Stat.AllResist, ">=", 8), 
            #     # lambda item: item.check(Stat.MaxDamage, ">=", 10),
            #     lambda item: item.check(Stat.FireResist, ">=", 25),
            #     # lambda item: item.check(Stat.EnhancedDamage, ">=", 20),
            #     # lambda item: item.check(Stat.LightningResist, ">=", 20),
            #     # lambda item: item.check(Stat.FasterHitRecovery, ">=", 7),
            #     # lambda item: item.check(Stat.MaxLife, ">=", 10),
            #     lambda item: item.check(Stat.RequirementPercent, "==", -15),
            # ],

            # Enchantress orbs
            # (ItemClass.SorceressOrbs, Quality.Rare): [
            #     lambda item: Action.KeepAndNotify if item.get(Stat.Enchant) >= 5 else Action.DontKeep,
            # ],
            # (ItemClass.SorceressOrbs, Quality.Magic): [
            #     lambda item: Action.KeepAndNotify if item.get(Stat.Enchant) >= 5 else Action.DontKeep,
            # ],

            # 5 BO Helms
            # (ItemClass.BarbarianHelms, Quality.Rare): [
            #     lambda item: Action.KeepAndNotify if item.get(Stat.BattleOrders) >= 5 else Action.DontKeep,
            # ],
            # (ItemClass.BarbarianHelms, Quality.Magic): [
            #     lambda item: Action.KeepAndNotify if item.get(Stat.BattleOrders) >= 5 else Action.DontKeep,
            # ],
            
            # 5-6 BO helms, only "Arreat style"
            # (Item.AssaultHelmet, Quality.Magic): [lambda item: item.get(Stat.BattleOrders) >= 5 and Action.KeepAndNotify],
            # (Item.AvengerGuard, Quality.Magic): [lambda item: item.get(Stat.BattleOrders) >= 5 and Action.KeepAndNotify],
            # (Item.SlayerGuard, Quality.Magic): [lambda item: item.get(Stat.BattleOrders) >= 5 and Action.KeepAndNotify],
            # (Item.SavageHelmet, Quality.Magic): [lambda item: item.get(Stat.BattleOrders) >= 5 and Action.KeepAndNotify],
            # (Item.AssaultHelmet, Quality.Rare): [lambda item: item.get(Stat.BattleOrders) >= 5 and Action.KeepAndNotify],
            # (Item.AvengerGuard, Quality.Rare): [lambda item: item.get(Stat.BattleOrders) >= 5 and Action.KeepAndNotify],
            # (Item.SlayerGuard, Quality.Rare): [lambda item: item.get(Stat.BattleOrders) >= 5 and Action.KeepAndNotify],
            # (Item.SavageHelmet, Quality.Rare): [lambda item: item.get(Stat.BattleOrders) >= 5 and Action.KeepAndNotify],

            # Rare boots
            # (ItemClass.Boots, Quality.Rare): [
            #     lambda item: item.check(Stat.FireResist, ">=", 15) and item.check(Stat.LightningResist, ">=", 15) and item.check(Stat.ColdResist, ">=", 15),
            #     lambda item: item.check(Stat.FireResist, ">=", 20) and item.check(Stat.LightningResist, ">=", 20) and item.check(Stat.FasterRunWalk, ">=", 20),
            #     lambda item: item.check(Stat.FireResist, ">=", 25) and item.check(Stat.LightningResist, ">=", 25) and item.check(Stat.FasterHitRecovery, ">=", 10),
            #     lambda item: item.check(Stat.FireResist, ">=", 20) and item.check(Stat.LightningResist, ">=", 20) and item.check(Stat.MagicFind, ">=", 25),
            #     lambda item: item.check(Stat.FireResist, ">=", 20) and item.check(Stat.LightningResist, ">=", 20) and item.check(Stat.GoldFind, ">=", 40),
            # ],

            # Rare gloves
            # (ItemClass.Gloves, Quality.Rare): [
            #     lambda item: item.get(Stat.AmazonJavelinAndSpear) + item.get(Stat.AmazonBowAndCrossbow) + item.get(Stat.AssassinMartialArts) >= 2 and item.check(Stat.IncreasedAttackSpeed, ">=", 20),
            # ],

            # Magic amulets
            # (Item.Amulet, Quality.Magic): [
            #     lambda item: item.check(Stat.BarbarianWarcries, ">=", 3),
            #     lambda item: item.check(Stat.SorceressFire, ">=", 3),
            #     lambda item: item.check(Stat.SorceressCold, ">=", 3),
            #     lambda item: item.check(Stat.PaladinCombatSkills, ">=", 3),
            #     lambda item: item.get(Stat.SorceressFire) + item.get(Stat.AddSorceressSkills) >= 2 and item.get(Stat.FasterCastRate) >= 10,
            #     lambda item: item.get(Stat.SorceressCold) + item.get(Stat.AddSorceressSkills) >= 2 and item.get(Stat.FasterCastRate) >= 10,
            #     lambda item: item.get(Stat.SorceressLightning) + item.get(Stat.AddSorceressSkills) >= 2 and item.get(Stat.FasterCastRate) >= 10,
            # ],

            # Rare amulets
            # (Item.Amulet, Quality.Rare): [
            #     lambda item: item.get(Stat.BarbarianWarcries) + item.get(Stat.Barbarian) >= 2 and item.get(Stat.FasterCastRate) >= 10,
            #     lambda item: item.get(Stat.SorceressFire) + item.get(Stat.Sorceress) >= 2 and item.get(Stat.FasterCastRate) >= 10,
            #     lambda item: item.get(Stat.SorceressCold) + item.get(Stat.Sorceress) >= 2 and item.get(Stat.FasterCastRate) >= 10,
            #     lambda item: item.get(Stat.SorceressLightning) + item.get(Stat.Sorceress) >= 2 and item.get(Stat.FasterCastRate) >= 10,
            #     lambda item: item.get(Stat.PaladinCombatSkills) + item.get(Stat.Paladin) >= 2 and item.get(Stat.FasterCastRate) >= 10,
            #     lambda item: item.get(Stat.NecromancerPoisonAndBone) + item.get(Stat.Necromancer) >= 2 and item.get(Stat.FasterCastRate) >= 10,
            #     lambda item: item.get(Stat.TeleportCharges) >= 1, # Teleport charge amulet, the number represents the level of the skill with charges
            # ],

            # Rare rings
            (Item.Ring, Quality.Rare): [
                lambda item: item.get(Stat.FasterCastRate) >= 10 and item.get(Stat.AllResist) >= 10,
                lambda item: item.get(Stat.FasterCastRate) >= 10 and item.get(Stat.Strength) >= 17,
                lambda item: item.get(Stat.FasterCastRate) >= 10 and item.get(Stat.Dexterity) >= 17,
                lambda item: item.get(Stat.FasterCastRate) >= 10 and item.get(Stat.Strength) + item.get(Stat.Dexterity) >= 25,
                lambda item: item.get(Stat.FasterCastRate) >= 10 and item.get(Stat.FireResist) + item.get(Stat.LightningResist) >= 40,
                lambda item: item.get(Stat.FasterCastRate) >= 10 and item.get(Stat.FireResist) >= 20 and (item.get(Stat.MaxLife) + item.get(Stat.MaxMana) >= 60 or item.get(Stat.Strength) + item.get(Stat.Dexterity) >= 10),
                lambda item: item.get(Stat.FasterCastRate) >= 10 and item.get(Stat.LightningResist) >= 20 and (item.get(Stat.MaxLife) + item.get(Stat.MaxMana) >= 60 or item.get(Stat.Strength) + item.get(Stat.Dexterity) >= 10),
                lambda item: item.get(Stat.FasterCastRate) >= 10 and item.get(Stat.MagicFind) >= 12,
                lambda item: item.get(Stat.FasterCastRate) >= 10 and (item.get(Stat.MaxLife) + item.get(Stat.MaxMana)) >= 80,
                lambda item: item.get(Stat.LifeSteal) >= 5 and item.get(Stat.ManaSteal) >= 5,
                # lambda item: item.get(Stat.ManaSteal) >= 6,
                # lambda item: item.get(Stat.LifeSteal) >= 8,
            ],

            # Misc uniques to ID
            (Item.EldritchOrb, Quality.Unique): [lambda item: item.get(Stat.Sorceress) >= 3 and (item.get(Stat.FireSkillDamage) >= 20 or item.get(Stat.LightningSkillDamage) >= 20)], # Only +3 Sorc Eschuta's
            (Item.ChainGloves, Quality.Unique): [lambda item: item.get(Stat.MagicFind) >= 40], # Only 40 MF Chance Guards
            (Item.ScarabshellBoots, Quality.Unique): [lambda item: Action.KeepAndNotify if item.is_ethereal or (item.get(Stat.Strength) + item.get(Stat.Vitality)) >= 30 else Action.DontKeep], # Only 15/15 Treks
            # (Item.BattleBoots, Quality.Set): [lambda item: item.get(Stat.FireResist) >= 50],
            (Item.MightyScepter, Quality.Unique): [lambda item: item.get(Stat.Paladin) >= 3 and item.sockets >= 2],
            # (Item.SwirlingCrystal, Quality.Set): [lambda item: item.get(Stat.FireMastery) >= 2 and item.get(Stat.ColdMastery) >= 2 and item.get(Stat.LightningMastery) >= 2],
            # (Item.MeshBelt, Quality.Set): [lambda item: item.get(Stat.MagicFind) >= 15],
            # (Item.AvengerGuard, Quality.Set): [lambda item: item.get(Stat.MagicFind) >= 40],
            # (Item.OgreMaul, Quality.Set): [lambda item: item.get(Stat.CrushingBlow) >= 40],
            (Item.DemonhideSash, Quality.Unique): [lambda item: item.get(Stat.DamageReduced) >= 15 and item.get(Stat.MagicDamageReduction) >= 15],
            (Item.MithrilCoil, Quality.Unique): [lambda item: item.get(Stat.DamageReduced) >= 15],
            (Item.DuskShroud, Quality.Unique): [
                lambda item: item.get(Stat.Enchant) >= 3,
                lambda item: item.get(Stat.Blizzard) >= 3 and item.get(Stat.ColdSkillDamage) >= 15,
                lambda item: item.get(Stat.Lightning) >= 3 and item.get(Stat.LightningSkillDamage) >= 15,
            ],
            (Item.PhaseBlade, Quality.Unique): [lambda item: item.get(Stat.AllSkills) >= 1], # Azurewrath
            (Item.BalrogSkin, Quality.Unique): [lambda item: item.get(Stat.AllSkills) >= 2], # +2 Arkaine's Valor
            (Item.Scourge, Quality.Unique): [lambda item: item.get(Stat.IncreasedAttackSpeed) == 30], # Stormlash
            (Item.LegendaryMallet, Quality.Unique): [lambda item: item.get(Stat.IncreasedAttackSpeed) == 20], # Schaefer's
            (Item.SlayerGuard, Quality.Unique): [lambda item: item.get(Stat.LifeSteal) >= 6], # Arreat's Face 6% LL
        }

        # Unidentified unique, set, rare, magic utems (won't ID unless defined in IdentifiedItems)
        self.UnidentifiedItems = {
            # Unique charms, jewelry, jewels
            # (Item.GrandCharm, Quality.Unique): Action.Keep,
            # (Item.LargeCharm, Quality.Unique): Action.Keep,
            (Item.SmallCharm, Quality.Unique): Action.Keep,
            (Item.Amulet, Quality.Unique): Action.Keep,
            (Item.Ring, Quality.Unique): Action.Keep,
            (Item.Jewel, Quality.Unique): Action.Keep,
            
            # Rare jewelry, jewels
            # (Item.Amulet, Quality.Rare): Action.Keep,
            # (Item.Ring, Quality.Rare): Action.Keep,
            # (Item.Jewel, Quality.Rare): Action.Keep,
            
            # Magic charms, jewels
            (Item.GrandCharm, Quality.Magic): Action.Keep,
            # (Item.LargeCharm, Quality.Magic): Action.Keep,
            (Item.SmallCharm, Quality.Magic): Action.Keep,
            # (Item.Amulet, Quality.Magic): Action.Keep,
            # (Item.Ring, Quality.Magic): Action.Keep,
            (Item.Jewel, Quality.Magic): Action.Keep,

            # Unique body armor
            # (Item.BalrogSkin, Quality.Unique): (Action.Keep, Options(eth = EthOption.NonEthOnly)),
            # (Item.DuskShroud, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            (Item.SacredArmor, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            # (Item.SerpentskinArmor, Quality.Unique): (Action.Keep, Options(eth = EthOption.NonEthOnly)),
            (Item.TemplarCoat, Quality.Unique): (Action.Keep, Options(eth = EthOption.EthOnly)),
            # (Item.AncientArmor, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            # (Item.ChaosArmor, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            # (Item.Cuirass, Quality.Unique): (Action.Keep, Options(eth = EthOption.EthOnly)),
            # (Item.DemonhideArmor, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            # (Item.EmbossedPlate, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            # (Item.GhostArmor, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            # (Item.KrakenShell, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            # (Item.MagePlate, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            (Item.MeshArmor, Quality.Unique): (Action.Keep, Options(eth = EthOption.EthOnly)),
            # (Item.OrnatePlate, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            (Item.RussetArmor, Quality.Unique): (Action.Keep, Options(eth = EthOption.EthOnly)),
            # (Item.StuddedLeather, Quality.Unique): (Action.Keep, Options(eth = EthOption.EthOnly)),
            # (Item.WireFleece, Quality.Unique): (Action.Keep, Options(eth = EthOption.EthOnly)),
            
            # Unique belts
            # (Item.MithrilCoil, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            (Item.SpiderwebSash, Quality.Unique): (Action.KeepAndNotify, Options(eth = EthOption.Any)),
            (Item.WarBelt, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            # (Item.DemonhideSash, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            # (Item.BattleBelt, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            # (Item.Belt, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            # (Item.HeavyBelt, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            # (Item.MeshBelt, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            # (Item.Sash, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            # (Item.SharkskinBelt, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            # (Item.VampirefangBelt, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            
            # Unique boots
            (Item.BattleBoots, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            # (Item.BoneweaveBoots, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
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
            (Item.GrandCrown, Quality.Unique): (Action.Keep, Options(eth = EthOption.EthOnly)),
            (Item.GrimHelm, Quality.Unique): (Action.Keep, Options(eth = EthOption.EthOnly)),
            (Item.Shako, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            (Item.SpiredHelm, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            (Item.Tiara, Quality.Unique): (Action.Keep, Options(eth = EthOption.EthOnly)),
            # (Item.Armet, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            # (Item.Casque, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            # (Item.Sallet, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            # (Item.SkullCap, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            # (Item.WarHat, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            # (Item.WingedHelm, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            
            # Unique Barbarian helms
            # (Item.SlayerGuard, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            # (Item.FuryVisor, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            
            # Unique Druid helms
            # (Item.EarthSpirit, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            (Item.SkySpirit, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            # (Item.BloodSpirit, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            # (Item.TotemicMask, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            
            # Unique Necromancer shields
            (Item.SuccubusSkull, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            (Item.BloodlordSkull, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            # (Item.HierophantTrophy, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            
            # Unique wands
            # (Item.BurntWand, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)), # Suicide Branch
            (Item.UnearthedWand, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)), # Death's Web
            # (Item.GrimWand, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            # (Item.LichWand, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            # (Item.TombWand, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)), # Arm of King Leoric
            
            # Unique shields
            (Item.Monarch, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            # (Item.Pavise, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
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
            (Item.CrypticAxe, Quality.Unique): (Action.Keep, Options(eth = EthOption.EthOnly)),
            # (Item.EttinAxe, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            (Item.HydraBow, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            # (Item.LegendaryMallet, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            # (Item.MightyScepter, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            # (Item.QuarterStaff, Quality.Unique): (Action.Keep, Options(eth = EthOption.EthOnly)),
            # (Item.Scourge, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            (Item.Thresher, Quality.Unique): (Action.Keep, Options(eth = EthOption.EthOnly)),
            (Item.WingedAxe, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            # (Item.WingedKnife, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            (Item.BattleSword, Quality.Unique): (Action.Keep, Options(eth = EthOption.EthOnly)), 
            # (Item.BoneKnife, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            # (Item.Dagger, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            # (Item.DivineScepter, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            # (Item.ElderStaff, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            # (Item.OgreAxe, Quality.Unique): (Action.Keep, Options(eth = EthOption.EthOnly)),
            # (Item.PhaseBlade, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            # (Item.ThunderMaul, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            # (Item.Tulwar, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            # (Item.LongBow, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            (Item.BattleDart, Quality.Unique): (Action.Keep, Options(eth = EthOption.EthOnly)),
            # (Item.FlyingAxe, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            # (Item.BalrogSpear, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            # (Item.Francisca, Quality.Unique): (Action.Keep, Options(eth = EthOption.EthOnly)),
            
            # Unique Paladin shields
            (Item.GildedShield, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            # (Item.ZakarumShield, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            # (Item.DragonShield, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            # (Item.SacredRondache, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            # (Item.Ward, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            
            # Unique Sorceress orbs
            (Item.DimensionalShard, Quality.Unique): (Action.KeepAndNotify, Options(eth = EthOption.Any)),
            # (Item.EldritchOrb, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            # (Item.SwirlingCrystal, Quality.Unique): (Action.Keep, Options(eth = EthOption.Any)),
            
            # Unique Amazon bows/javelins
            (Item.CeremonialJavelin, Quality.Unique): (Action.Keep, Options(eth = EthOption.EthOnly)),
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

            # Naj's Staff
            # (Item.ElderStaff, Quality.Set): Action.Keep,
            
            # Aldur's set
            # (Item.BattleBoots, Quality.Set): Action.Keep,
            # (Item.HuntersGuise, Quality.Set): Action.Keep,
            # (Item.ShadowPlate, Quality.Set): Action.Keep,

            # BK set
            # (Item.MythicalSword, Quality.Set): Action.Keep,
            # (Item.ColossusBlade, Quality.Set): Action.Keep,

            # Griswold's set
            (Item.Caduceus, Quality.Set): Action.Keep,
            (Item.Corona, Quality.Set): Action.Keep,
            # (Item.OrnatePlate, Quality.Set): Action.Keep,
            (Item.VortexShield, Quality.Set): Action.Keep,

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
            # (Item.TrollBelt, Quality.Set): Action.Keep,
            # (Item.HeavyBracers, Quality.Set): Action.Keep,
            # (Item.CantorTrophy, Quality.Set): Action.Keep,
            # (Item.BoneVisage, Quality.Set): Action.Keep,
            # (Item.ChaosArmor, Quality.Set): Action.Keep,
            
            # Sazabi's Set
            # (Item.Basinet, Quality.Set): Action.Keep,
            (Item.BalrogSkin, Quality.Set): Action.Keep,
            (Item.CrypticSword, Quality.Set): Action.Keep,
            
            # Iratha's Set
            # (Item.LightGauntlets, Quality.Set): Action.Keep,
            # (Item.Crown, Quality.Set): Action.Keep,
            # (Item.HeavyBelt, Quality.Set): Action.Keep,
            
            # # Temp ladder reset rare boots
            # (Item.Boots, Quality.Rare): Action.Keep,
            # (Item.HeavyBoots, Quality.Rare): Action.Keep,
            # (Item.ChainBoots, Quality.Rare): Action.Keep,
            # (Item.LightPlatedBoots, Quality.Rare): Action.Keep,
            # (Item.Greaves, Quality.Rare): Action.Keep,
            # (Item.DemonhideBoots, Quality.Rare): Action.Keep,
            # (Item.SharkskinBoots, Quality.Rare): Action.Keep,
            # (Item.MeshBoots, Quality.Rare): Action.Keep,
            # (Item.WarBoots, Quality.Rare): Action.Keep,
            # (Item.BattleBoots, Quality.Rare): Action.Keep,
            # (Item.WyrmhideBoots, Quality.Rare): Action.Keep,
            # (Item.ScarabshellBoots, Quality.Rare): Action.Keep,

            # # Temp ladder reset rare gloves
            # (Item.LeatherGloves, Quality.Rare): Action.Keep,
            # (Item.HeavyGloves, Quality.Rare): Action.Keep,
            # (Item.ChainGloves, Quality.Rare): Action.Keep,
            # (Item.LightGauntlets, Quality.Rare): Action.Keep,
            # (Item.Gauntlets, Quality.Rare): Action.Keep,
            # (Item.DemonhideGloves, Quality.Rare): Action.Keep,
            # (Item.SharkskinGloves, Quality.Rare): Action.Keep,
            # (Item.HeavyBracers, Quality.Rare): Action.Keep,
            # (Item.BattleGauntlets, Quality.Rare): Action.Keep,
            
        }

        # If you have an item listed below, these rules will be applied to it. If any
        # of the rules in the list match the item, the item will be stashed. The rules
        # should be functions that take in a PickitItem and return a boolean.
        self.NormalItems = {
            # Non-eth Enigma/CoH/Fortitude bases
            Item.MagePlate: [
                lambda item: not item.is_ethereal and (item.sockets in [0, 3]) and item.quality == Quality.Superior,
                lambda item: not item.is_ethereal and item.sockets == 3 and item.quality <= Quality.Superior and item.defense >= 250,
            ],
            
            # Eth items for merc Fortitude/Treachery
            Item.ArchonPlate: [
                lambda item: item.is_ethereal and (item.sockets in [0, 3, 4]) and item.quality <= Quality.Superior and item.defense >= 750,
                lambda item: not item.is_ethereal and (item.sockets in [0, 3, 4]) and item.quality <= Quality.Superior and item.defense >= 500,
            ],
            Item.LacqueredPlate: [lambda item: item.is_ethereal and (item.sockets in [0, 3, 4]) and item.quality <= Quality.Superior and item.defense >= 750],
            Item.SacredArmor: [lambda item: item.is_ethereal and (item.sockets in [0, 3, 4]) and item.quality <= Quality.Superior and item.defense >= 750],
            Item.Wyrmhide: [lambda item: item.is_ethereal and (item.sockets in [0, 3, 4]) and item.quality <= Quality.Superior and item.defense >= 750],
            Item.BalrogSkin: [lambda item: item.is_ethereal and (item.sockets in [0, 3, 4]) and item.quality <= Quality.Superior and item.defense >= 750],
            Item.DuskShroud: [
                lambda item: item.is_ethereal and (item.sockets in [0, 3, 4]) and item.quality <= Quality.Superior and item.defense >= 750,
                lambda item: not item.is_ethereal and (item.sockets in [0, 3, 4]) and item.quality == Quality.Superior,
            ],
            Item.GreatHauberk: [lambda item: item.is_ethereal and (item.sockets in [0, 3, 4]) and item.quality <= Quality.Superior and item.defense >= 750],
            Item.ShadowPlate: [lambda item: item.is_ethereal and (item.sockets in [0, 3, 4]) and item.quality <= Quality.Superior and item.defense >= 750],
            Item.ScarabHusk: [lambda item: item.is_ethereal and (item.sockets in [0, 3, 4]) and item.quality <= Quality.Superior and item.defense >= 750],
            Item.DiamondMail: [lambda item: item.is_ethereal and (item.sockets in [0, 3, 4]) and item.quality <= Quality.Superior and item.defense >= 750],
            Item.LoricatedMail: [lambda item: item.is_ethereal and (item.sockets in [0, 3, 4]) and item.quality <= Quality.Superior and item.defense >= 750],
            Item.Boneweave: [lambda item: item.is_ethereal and (item.sockets in [0, 3, 4]) and item.quality <= Quality.Superior and item.defense >= 750],
            Item.HellforgePlate: [lambda item: item.is_ethereal and (item.sockets in [0, 3, 4]) and item.quality <= Quality.Superior and item.defense >= 750],
            Item.KrakenShell: [lambda item: item.is_ethereal and (item.sockets in [0, 3, 4]) and item.quality <= Quality.Superior and item.defense >= 750],

            # Polearms
            Item.GreatPoleaxe: [
                lambda item: item.is_ethereal and item.quality <= Quality.Normal and item.sockets in [0, 4],
                lambda item: item.is_ethereal and item.quality == Quality.Superior and item.sockets == 4,
            ],
            Item.GiantThresher: [
                lambda item: item.is_ethereal and item.quality <= Quality.Normal and item.sockets in [0, 4],
                lambda item: item.is_ethereal and item.quality == Quality.Superior and item.sockets == 4,
            ],
            Item.CrypticAxe: [
                lambda item: item.is_ethereal and item.quality <= Quality.Normal and item.sockets in [0, 4],
                lambda item: item.is_ethereal and item.quality == Quality.Superior and item.sockets == 4,
            ],
            Item.Thresher: [
                lambda item: item.is_ethereal and item.quality <= Quality.Normal and item.sockets in [0, 4],
                lambda item: item.is_ethereal and item.quality == Quality.Superior and item.sockets == 4,
            ],
            Item.ColossusVoulge: [lambda item: item.is_ethereal and item.sockets in [0, 4]],
            Item.Partizan: [lambda item: item.sockets in [0, 4] and item.is_ethereal], # Worth a lot for LLD (makes a monster insight)

            # Oath bases
            Item.BalrogBlade: [lambda item: item.is_ethereal and item.sockets in [0, 4]],
            # Item.ChampionSword: [lambda item: item.is_ethereal and item.sockets in [0, 4]],
            # Item.HighlandBlade: [lambda item: item.is_ethereal and item.sockets in [0, 4]],
            # Item.TuskSword: [lambda item: item.is_ethereal and item.sockets in [0, 4]],

            # Other eth weapons
            Item.WarPike: [lambda item: item.is_ethereal and item.sockets in [0, 6]],
            Item.Mancatcher: [lambda item: item.is_ethereal and item.sockets in [0, 4, 6]],
            Item.StygianPike: [lambda item: item.is_ethereal and item.sockets in [0, 4]],
            Item.ColossusBlade: [
                lambda item: item.sockets == 5 and item.get(Stat.EnhancedDamage) > 0,
                lambda item: item.is_ethereal and item.sockets in [0, 4, 5, 6],
            ],
            Item.ColossusSword: [
                lambda item: item.sockets == 5 and item.get(Stat.EnhancedDamage) > 0,
                lambda item: item.is_ethereal and item.sockets in [0, 4, 5],
            ],
            Item.PhaseBlade: [
                lambda item: item.sockets == 5,
                lambda item: item.sockets in [0, 5, 6] and item.get(Stat.EnhancedDamage) > 0,
            ],

            # Lawbringer
            Item.MythicalSword: [lambda item: item.is_ethereal and item.sockets in [0, 3]],
            Item.ConquestSword: [lambda item: item.is_ethereal and item.sockets in [0, 3]],
            Item.CrypticSword: [lambda item: item.is_ethereal and item.sockets in [0, 3]],

            # Spirit
            Item.CrystalSword: [lambda item: item.sockets == 5], # Spirit sword, CTA
            # Item.BroadSword: [lambda item: item.sockets == 4], # Spirit sword
            Item.Monarch: [lambda item: item.sockets == 4 or item.sockets in [0, 4] and item.is_ethereal], # Spirit monarch (eth is super good w/ CTA on swap for -10 str req)

            # Elite Pally shields
            Item.SacredTarge: [lambda item: item.sockets in [0, 3, 4] and item.get(Stat.AllResist) >= 20],
            Item.SacredRondache: [lambda item: item.sockets in [0, 3, 4] and item.get(Stat.AllResist) >= 25],
            Item.KurastShield: [lambda item: item.sockets in [0, 3, 4] and item.get(Stat.AllResist) >= 35],
            Item.ZakarumShield: [lambda item: item.sockets in [0, 3, 4] and item.get(Stat.AllResist) >= 35],
            Item.VortexShield: [lambda item: item.sockets in [0, 3, 4] and item.get(Stat.AllResist) >= 35],
            
            # Exceptional Pally shields
            Item.AkaranTarge: [lambda item: item.sockets in [0, 3, 4] and item.get(Stat.AllResist) >= 40],
            Item.AkaranRondache: [lambda item: item.sockets in [0, 3, 4] and item.get(Stat.AllResist) >= 40],
            Item.ProtectorShield: [lambda item: item.sockets in [0, 3, 4] and item.get(Stat.AllResist) >= 40],
            Item.GildedShield: [lambda item: item.sockets in [0, 3, 4] and item.get(Stat.AllResist) >= 40],
            Item.RoyalShield: [lambda item: item.sockets in [0, 3, 4] and item.get(Stat.AllResist) >= 40],

            ItemClass.BarbarianHelms: [
                lambda item: item.sockets in [0, 2, 3] and item.get(Stat.BattleOrders) >= 3, # Wisdom
                lambda item: item.sockets in [0, 2, 3] and item.get(Stat.ThrowingMastery) >= 3, # Wisdom
                lambda item: item.sockets in [0, 2, 3] and item.get(Stat.BattleOrders) >= 3, # Delirium or Wisdom
            ],

            # GG Obsession runeword bases
            Item.WarStaff: [
                lambda item: item.sockets in [0, 5] and (item.get(Stat.Nova) >= 3 or item.get(Stat.Nova) + item.get(Stat.LightningMastery) >= 5),
                lambda item: item.sockets in [0, 5] and (item.get(Stat.Lightning) >= 3 or item.get(Stat.Lightning) + item.get(Stat.LightningMastery) >= 5),
                lambda item: item.sockets in [0, 5] and (item.get(Stat.FireBall) >= 3 or item.get(Stat.FireBall) + item.get(Stat.FireMastery) >= 5),
                lambda item: item.sockets in [0, 5] and item.get(Stat.FrozenOrb) >= 3,
                lambda item: item.sockets in [0, 5] and item.get(Stat.Blizzard) >= 3,
            ],
            Item.RuneStaff: [
                lambda item: item.sockets in [0, 5] and (item.get(Stat.Nova) >= 3 or item.get(Stat.Nova) + item.get(Stat.LightningMastery) >= 5),
                lambda item: item.sockets in [0, 5] and (item.get(Stat.Lightning) >= 3 or item.get(Stat.Lightning) + item.get(Stat.LightningMastery) >= 5),
                lambda item: item.sockets in [0, 5] and (item.get(Stat.FireBall) >= 3 or item.get(Stat.FireBall) + item.get(Stat.FireMastery) >= 5),
                lambda item: item.sockets in [0, 5] and item.get(Stat.FrozenOrb) >= 3,
                lambda item: item.sockets in [0, 5] and item.get(Stat.Blizzard) >= 3,
            ],
            Item.ArchonStaff: [
                lambda item: item.sockets in [0, 5] and (item.get(Stat.Nova) >= 3 or item.get(Stat.Nova) + item.get(Stat.LightningMastery) >= 5),
                lambda item: item.sockets in [0, 5] and (item.get(Stat.Lightning) >= 3 or item.get(Stat.Lightning) + item.get(Stat.LightningMastery) >= 5),
                lambda item: item.sockets in [0, 5] and (item.get(Stat.FireBall) >= 3 or item.get(Stat.FireBall) + item.get(Stat.FireMastery) >= 5),
                lambda item: item.sockets in [0, 5] and item.get(Stat.FrozenOrb) >= 3,
                lambda item: item.sockets in [0, 5] and item.get(Stat.Blizzard) >= 3,
            ],

            # CTA bases w/ +Holy Shield skill for pre-buff
            Item.WarScepter: [lambda item: item.get(Stat.HolyShield) >= 2 and item.sockets in [0, 5]],
            Item.DivineScepter: [lambda item: item.get(Stat.HolyShield) >= 2 and item.sockets in [0, 5]],
            Item.Caduceus: [lambda item: item.get(Stat.HolyShield) >= 2 and item.sockets in [0, 5]],
        }

pickit_config = PickitConfig()
