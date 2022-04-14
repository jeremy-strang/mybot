from enum import Enum
from functools import total_ordering

@total_ordering
class Action(Enum):
    DontKeep = 0
    Keep = 1
    KeepAndNotify = 2

    def _missing_(value):
        if type(value) is int:
            if value < 0: return Action.DontKeep
            elif value > 2: return Action.KeepAndNotify
        elif type(value) is str:
            if value == "Keep" or value =="1": return Action.Keep
            if value == "KeepAndNotify" or value == "2": return Action.KeepAndNotify
        return Action.DontKeep
    
    def __eq__(self, other):
        if self.__class__ is other.__class__: return self.value == other.value
        elif type(other) is int or type(other) is float: return self.value == int(other)
        return NotImplemented

    def __lt__(self, other):
        if self.__class__ is other.__class__: return self.value < other.value
        elif type(other) is int or type(other) is float: return self.value < other
        return NotImplemented
    
    def __le__(self, other):
        if self.__class__ is other.__class__: return self.value <= other.value
        elif type(other) is int or type(other) is float: return self.value <= other
        return NotImplemented
    
    def __gt__(self, other):
        if self.__class__ is other.__class__: return self.value > other.value
        elif type(other) is int or type(other) is float: return self.value > other
        return NotImplemented
    
    def __ge__(self, other):
        if self.__class__ is other.__class__: return self.value >= other.value
        elif type(other) is int or type(other) is float: return self.value >= other
        return NotImplemented
    
    def __int__(self):
        return self.value
    
    def __str__(self):
        return self.name

class EthOption:
    Any = 0
    EthOnly = 1
    NonEthOnly = 2

class Options:
    def __init__(self, eth: EthOption = EthOption.Any, min_defense: int = None, max_quantity: int = None):
        self.eth = eth
        self.min_defense = min_defense
        self.max_quantity = max_quantity

class InventoryPage:
    Inventory = "INVENTORY"
    Equip = "EQUIP"
    Trade = "TRADE"
    Cube = "CUBE"
    Stash = "STASH"
    Belt = "BELT"
    Null = "NULL"

class StashType:
    Body = "Body"
    Personal = "Personal"
    Shared1 = "Shared1"
    Shared2 = "Shared2"
    Shared3 = "Shared3"
    Belt = "Belt"

@total_ordering
class Quality(Enum):
    Inferior = 1
    Normal = 2
    Superior = 3
    Magic = 4
    Set = 5
    Rare = 6
    Unique = 7
    Craft = 8
    Tempered = 9
    
    def __eq__(self, other):
        if self.__class__ is other.__class__: return self.value == other.value
        elif type(other) is int or type(other) is float: return self.value == int(other)
        return NotImplemented
    
    def __hash__(self):
        return self.value
    
    def __int__(self):
        return self.value
    
    def __str__(self):
        return self.name

    def __lt__(self, other):
        if self.__class__ is other.__class__: return self.value < other.value
        elif type(other) is int or type(other) is float: return self.value < other
        return NotImplemented
    
    def __le__(self, other):
        if self.__class__ is other.__class__: return self.value <= other.value
        elif type(other) is int or type(other) is float: return self.value <= other
        return NotImplemented
    
    def __gt__(self, other):
        if self.__class__ is other.__class__: return self.value > other.value
        elif type(other) is int or type(other) is float: return self.value > other
        return NotImplemented
    
    def __ge__(self, other):
        if self.__class__ is other.__class__: return self.value >= other.value
        elif type(other) is int or type(other) is float: return self.value >= other
        return NotImplemented

class ItemMode:
    Stored = "STORED" # Item is in storage (inventory, cube, stash?)
    Equip = "EQUIP" # Item is equippped
    Inbelt = "INBELT" # Item is in belt rows
    OnGround = "ONGROUND" # Item is on ground
    OnCursor = "ONCURSOR" # Item is on cursor
    Dropping = "DROPPING" # Item is being dropped
    Socketed = "SOCKETED" # Item is socketed in another item

class Flag:
    NewItem = "IFLAG_NEWITEM"
    Target = "IFLAG_TARGET"
    Targeting = "IFLAG_TARGETING"
    Deleted = "IFLAG_DELETED"
    Identified = "IFLAG_IDENTIFIED"
    Quantity = "IFLAG_QUANTITY"
    SwitchIn = "IFLAG_SWITCHIN"
    SwitchOut = "IFLAG_SWITCHOUT"
    Broken = "IFLAG_BROKEN"
    Repaired = "IFLAG_REPAIRED"
    Unk1 = "IFLAG_UNK1"
    Socketed = "IFLAG_SOCKETED"
    NoSell = "IFLAG_NOSELL"
    InStore = "IFLAG_INSTORE"
    NoEquip = "IFLAG_NOEQUIP"
    Named = "IFLAG_NAMED"
    IsEar = "IFLAG_ISEAR"
    StartItem = "IFLAG_STARTITEM"
    Unk2 = "IFLAG_UNK2"
    Init = "IFLAG_INIT"
    Unk3 = "IFLAG_UNK3"
    CompactSave = "IFLAG_COMPACTSAVE"
    Ethereal = "IFLAG_ETHEREAL"
    JustSaved = "IFLAG_JUSTSAVED"
    Personalized = "IFLAG_PERSONALIZED"
    LowQuality = "IFLAG_LOWQUALITY"
    RuneWord = "IFLAG_RUNEWORD"
    Item = "IFLAG_ITEM"

class BodyLoc:
    NotEquipped = "NONE" # Not equipped
    Helm = "HEAD" # Helm
    Amulet = "NECK" # Amulet
    BodyArmor = "TORSO" # Body armor
    RightHand = "RARM" # Right-hand
    LeftHand = "LARM" # Left-hand
    RightRing = "RRIN" # Right ring
    LeftRing = "LRIN" # Left ring
    Belt = "BELT" # Belt
    Boots = "FEET" # Boots
    Gloves = "GLOVES" # Gloves
    RightHandOnSwitch = "SWRARM" # Right-hand on switch
    LeftHandOnSwitch = "SWLARM" # Left-hand on switch

class SkillTree:
    AmazonBowAndCrossbow = 0
    AmazonPassiveAndMagic = 1
    AmazonJavelinAndSpear = 2
    SorceressFire = 8
    SorceressLightning = 9
    SorceressCold = 10
    NecromancerCurses = 16
    NecromancerPoisonAndBone = 17
    NecromancerSummoning = 18
    PaladinCombatSkills = 24
    PaladinOffensiveAuras = 25
    PaladinDefensiveAuras = 26
    BarbarianCombatSkills = 32
    BarbarianMasteries = 33
    BarbarianWarcries = 34
    DruidSummoning = 40
    DruidShapeShifting = 41
    DruidElemental = 42
    AssassinTraps = 48
    AssassinShadowDisciplines = 49
    AssassinMartialArts = 50

class Item:
    HandAxe = "HandAxe"
    Axe = "Axe"
    DoubleAxe = "DoubleAxe"
    MilitaryPick = "MilitaryPick"
    WarAxe = "WarAxe"
    LargeAxe = "LargeAxe"
    BroadAxe = "BroadAxe"
    BattleAxe = "BattleAxe"
    GreatAxe = "GreatAxe"
    GiantAxe = "GiantAxe"
    Wand = "Wand"
    YewWand = "YewWand"
    BoneWand = "BoneWand"
    GrimWand = "GrimWand"
    Club = "Club"
    Scepter = "Scepter"
    GrandScepter = "GrandScepter"
    WarScepter = "WarScepter"
    SpikedClub = "SpikedClub"
    Mace = "Mace"
    MorningStar = "MorningStar"
    Flail = "Flail"
    WarHammer = "WarHammer"
    Maul = "Maul"
    GreatMaul = "GreatMaul"
    ShortSword = "ShortSword"
    Scimitar = "Scimitar"
    Sabre = "Sabre"
    Falchion = "Falchion"
    CrystalSword = "CrystalSword"
    BroadSword = "BroadSword"
    LongSword = "LongSword"
    WarSword = "WarSword"
    TwoHandedSword = "TwoHandedSword"
    Claymore = "Claymore"
    GiantSword = "GiantSword"
    BastardSword = "BastardSword"
    Flamberge = "Flamberge"
    GreatSword = "GreatSword"
    Dagger = "Dagger"
    Dirk = "Dirk"
    Kris = "Kris"
    Blade = "Blade"
    ThrowingKnife = "ThrowingKnife"
    ThrowingAxe = "ThrowingAxe"
    BalancedKnife = "BalancedKnife"
    BalancedAxe = "BalancedAxe"
    Javelin = "Javelin"
    Pilum = "Pilum"
    ShortSpear = "ShortSpear"
    Glaive = "Glaive"
    ThrowingSpear = "ThrowingSpear"
    Spear = "Spear"
    Trident = "Trident"
    Brandistock = "Brandistock"
    Spetum = "Spetum"
    Pike = "Pike"
    Bardiche = "Bardiche"
    Voulge = "Voulge"
    Scythe = "Scythe"
    Poleaxe = "Poleaxe"
    Halberd = "Halberd"
    WarScythe = "WarScythe"
    ShortStaff = "ShortStaff"
    LongStaff = "LongStaff"
    GnarledStaff = "GnarledStaff"
    BattleStaff = "BattleStaff"
    WarStaff = "WarStaff"
    ShortBow = "ShortBow"
    HuntersBow = "HuntersBow"
    LongBow = "LongBow"
    CompositeBow = "CompositeBow"
    ShortBattleBow = "ShortBattleBow"
    LongBattleBow = "LongBattleBow"
    ShortWarBow = "ShortWarBow"
    LongWarBow = "LongWarBow"
    LightCrossbow = "LightCrossbow"
    Crossbow = "Crossbow"
    HeavyCrossbow = "HeavyCrossbow"
    RepeatingCrossbow = "RepeatingCrossbow"
    RancidGasPotion = "RancidGasPotion"
    OilPotion = "OilPotion"
    ChokingGasPotion = "ChokingGasPotion"
    ExplodingPotion = "ExplodingPotion"
    StranglingGasPotion = "StranglingGasPotion"
    FulminatingPotion = "FulminatingPotion"
    DecoyGidbinn = "DecoyGidbinn"
    TheGidbinn = "TheGidbinn"
    WirtsLeg = "WirtsLeg"
    HoradricMalus = "HoradricMalus"
    HellforgeHammer = "HellforgeHammer"
    HoradricStaff = "HoradricStaff"
    StaffOfKings = "StaffOfKings"
    Hatchet = "Hatchet"
    Cleaver = "Cleaver"
    TwinAxe = "TwinAxe"
    Crowbill = "Crowbill"
    Naga = "Naga"
    MilitaryAxe = "MilitaryAxe"
    BeardedAxe = "BeardedAxe"
    Tabar = "Tabar"
    GothicAxe = "GothicAxe"
    AncientAxe = "AncientAxe"
    BurntWand = "BurntWand"
    PetrifiedWand = "PetrifiedWand"
    TombWand = "TombWand"
    GraveWand = "GraveWand"
    Cudgel = "Cudgel"
    RuneScepter = "RuneScepter"
    HolyWaterSprinkler = "HolyWaterSprinkler"
    DivineScepter = "DivineScepter"
    BarbedClub = "BarbedClub"
    FlangedMace = "FlangedMace"
    JaggedStar = "JaggedStar"
    Knout = "Knout"
    BattleHammer = "BattleHammer"
    WarClub = "WarClub"
    MartelDeFer = "MartelDeFer"
    Gladius = "Gladius"
    Cutlass = "Cutlass"
    Shamshir = "Shamshir"
    Tulwar = "Tulwar"
    DimensionalBlade = "DimensionalBlade"
    BattleSword = "BattleSword"
    RuneSword = "RuneSword"
    AncientSword = "AncientSword"
    Espandon = "Espandon"
    DacianFalx = "DacianFalx"
    TuskSword = "TuskSword"
    GothicSword = "GothicSword"
    Zweihander = "Zweihander"
    ExecutionerSword = "ExecutionerSword"
    Poignard = "Poignard"
    Rondel = "Rondel"
    Cinquedeas = "Cinquedeas"
    Stiletto = "Stiletto"
    BattleDart = "BattleDart"
    Francisca = "Francisca"
    WarDart = "WarDart"
    Hurlbat = "Hurlbat"
    WarJavelin = "WarJavelin"
    GreatPilum = "GreatPilum"
    Simbilan = "Simbilan"
    Spiculum = "Spiculum"
    Harpoon = "Harpoon"
    WarSpear = "WarSpear"
    Fuscina = "Fuscina"
    WarFork = "WarFork"
    Yari = "Yari"
    Lance = "Lance"
    LochaberAxe = "LochaberAxe"
    Bill = "Bill"
    BattleScythe = "BattleScythe"
    Partizan = "Partizan"
    BecDeCorbin = "BecDeCorbin"
    GrimScythe = "GrimScythe"
    JoStaff = "JoStaff"
    QuarterStaff = "QuarterStaff"
    CedarStaff = "CedarStaff"
    GothicStaff = "GothicStaff"
    RuneStaff = "RuneStaff"
    EdgeBow = "EdgeBow"
    RazorBow = "RazorBow"
    CedarBow = "CedarBow"
    DoubleBow = "DoubleBow"
    ShortSiegeBow = "ShortSiegeBow"
    LargeSiegeBow = "LargeSiegeBow"
    RuneBow = "RuneBow"
    GothicBow = "GothicBow"
    Arbalest = "Arbalest"
    SiegeCrossbow = "SiegeCrossbow"
    Ballista = "Ballista"
    ChuKoNu = "ChuKoNu"
    KhalimsFlail = "KhalimsFlail"
    KhalimsWill = "KhalimsWill"
    Katar = "Katar"
    WristBlade = "WristBlade"
    HatchetHands = "HatchetHands"
    Cestus = "Cestus"
    Claws = "Claws"
    BladeTalons = "BladeTalons"
    ScissorsKatar = "ScissorsKatar"
    Quhab = "Quhab"
    WristSpike = "WristSpike"
    Fascia = "Fascia"
    HandScythe = "HandScythe"
    GreaterClaws = "GreaterClaws"
    GreaterTalons = "GreaterTalons"
    ScissorsQuhab = "ScissorsQuhab"
    Suwayyah = "Suwayyah"
    WristSword = "WristSword"
    WarFist = "WarFist"
    BattleCestus = "BattleCestus"
    FeralClaws = "FeralClaws"
    RunicTalons = "RunicTalons"
    ScissorsSuwayyah = "ScissorsSuwayyah"
    Tomahawk = "Tomahawk"
    SmallCrescent = "SmallCrescent"
    EttinAxe = "EttinAxe"
    WarSpike = "WarSpike"
    BerserkerAxe = "BerserkerAxe"
    FeralAxe = "FeralAxe"
    SilverEdgedAxe = "SilverEdgedAxe"
    Decapitator = "Decapitator"
    ChampionAxe = "ChampionAxe"
    GloriousAxe = "GloriousAxe"
    PolishedWand = "PolishedWand"
    GhostWand = "GhostWand"
    LichWand = "LichWand"
    UnearthedWand = "UnearthedWand"
    Truncheon = "Truncheon"
    MightyScepter = "MightyScepter"
    SeraphRod = "SeraphRod"
    Caduceus = "Caduceus"
    TyrantClub = "TyrantClub"
    ReinforcedMace = "ReinforcedMace"
    DevilStar = "DevilStar"
    Scourge = "Scourge"
    LegendaryMallet = "LegendaryMallet"
    OgreMaul = "OgreMaul"
    ThunderMaul = "ThunderMaul"
    Falcata = "Falcata"
    Ataghan = "Ataghan"
    ElegantBlade = "ElegantBlade"
    HydraEdge = "HydraEdge"
    PhaseBlade = "PhaseBlade"
    ConquestSword = "ConquestSword"
    CrypticSword = "CrypticSword"
    MythicalSword = "MythicalSword"
    LegendSword = "LegendSword"
    HighlandBlade = "HighlandBlade"
    BalrogBlade = "BalrogBlade"
    ChampionSword = "ChampionSword"
    ColossusSword = "ColossusSword"
    ColossusBlade = "ColossusBlade"
    BoneKnife = "BoneKnife"
    MithrilPoint = "MithrilPoint"
    FangedKnife = "FangedKnife"
    LegendSpike = "LegendSpike"
    FlyingKnife = "FlyingKnife"
    FlyingAxe = "FlyingAxe"
    WingedKnife = "WingedKnife"
    WingedAxe = "WingedAxe"
    HyperionJavelin = "HyperionJavelin"
    StygianPilum = "StygianPilum"
    BalrogSpear = "BalrogSpear"
    GhostGlaive = "GhostGlaive"
    WingedHarpoon = "WingedHarpoon"
    HyperionSpear = "HyperionSpear"
    StygianPike = "StygianPike"
    Mancatcher = "Mancatcher"
    GhostSpear = "GhostSpear"
    WarPike = "WarPike"
    OgreAxe = "OgreAxe"
    ColossusVoulge = "ColossusVoulge"
    Thresher = "Thresher"
    CrypticAxe = "CrypticAxe"
    GreatPoleaxe = "GreatPoleaxe"
    GiantThresher = "GiantThresher"
    WalkingStick = "WalkingStick"
    Stalagmite = "Stalagmite"
    ElderStaff = "ElderStaff"
    Shillelagh = "Shillelagh"
    ArchonStaff = "ArchonStaff"
    SpiderBow = "SpiderBow"
    BladeBow = "BladeBow"
    ShadowBow = "ShadowBow"
    GreatBow = "GreatBow"
    DiamondBow = "DiamondBow"
    CrusaderBow = "CrusaderBow"
    WardBow = "WardBow"
    HydraBow = "HydraBow"
    PelletBow = "PelletBow"
    GorgonCrossbow = "GorgonCrossbow"
    ColossusCrossbow = "ColossusCrossbow"
    DemonCrossBow = "DemonCrossBow"
    EagleOrb = "EagleOrb"
    SacredGlobe = "SacredGlobe"
    SmokedSphere = "SmokedSphere"
    ClaspedOrb = "ClaspedOrb"
    JaredsStone = "JaredsStone"
    StagBow = "StagBow"
    ReflexBow = "ReflexBow"
    MaidenSpear = "MaidenSpear"
    MaidenPike = "MaidenPike"
    MaidenJavelin = "MaidenJavelin"
    GlowingOrb = "GlowingOrb"
    CrystallineGlobe = "CrystallineGlobe"
    CloudySphere = "CloudySphere"
    SparklingBall = "SparklingBall"
    SwirlingCrystal = "SwirlingCrystal"
    AshwoodBow = "AshwoodBow"
    CeremonialBow = "CeremonialBow"
    CeremonialSpear = "CeremonialSpear"
    CeremonialPike = "CeremonialPike"
    CeremonialJavelin = "CeremonialJavelin"
    HeavenlyStone = "HeavenlyStone"
    EldritchOrb = "EldritchOrb"
    DemonHeart = "DemonHeart"
    VortexOrb = "VortexOrb"
    DimensionalShard = "DimensionalShard"
    MatriarchalBow = "MatriarchalBow"
    GrandMatronBow = "GrandMatronBow"
    MatriarchalSpear = "MatriarchalSpear"
    MatriarchalPike = "MatriarchalPike"
    MatriarchalJavelin = "MatriarchalJavelin"
    Cap = "Cap"
    SkullCap = "SkullCap"
    Helm = "Helm"
    FullHelm = "FullHelm"
    GreatHelm = "GreatHelm"
    Crown = "Crown"
    Mask = "Mask"
    QuiltedArmor = "QuiltedArmor"
    LeatherArmor = "LeatherArmor"
    HardLeatherArmor = "HardLeatherArmor"
    StuddedLeather = "StuddedLeather"
    RingMail = "RingMail"
    ScaleMail = "ScaleMail"
    ChainMail = "ChainMail"
    BreastPlate = "BreastPlate"
    SplintMail = "SplintMail"
    PlateMail = "PlateMail"
    FieldPlate = "FieldPlate"
    GothicPlate = "GothicPlate"
    FullPlateMail = "FullPlateMail"
    AncientArmor = "AncientArmor"
    LightPlate = "LightPlate"
    Buckler = "Buckler"
    SmallShield = "SmallShield"
    LargeShield = "LargeShield"
    KiteShield = "KiteShield"
    TowerShield = "TowerShield"
    GothicShield = "GothicShield"
    LeatherGloves = "LeatherGloves"
    HeavyGloves = "HeavyGloves"
    ChainGloves = "ChainGloves"
    LightGauntlets = "LightGauntlets"
    Gauntlets = "Gauntlets"
    Boots = "Boots"
    HeavyBoots = "HeavyBoots"
    ChainBoots = "ChainBoots"
    LightPlatedBoots = "LightPlatedBoots"
    Greaves = "Greaves"
    Sash = "Sash"
    LightBelt = "LightBelt"
    Belt = "Belt"
    HeavyBelt = "HeavyBelt"
    PlatedBelt = "PlatedBelt"
    BoneHelm = "BoneHelm"
    BoneShield = "BoneShield"
    SpikedShield = "SpikedShield"
    WarHat = "WarHat"
    Sallet = "Sallet"
    Casque = "Casque"
    Basinet = "Basinet"
    WingedHelm = "WingedHelm"
    GrandCrown = "GrandCrown"
    DeathMask = "DeathMask"
    GhostArmor = "GhostArmor"
    SerpentskinArmor = "SerpentskinArmor"
    DemonhideArmor = "DemonhideArmor"
    TrellisedArmor = "TrellisedArmor"
    LinkedMail = "LinkedMail"
    TigulatedMail = "TigulatedMail"
    MeshArmor = "MeshArmor"
    Cuirass = "Cuirass"
    RussetArmor = "RussetArmor"
    TemplarCoat = "TemplarCoat"
    SharktoothArmor = "SharktoothArmor"
    EmbossedPlate = "EmbossedPlate"
    ChaosArmor = "ChaosArmor"
    OrnatePlate = "OrnatePlate"
    MagePlate = "MagePlate"
    Defender = "Defender"
    RoundShield = "RoundShield"
    Scutum = "Scutum"
    DragonShield = "DragonShield"
    Pavise = "Pavise"
    AncientShield = "AncientShield"
    DemonhideGloves = "DemonhideGloves"
    SharkskinGloves = "SharkskinGloves"
    HeavyBracers = "HeavyBracers"
    BattleGauntlets = "BattleGauntlets"
    WarGauntlets = "WarGauntlets"
    DemonhideBoots = "DemonhideBoots"
    SharkskinBoots = "SharkskinBoots"
    MeshBoots = "MeshBoots"
    BattleBoots = "BattleBoots"
    WarBoots = "WarBoots"
    DemonhideSash = "DemonhideSash"
    SharkskinBelt = "SharkskinBelt"
    MeshBelt = "MeshBelt"
    BattleBelt = "BattleBelt"
    WarBelt = "WarBelt"
    GrimHelm = "GrimHelm"
    GrimShield = "GrimShield"
    BarbedShield = "BarbedShield"
    WolfHead = "WolfHead"
    HawkHelm = "HawkHelm"
    Antlers = "Antlers"
    FalconMask = "FalconMask"
    SpiritMask = "SpiritMask"
    JawboneCap = "JawboneCap"
    FangedHelm = "FangedHelm"
    HornedHelm = "HornedHelm"
    AssaultHelmet = "AssaultHelmet"
    AvengerGuard = "AvengerGuard"
    Targe = "Targe"
    Rondache = "Rondache"
    HeraldicShield = "HeraldicShield"
    AerinShield = "AerinShield"
    CrownShield = "CrownShield"
    PreservedHead = "PreservedHead"
    ZombieHead = "ZombieHead"
    UnravellerHead = "UnravellerHead"
    GargoyleHead = "GargoyleHead"
    DemonHeadShield = "DemonHeadShield"
    Circlet = "Circlet"
    Coronet = "Coronet"
    Tiara = "Tiara"
    Diadem = "Diadem"
    Shako = "Shako"
    Hydraskull = "Hydraskull"
    Armet = "Armet"
    GiantConch = "GiantConch"
    SpiredHelm = "SpiredHelm"
    Corona = "Corona"
    DemonHead = "DemonHead"
    DuskShroud = "DuskShroud"
    Wyrmhide = "Wyrmhide"
    ScarabHusk = "ScarabHusk"
    WireFleece = "WireFleece"
    DiamondMail = "DiamondMail"
    LoricatedMail = "LoricatedMail"
    Boneweave = "Boneweave"
    GreatHauberk = "GreatHauberk"
    BalrogSkin = "BalrogSkin"
    HellforgePlate = "HellforgePlate"
    KrakenShell = "KrakenShell"
    LacqueredPlate = "LacqueredPlate"
    ShadowPlate = "ShadowPlate"
    SacredArmor = "SacredArmor"
    ArchonPlate = "ArchonPlate"
    Heater = "Heater"
    Luna = "Luna"
    Hyperion = "Hyperion"
    Monarch = "Monarch"
    Aegis = "Aegis"
    Ward = "Ward"
    BrambleMitts = "BrambleMitts"
    VampireboneGloves = "VampireboneGloves"
    Vambraces = "Vambraces"
    CrusaderGauntlets = "CrusaderGauntlets"
    OgreGauntlets = "OgreGauntlets"
    WyrmhideBoots = "WyrmhideBoots"
    ScarabshellBoots = "ScarabshellBoots"
    BoneweaveBoots = "BoneweaveBoots"
    MirroredBoots = "MirroredBoots"
    MyrmidonGreaves = "MyrmidonGreaves"
    SpiderwebSash = "SpiderwebSash"
    VampirefangBelt = "VampirefangBelt"
    MithrilCoil = "MithrilCoil"
    TrollBelt = "TrollBelt"
    ColossusGirdle = "ColossusGirdle"
    BoneVisage = "BoneVisage"
    TrollNest = "TrollNest"
    BladeBarrier = "BladeBarrier"
    AlphaHelm = "AlphaHelm"
    GriffonHeaddress = "GriffonHeaddress"
    HuntersGuise = "HuntersGuise"
    SacredFeathers = "SacredFeathers"
    TotemicMask = "TotemicMask"
    JawboneVisor = "JawboneVisor"
    LionHelm = "LionHelm"
    RageMask = "RageMask"
    SavageHelmet = "SavageHelmet"
    SlayerGuard = "SlayerGuard"
    AkaranTarge = "AkaranTarge"
    AkaranRondache = "AkaranRondache"
    ProtectorShield = "ProtectorShield"
    GildedShield = "GildedShield"
    RoyalShield = "RoyalShield"
    MummifiedTrophy = "MummifiedTrophy"
    FetishTrophy = "FetishTrophy"
    SextonTrophy = "SextonTrophy"
    CantorTrophy = "CantorTrophy"
    HierophantTrophy = "HierophantTrophy"
    BloodSpirit = "BloodSpirit"
    SunSpirit = "SunSpirit"
    EarthSpirit = "EarthSpirit"
    SkySpirit = "SkySpirit"
    DreamSpirit = "DreamSpirit"
    CarnageHelm = "CarnageHelm"
    FuryVisor = "FuryVisor"
    DestroyerHelm = "DestroyerHelm"
    ConquerorCrown = "ConquerorCrown"
    GuardianCrown = "GuardianCrown"
    SacredTarge = "SacredTarge"
    SacredRondache = "SacredRondache"
    KurastShield = "KurastShield"
    ZakarumShield = "ZakarumShield"
    VortexShield = "VortexShield"
    MinionSkull = "MinionSkull"
    HellspawnSkull = "HellspawnSkull"
    OverseerSkull = "OverseerSkull"
    SuccubusSkull = "SuccubusSkull"
    BloodlordSkull = "BloodlordSkull"
    Elixir = "Elixir"
    INVALID509 = "INVALID509"
    INVALID510 = "INVALID510"
    INVALID511 = "INVALID511"
    INVALID512 = "INVALID512"
    StaminaPotion = "StaminaPotion"
    AntidotePotion = "AntidotePotion"
    RejuvenationPotion = "RejuvenationPotion"
    FullRejuvenationPotion = "FullRejuvenationPotion"
    ThawingPotion = "ThawingPotion"
    TomeOfTownPortal = "TomeOfTownPortal"
    TomeOfIdentify = "TomeOfIdentify"
    Amulet = "Amulet"
    AmuletOfTheViper = "AmuletOfTheViper"
    Ring = "Ring"
    Gold = "Gold"
    ScrollOfInifuss = "ScrollOfInifuss"
    KeyToTheCairnStones = "KeyToTheCairnStones"
    Arrows = "Arrows"
    Torch = "Torch"
    Bolts = "Bolts"
    ScrollOfTownPortal = "ScrollOfTownPortal"
    ScrollOfIdentify = "ScrollOfIdentify"
    Heart = "Heart"
    Brain = "Brain"
    Jawbone = "Jawbone"
    Eye = "Eye"
    Horn = "Horn"
    Tail = "Tail"
    Flag = "Flag"
    Fang = "Fang"
    Quill = "Quill"
    Soul = "Soul"
    Scalp = "Scalp"
    Spleen = "Spleen"
    Key = "Key"
    TheBlackTowerKey = "TheBlackTowerKey"
    PotionOfLife = "PotionOfLife"
    AJadeFigurine = "AJadeFigurine"
    TheGoldenBird = "TheGoldenBird"
    LamEsensTome = "LamEsensTome"
    HoradricCube = "HoradricCube"
    HoradricScroll = "HoradricScroll"
    MephistosSoulstone = "MephistosSoulstone"
    BookOfSkill = "BookOfSkill"
    KhalimsEye = "KhalimsEye"
    KhalimsHeart = "KhalimsHeart"
    KhalimsBrain = "KhalimsBrain"
    Ear = "Ear"
    ChippedAmethyst = "ChippedAmethyst"
    FlawedAmethyst = "FlawedAmethyst"
    Amethyst = "Amethyst"
    FlawlessAmethyst = "FlawlessAmethyst"
    PerfectAmethyst = "PerfectAmethyst"
    ChippedTopaz = "ChippedTopaz"
    FlawedTopaz = "FlawedTopaz"
    Topaz = "Topaz"
    FlawlessTopaz = "FlawlessTopaz"
    PerfectTopaz = "PerfectTopaz"
    ChippedSapphire = "ChippedSapphire"
    FlawedSapphire = "FlawedSapphire"
    Sapphire = "Sapphire"
    FlawlessSapphire = "FlawlessSapphire"
    PerfectSapphire = "PerfectSapphire"
    ChippedEmerald = "ChippedEmerald"
    FlawedEmerald = "FlawedEmerald"
    Emerald = "Emerald"
    FlawlessEmerald = "FlawlessEmerald"
    PerfectEmerald = "PerfectEmerald"
    ChippedRuby = "ChippedRuby"
    FlawedRuby = "FlawedRuby"
    Ruby = "Ruby"
    FlawlessRuby = "FlawlessRuby"
    PerfectRuby = "PerfectRuby"
    ChippedDiamond = "ChippedDiamond"
    FlawedDiamond = "FlawedDiamond"
    Diamond = "Diamond"
    FlawlessDiamond = "FlawlessDiamond"
    PerfectDiamond = "PerfectDiamond"
    MinorHealingPotion = "MinorHealingPotion"
    LightHealingPotion = "LightHealingPotion"
    HealingPotion = "HealingPotion"
    GreaterHealingPotion = "GreaterHealingPotion"
    SuperHealingPotion = "SuperHealingPotion"
    MinorManaPotion = "MinorManaPotion"
    LightManaPotion = "LightManaPotion"
    ManaPotion = "ManaPotion"
    GreaterManaPotion = "GreaterManaPotion"
    SuperManaPotion = "SuperManaPotion"
    ChippedSkull = "ChippedSkull"
    FlawedSkull = "FlawedSkull"
    Skull = "Skull"
    FlawlessSkull = "FlawlessSkull"
    PerfectSkull = "PerfectSkull"
    Herb = "Herb"
    SmallCharm = "SmallCharm"
    LargeCharm = "LargeCharm"
    GrandCharm = "GrandCharm"
    INVALID606 = "INVALID606"
    INVALID607 = "INVALID607"
    INVALID608 = "INVALID608"
    INVALID609 = "INVALID609"
    ElRune = "ElRune"
    EldRune = "EldRune"
    TirRune = "TirRune"
    NefRune = "NefRune"
    EthRune = "EthRune"
    IthRune = "IthRune"
    TalRune = "TalRune"
    RalRune = "RalRune"
    OrtRune = "OrtRune"
    ThulRune = "ThulRune"
    AmnRune = "AmnRune"
    SolRune = "SolRune"
    ShaelRune = "ShaelRune"
    DolRune = "DolRune"
    HelRune = "HelRune"
    IoRune = "IoRune"
    LumRune = "LumRune"
    KoRune = "KoRune"
    FalRune = "FalRune"
    LemRune = "LemRune"
    PulRune = "PulRune"
    UmRune = "UmRune"
    MalRune = "MalRune"
    IstRune = "IstRune"
    GulRune = "GulRune"
    VexRune = "VexRune"
    OhmRune = "OhmRune"
    LoRune = "LoRune"
    SurRune = "SurRune"
    BerRune = "BerRune"
    JahRune = "JahRune"
    ChamRune = "ChamRune"
    ZodRune = "ZodRune"
    Jewel = "Jewel"
    MalahsPotion = "MalahsPotion"
    ScrollOfKnowledge = "ScrollOfKnowledge"
    ScrollOfResistance = "ScrollOfResistance"
    KeyOfTerror = "KeyOfTerror"
    KeyOfHate = "KeyOfHate"
    KeyOfDestruction = "KeyOfDestruction"
    DiablosHorn = "DiablosHorn"
    BaalsEye = "BaalsEye"
    MephistosBrain = "MephistosBrain"
    TokenofAbsolution = "TokenofAbsolution"
    TwistedEssenceOfSuffering = "TwistedEssenceOfSuffering"
    ChargedEssenceOfHatred = "ChargedEssenceOfHatred"
    BurningEssenceOfTerror = "BurningEssenceOfTerror"
    FesteringEssenceOfDestruction = "FesteringEssenceOfDestruction"
    StandardOfHeroes = "StandardOfHeroes"

class Stat:
    Invalid = "Invalid"
    Strength = "Strength"
    Energy = "Energy"
    Dexterity = "Dexterity"
    Vitality = "Vitality"
    StatPoints = "StatPoints"
    SkillPoints = "SkillPoints"
    Life = "Life"
    MaxLife = "MaxLife"
    Mana = "Mana"
    MaxMana = "MaxMana"
    Stamina = "Stamina"
    MaxStamina = "MaxStamina"
    Level = "Level"
    Experience = "Experience"
    Gold = "Gold"
    StashGold = "StashGold"
    ArmorPercent = "ArmorPercent"
    MaxDamagePercent = "MaxDamagePercent"
    MinDamagePercent = "MinDamagePercent"
    AttackRating = "AttackRating"
    ChanceToBlock = "ChanceToBlock"
    MinDamage = "MinDamage"
    MaxDamage = "MaxDamage"
    SecondMinDamage = "SecondMinDamage"
    SecMaxDamage = "SecMaxDamage"
    DamagePercent = "DamagePercent"
    ManaRecovery = "ManaRecovery"
    ManaRecoveryBonus = "ManaRecoveryBonus"
    StaminaRecoveryBonus = "StaminaRecoveryBonus"
    LastExp = "LastExp"
    NextExp = "NextExp"
    Defense = "Defense"
    DefenseVsMissiles = "DefenseVsMissiles"
    DefenseVsHth = "DefenseVsHth"
    NormalDamageReduction = "NormalDamageReduction"
    MagicDamageReduction = "MagicDamageReduction"
    DamageReduced = "DamageReduced"
    MagicResist = "MagicResist"
    MaxMagicResist = "MaxMagicResist"
    FireResist = "FireResist"
    MaxFireResist = "MaxFireResist"
    LightningResist = "LightningResist"
    MaxLightningResist = "MaxLightningResist"
    ColdResist = "ColdResist"
    MaxColdResist = "MaxColdResist"
    PoisonResist = "PoisonResist"
    MaxPoisonResist = "MaxPoisonResist"
    DamageAura = "DamageAura"
    FireMinDamage = "FireMinDamage"
    FireMaxDamage = "FireMaxDamage"
    LightningMinDamage = "LightningMinDamage"
    LightningMaxDamage = "LightningMaxDamage"
    MagicMinDamage = "MagicMinDamage"
    MagicMaxDamage = "MagicMaxDamage"
    ColdMinDamage = "ColdMinDamage"
    ColdMaxDamage = "ColdMaxDamage"
    ColdLength = "ColdLength"
    PoisonMinDamage = "PoisonMinDamage"
    PoisonMaxDamage = "PoisonMaxDamage"
    PoisonLength = "PoisonLength"
    LifeSteal = "LifeSteal"
    LifeStealMax = "LifeStealMax"
    ManaSteal = "ManaSteal"
    ManaStealMax = "ManaStealMax"
    StaminaDrainMinDamage = "StaminaDrainMinDamage"
    StaminaDrainMaxDamage = "StaminaDrainMaxDamage"
    StunLength = "StunLength"
    VelocityPercent = "VelocityPercent"
    AttackRate = "AttackRate"
    OtherAnimRate = "OtherAnimRate"
    Quantity = "Quantity"
    Value = "Value"
    Durability = "Durability"
    MaxDurability = "MaxDurability"
    HPRegen = "HPRegen"
    MaxDurabilityPercent = "MaxDurabilityPercent"
    MaxHPPercent = "MaxHPPercent"
    MaxManaPercent = "MaxManaPercent"
    AttackerTakesDamage = "AttackerTakesDamage"
    GoldFind = "GoldFind"
    MagicFind = "MagicFind"
    Knockback = "Knockback"
    TimeDuration = "TimeDuration"
    AddClassSkills = "AddClassSkills"
    Unused84 = "Unused84"
    AddExperience = "AddExperience"
    HealAfterKill = "HealAfterKill"
    ReducePrices = "ReducePrices"
    DoubleHerbDuration = "DoubleHerbDuration"
    LightRadius = "LightRadius"
    LightColor = "LightColor"
    RequirementPercent = "RequirementPercent"
    LevelRequire = "LevelRequire"
    IncreasedAttackSpeed = "IncreasedAttackSpeed"
    LevelRequirePercent = "LevelRequirePercent"
    LastBlockFrame = "LastBlockFrame"
    FasterRunWalk = "FasterRunWalk"
    NonClassSkill = "NonClassSkill"
    State = "State"
    FasterHitRecovery = "FasterHitRecovery"
    PlayerCount = "PlayerCount"
    PoisonOverrideLength = "PoisonOverrideLength"
    FasterBlockRate = "FasterBlockRate"
    BypassUndead = "BypassUndead"
    BypassDemons = "BypassDemons"
    FasterCastRate = "FasterCastRate"
    BypassBeasts = "BypassBeasts"
    SingleSkill = "SingleSkill"
    SlainMonstersRestInPeace = "SlainMonstersRestInPeace"
    CurseResistance = "CurseResistance"
    PoisonLengthResist = "PoisonLengthResist"
    NormalDamage = "NormalDamage"
    Howl = "Howl"
    Stupidity = "Stupidity"
    DamageTakenGoesToMana = "DamageTakenGoesToMana"
    IgnoreTargetsAR = "IgnoreTargetsAR"
    FractionalTargetAC = "FractionalTargetAC"
    PreventMonsterHeal = "PreventMonsterHeal"
    HalfFreezeDuration = "HalfFreezeDuration"
    AttackRatingPercent = "AttackRatingPercent"
    DamageTargetAC = "DamageTargetAC"
    DemonDamagePercent = "DemonDamagePercent"
    UndeadDamagePercent = "UndeadDamagePercent"
    DemonAttackRating = "DemonAttackRating"
    UndeadAttackRating = "UndeadAttackRating"
    Throwable = "Throwable"
    ElemSkills = "ElemSkills"
    AllSkills = "AllSkills"
    AttackerTakesLightDamage = "AttackerTakesLightDamage"
    IronMaidenLevel = "IronMaidenLevel"
    LifeTapLevel = "LifeTapLevel"
    ThornsPercent = "ThornsPercent"
    BoneArmor = "BoneArmor"
    BoneArmorMax = "BoneArmorMax"
    Freeze = "Freeze"
    OpenWounds = "OpenWounds"
    CrushingBlow = "CrushingBlow"
    KickDamage = "KickDamage"
    ManaAfterKill = "ManaAfterKill"
    HealAfterDemonKill = "HealAfterDemonKill"
    ExtraBlood = "ExtraBlood"
    DeadlyStrike = "DeadlyStrike"
    AbsorbFirePercent = "AbsorbFirePercent"
    AbsorbFire = "AbsorbFire"
    AbsorbLightningPercent = "AbsorbLightningPercent"
    AbsorbLightning = "AbsorbLightning"
    AbsorbMagicPercent = "AbsorbMagicPercent"
    AbsorbMagic = "AbsorbMagic"
    AbsorbColdPercent = "AbsorbColdPercent"
    AbsorbCold = "AbsorbCold"
    Slow = "Slow"
    Aura = "Aura"
    Indestructible = "Indestructible"
    CannotBeFrozen = "CannotBeFrozen"
    StaminaDrainPercent = "StaminaDrainPercent"
    Reanimate = "Reanimate"
    Pierce = "Pierce"
    MagicAarow = "MagicAarow"
    ExplosiveAarow = "ExplosiveAarow"
    ThrowMinDamage = "ThrowMinDamage"
    ThrowMaxDamage = "ThrowMaxDamage"
    SkillHandofAthena = "SkillHandofAthena"
    SkillStaminaPercent = "SkillStaminaPercent"
    SkillPassiveStaminaPercent = "SkillPassiveStaminaPercent"
    SkillConcentration = "SkillConcentration"
    SkillEnchant = "SkillEnchant"
    SkillPierce = "SkillPierce"
    SkillConviction = "SkillConviction"
    SkillChillingArmor = "SkillChillingArmor"
    SkillFrenzy = "SkillFrenzy"
    SkillDecrepify = "SkillDecrepify"
    SkillArmorPercent = "SkillArmorPercent"
    Alignment = "Alignment"
    Target0 = "Target0"
    Target1 = "Target1"
    GoldLost = "GoldLost"
    ConverisonLevel = "ConverisonLevel"
    ConverisonMaxHP = "ConverisonMaxHP"
    UnitDooverlay = "UnitDooverlay"
    AttackVsMonType = "AttackVsMonType"
    DamageVsMonType = "DamageVsMonType"
    Fade = "Fade"
    ArmorOverridePercent = "ArmorOverridePercent"
    Unused183 = "Unused183"
    Unused184 = "Unused184"
    Unused185 = "Unused185"
    Unused186 = "Unused186"
    Unused187 = "Unused187"
    AddSkillTab = "AddSkillTab"
    Unused189 = "Unused189"
    Unused190 = "Unused190"
    Unused191 = "Unused191"
    Unused192 = "Unused192"
    Unused193 = "Unused193"
    NumSockets = "NumSockets"
    SkillOnAttack = "SkillOnAttack"
    SkillOnKill = "SkillOnKill"
    SkillOnDeath = "SkillOnDeath"
    SkillOnHit = "SkillOnHit"
    SkillOnLevelUp = "SkillOnLevelUp"
    Unused200 = "Unused200"
    SkillOnGetHit = "SkillOnGetHit"
    Unused202 = "Unused202"
    Unused203 = "Unused203"
    ItemChargedSkill = "ItemChargedSkill"
    Unused205 = "Unused205"
    Unused206 = "Unused206"
    Unused207 = "Unused207"
    Unused208 = "Unused208"
    Unused209 = "Unused209"
    Unused210 = "Unused210"
    Unused211 = "Unused211"
    Unused212 = "Unused212"
    Unused213 = "Unused213"
    ArmorPerLevel = "ArmorPerLevel"
    ArmorPercentPerLevel = "ArmorPercentPerLevel"
    LifePerLevel = "LifePerLevel"
    ManaPerLevel = "ManaPerLevel"
    MaxDamagePerLevel = "MaxDamagePerLevel"
    MaxDamagePercentPerLevel = "MaxDamagePercentPerLevel"
    StrengthPerLevel = "StrengthPerLevel"
    DexterityPerLevel = "DexterityPerLevel"
    EnergyPerLevel = "EnergyPerLevel"
    VitalityPerLevel = "VitalityPerLevel"
    AttackRatingPerLevel = "AttackRatingPerLevel"
    AttackRatingPercentPerLevel = "AttackRatingPercentPerLevel"
    ColdDamageMaxPerLevel = "ColdDamageMaxPerLevel"
    FireDamageMaxPerLevel = "FireDamageMaxPerLevel"
    LightningDamageMaxPerLevel = "LightningDamageMaxPerLevel"
    PoisonDamageMaxPerLevel = "PoisonDamageMaxPerLevel"
    ResistColdPerLevel = "ResistColdPerLevel"
    ResistFirePerLevel = "ResistFirePerLevel"
    ResistLightningPerLevel = "ResistLightningPerLevel"
    ResistPoisonPerLevel = "ResistPoisonPerLevel"
    AbsorbColdPerLevel = "AbsorbColdPerLevel"
    AbsorbFirePerLevel = "AbsorbFirePerLevel"
    AbsorbLightningPerLevel = "AbsorbLightningPerLevel"
    AbsorbPoisonPerLevel = "AbsorbPoisonPerLevel"
    ThornsPerLevel = "ThornsPerLevel"
    FindGoldPerLevel = "FindGoldPerLevel"
    MagicFindPerLevel = "MagicFindPerLevel"
    RegenStaminaPerLevel = "RegenStaminaPerLevel"
    StaminaPerLevel = "StaminaPerLevel"
    DamageDemonPerLevel = "DamageDemonPerLevel"
    DamageUndeadPerLevel = "DamageUndeadPerLevel"
    AttackRatingDemonPerLevel = "AttackRatingDemonPerLevel"
    AttackRatingUndeadPerLevel = "AttackRatingUndeadPerLevel"
    CrushingBlowPerLevel = "CrushingBlowPerLevel"
    OpenWoundsPerLevel = "OpenWoundsPerLevel"
    KickDamagePerLevel = "KickDamagePerLevel"
    DeadlyStrikePerLevel = "DeadlyStrikePerLevel"
    FindGemsPerLevel = "FindGemsPerLevel"
    ReplenishDurability = "ReplenishDurability"
    ReplenishQuantity = "ReplenishQuantity"
    ExtraStack = "ExtraStack"
    FindItem = "FindItem"
    SlashDamage = "SlashDamage"
    SlashDamagePercent = "SlashDamagePercent"
    CrushDamage = "CrushDamage"
    CrushDamagePercent = "CrushDamagePercent"
    ThrustDamage = "ThrustDamage"
    ThrustDamagePercent = "ThrustDamagePercent"
    AbsorbSlash = "AbsorbSlash"
    AbsorbCrush = "AbsorbCrush"
    AbsorbThrust = "AbsorbThrust"
    AbsorbSlashPercent = "AbsorbSlashPercent"
    AbsorbCrushPercent = "AbsorbCrushPercent"
    AbsorbThrustPercent = "AbsorbThrustPercent"
    ArmorByTime = "ArmorByTime"
    ArmorPercentByTime = "ArmorPercentByTime"
    LifeByTime = "LifeByTime"
    ManaByTime = "ManaByTime"
    MaxDamageByTime = "MaxDamageByTime"
    MaxDamagePercentByTime = "MaxDamagePercentByTime"
    StrengthByTime = "StrengthByTime"
    DexterityByTime = "DexterityByTime"
    EnergyByTime = "EnergyByTime"
    VitalityByTime = "VitalityByTime"
    AttackRatingByTime = "AttackRatingByTime"
    AttackRatingPercentByTime = "AttackRatingPercentByTime"
    ColdDamageMaxByTime = "ColdDamageMaxByTime"
    FireDamageMaxByTime = "FireDamageMaxByTime"
    LightningDamageMaxByTime = "LightningDamageMaxByTime"
    PoisonDamageMaxByTime = "PoisonDamageMaxByTime"
    ResistColdByTime = "ResistColdByTime"
    ResistFireByTime = "ResistFireByTime"
    ResistLightningByTime = "ResistLightningByTime"
    ResistPoisonByTime = "ResistPoisonByTime"
    AbsorbColdByTime = "AbsorbColdByTime"
    AbsorbFireByTime = "AbsorbFireByTime"
    AbsorbLightningByTime = "AbsorbLightningByTime"
    AbsorbPoisonByTime = "AbsorbPoisonByTime"
    FindGoldByTime = "FindGoldByTime"
    MagicFindByTime = "MagicFindByTime"
    RegenStaminaByTime = "RegenStaminaByTime"
    StaminaByTime = "StaminaByTime"
    DamageDemonByTime = "DamageDemonByTime"
    DamageUndeadByTime = "DamageUndeadByTime"
    AttackRatingDemonByTime = "AttackRatingDemonByTime"
    AttackRatingUndeadByTime = "AttackRatingUndeadByTime"
    CrushingBlowByTime = "CrushingBlowByTime"
    OpenWoundsByTime = "OpenWoundsByTime"
    KickDamageByTime = "KickDamageByTime"
    DeadlyStrikeByTime = "DeadlyStrikeByTime"
    FindGemsByTime = "FindGemsByTime"
    PierceCold = "PierceCold"
    PierceFire = "PierceFire"
    PierceLightning = "PierceLightning"
    PiercePoison = "PiercePoison"
    DamageVsMonster = "DamageVsMonster"
    DamagePercentVsMonster = "DamagePercentVsMonster"
    AttackRatingVsMonster = "AttackRatingVsMonster"
    AttackRatingPercentVsMonster = "AttackRatingPercentVsMonster"
    AcVsMonster = "AcVsMonster"
    AcPercentVsMonster = "AcPercentVsMonster"
    FireLength = "FireLength"
    BurningMin = "BurningMin"
    BurningMax = "BurningMax"
    ProgressiveDamage = "ProgressiveDamage"
    ProgressiveSteal = "ProgressiveSteal"
    ProgressiveOther = "ProgressiveOther"
    ProgressiveFire = "ProgressiveFire"
    ProgressiveCold = "ProgressiveCold"
    ProgressiveLightning = "ProgressiveLightning"
    ExtraCharges = "ExtraCharges"
    ProgressiveAttackRating = "ProgressiveAttackRating"
    PoisonCount = "PoisonCount"
    DamageFrameRate = "DamageFrameRate"
    PierceIdx = "PierceIdx"
    FireSkillDamage = "FireSkillDamage"
    LightningSkillDamage = "LightningSkillDamage"
    ColdSkillDamage = "ColdSkillDamage"
    PoisonSkillDamage = "PoisonSkillDamage"
    EnemyFireResist = "EnemyFireResist"
    EnemyLightningResist = "EnemyLightningResist"
    EnemyColdResist = "EnemyColdResist"
    EnemyPoisonResist = "EnemyPoisonResist"
    PassiveCriticalStrike = "PassiveCriticalStrike"
    PassiveDodge = "PassiveDodge"
    PassiveAvoid = "PassiveAvoid"
    PassiveEvade = "PassiveEvade"
    PassiveWarmth = "PassiveWarmth"
    PassiveMasteryMeleeAttackRating = "PassiveMasteryMeleeAttackRating"
    PassiveMasteryMeleeDamage = "PassiveMasteryMeleeDamage"
    PassiveMasteryMeleeCritical = "PassiveMasteryMeleeCritical"
    PassiveMasteryThrowAttackRating = "PassiveMasteryThrowAttackRating"
    PassiveMasteryThrowDamage = "PassiveMasteryThrowDamage"
    PassiveMasteryThrowCritical = "PassiveMasteryThrowCritical"
    PassiveWeaponBlock = "PassiveWeaponBlock"
    SummonResist = "SummonResist"
    ModifierListSkill = "ModifierListSkill"
    ModifierListLevel = "ModifierListLevel"
    LastSentHPPercent = "LastSentHPPercent"
    SourceUnitType = "SourceUnitType"
    SourceUnitID = "SourceUnitID"
    ShortParam1 = "ShortParam1"
    QuestItemDifficulty = "QuestItemDifficulty"
    PassiveMagicMastery = "PassiveMagicMastery"
    PassiveMagicPierce = "PassiveMagicPierce"
    # NOTE: Below stats are not in the raw game data, this is something computed in PickitItem or in the API
    AllResist = "AllResist" 
    AddDruidSkills = "AddDruidSkills"
    AddBarbarianSkills = "AddBarbarianSkills"
    AddAmazonSkills = "AddAmazonSkills"
    AddPaladinSkills = "AddPaladinSkills"
    AddSorceressSkills = "AddSorceressSkills"
    AddAssassinSkills = "AddAssassinSkills"
    AddNecromancerSkills = "AddNecromancerSkills"

class ItemClass:
    Axes = "Axes"
    Wands = "Wands"
    Clubs = "Clubs"
    Scepters = "Scepters"
    Maces = "Maces"
    Hammers = "Hammers"
    Swords = "Swords"
    Daggers = "Daggers"
    ThrowingKnifes = "ThrowingKnifes"
    ThrowingAxes = "ThrowingAxes"
    Javelins = "Javelins"
    Spears = "Spears"
    Polearms = "Polearms"
    Staves = "Staves"
    Bows = "Bows"
    Crossbows = "Crossbows"
    Helms = "Helms"
    Armors = "Armors"
    Shields = "Shields"
    Gloves = "Gloves"
    Boots = "Boots"
    Belts = "Belts"
    Circlets = "Circlets"
    AssassinKatars = "AssassinKatars"
    SorceressOrbs = "SorceressOrbs"
    AmazonBows = "AmazonBows"
    AmazonSpears = "AmazonSpears"
    AmazonJavelins = "AmazonJavelins"
    DruidHelms = "DruidHelms"
    BarbarianHelms = "BarbarianHelms"
    PaladinShields = "PaladinShields"
    NecromancerShields = "NecromancerShields"

ITEM_CLASSES = {
    Item.HandAxe: ItemClass.Axes,
    Item.Axe: ItemClass.Axes,
    Item.DoubleAxe: ItemClass.Axes,
    Item.MilitaryPick: ItemClass.Axes,
    Item.WarAxe: ItemClass.Axes,
    Item.LargeAxe: ItemClass.Axes,
    Item.BroadAxe: ItemClass.Axes,
    Item.BattleAxe: ItemClass.Axes,
    Item.GreatAxe: ItemClass.Axes,
    Item.GiantAxe: ItemClass.Axes,
    Item.Hatchet: ItemClass.Axes,
    Item.Cleaver: ItemClass.Axes,
    Item.TwinAxe: ItemClass.Axes,
    Item.Crowbill: ItemClass.Axes,
    Item.Naga: ItemClass.Axes,
    Item.MilitaryAxe: ItemClass.Axes,
    Item.BeardedAxe: ItemClass.Axes,
    Item.Tabar: ItemClass.Axes,
    Item.GothicAxe: ItemClass.Axes,
    Item.AncientAxe: ItemClass.Axes,
    Item.Tomahawk: ItemClass.Axes,
    Item.SmallCrescent: ItemClass.Axes,
    Item.EttinAxe: ItemClass.Axes,
    Item.WarSpike: ItemClass.Axes,
    Item.BerserkerAxe: ItemClass.Axes,
    Item.FeralAxe: ItemClass.Axes,
    Item.SilverEdgedAxe: ItemClass.Axes,
    Item.Decapitator: ItemClass.Axes,
    Item.ChampionAxe: ItemClass.Axes,
    Item.GloriousAxe: ItemClass.Axes,
    Item.Wand: ItemClass.Wands,
    Item.YewWand: ItemClass.Wands,
    Item.BoneWand: ItemClass.Wands,
    Item.GrimWand: ItemClass.Wands,
    Item.BurntWand: ItemClass.Wands,
    Item.PetrifiedWand: ItemClass.Wands,
    Item.TombWand: ItemClass.Wands,
    Item.GraveWand: ItemClass.Wands,
    Item.PolishedWand: ItemClass.Wands,
    Item.GhostWand: ItemClass.Wands,
    Item.LichWand: ItemClass.Wands,
    Item.UnearthedWand: ItemClass.Wands,
    Item.Club: ItemClass.Clubs,
    Item.SpikedClub: ItemClass.Clubs,
    Item.Cudgel: ItemClass.Clubs,
    Item.BarbedClub: ItemClass.Clubs,
    Item.Truncheon: ItemClass.Clubs,
    Item.TyrantClub: ItemClass.Clubs,
    Item.Scepter: ItemClass.Scepters,
    Item.GrandScepter: ItemClass.Scepters,
    Item.WarScepter: ItemClass.Scepters,
    Item.RuneScepter: ItemClass.Scepters,
    Item.HolyWaterSprinkler: ItemClass.Scepters,
    Item.DivineScepter: ItemClass.Scepters,
    Item.MightyScepter: ItemClass.Scepters,
    Item.SeraphRod: ItemClass.Scepters,
    Item.Caduceus: ItemClass.Scepters,
    Item.Mace: ItemClass.Maces,
    Item.MorningStar: ItemClass.Maces,
    Item.Flail: ItemClass.Maces,
    Item.FlangedMace: ItemClass.Maces,
    Item.JaggedStar: ItemClass.Maces,
    Item.Knout: ItemClass.Maces,
    Item.ReinforcedMace: ItemClass.Maces,
    Item.DevilStar: ItemClass.Maces,
    Item.Scourge: ItemClass.Maces,
    Item.WarHammer: ItemClass.Hammers,
    Item.Maul: ItemClass.Hammers,
    Item.GreatMaul: ItemClass.Hammers,
    Item.BattleHammer: ItemClass.Hammers,
    Item.WarClub: ItemClass.Hammers,
    Item.MartelDeFer: ItemClass.Hammers,
    Item.LegendaryMallet: ItemClass.Hammers,
    Item.OgreMaul: ItemClass.Hammers,
    Item.ThunderMaul: ItemClass.Hammers,
    Item.ShortSword: ItemClass.Swords,
    Item.Scimitar: ItemClass.Swords,
    Item.Sabre: ItemClass.Swords,
    Item.Falchion: ItemClass.Swords,
    Item.CrystalSword: ItemClass.Swords,
    Item.BroadSword: ItemClass.Swords,
    Item.LongSword: ItemClass.Swords,
    Item.WarSword: ItemClass.Swords,
    Item.TwoHandedSword: ItemClass.Swords,
    Item.Claymore: ItemClass.Swords,
    Item.GiantSword: ItemClass.Swords,
    Item.BastardSword: ItemClass.Swords,
    Item.Flamberge: ItemClass.Swords,
    Item.GreatSword: ItemClass.Swords,
    Item.Gladius: ItemClass.Swords,
    Item.Cutlass: ItemClass.Swords,
    Item.Shamshir: ItemClass.Swords,
    Item.Tulwar: ItemClass.Swords,
    Item.DimensionalBlade: ItemClass.Swords,
    Item.BattleSword: ItemClass.Swords,
    Item.RuneSword: ItemClass.Swords,
    Item.AncientSword: ItemClass.Swords,
    Item.Espandon: ItemClass.Swords,
    Item.DacianFalx: ItemClass.Swords,
    Item.TuskSword: ItemClass.Swords,
    Item.GothicSword: ItemClass.Swords,
    Item.Zweihander: ItemClass.Swords,
    Item.ExecutionerSword: ItemClass.Swords,
    Item.Falcata: ItemClass.Swords,
    Item.Ataghan: ItemClass.Swords,
    Item.ElegantBlade: ItemClass.Swords,
    Item.HydraEdge: ItemClass.Swords,
    Item.PhaseBlade: ItemClass.Swords,
    Item.ConquestSword: ItemClass.Swords,
    Item.CrypticSword: ItemClass.Swords,
    Item.MythicalSword: ItemClass.Swords,
    Item.LegendSword: ItemClass.Swords,
    Item.HighlandBlade: ItemClass.Swords,
    Item.BalrogBlade: ItemClass.Swords,
    Item.ChampionSword: ItemClass.Swords,
    Item.ColossusSword: ItemClass.Swords,
    Item.ColossusBlade: ItemClass.Swords,
    Item.Dagger: ItemClass.Daggers,
    Item.Dirk: ItemClass.Daggers,
    Item.Kris: ItemClass.Daggers,
    Item.Blade: ItemClass.Daggers,
    Item.Poignard: ItemClass.Daggers,
    Item.Rondel: ItemClass.Daggers,
    Item.Cinquedeas: ItemClass.Daggers,
    Item.Stiletto: ItemClass.Daggers,
    Item.BoneKnife: ItemClass.Daggers,
    Item.MithrilPoint: ItemClass.Daggers,
    Item.FangedKnife: ItemClass.Daggers,
    Item.LegendSpike: ItemClass.Daggers,
    Item.ThrowingKnife: ItemClass.ThrowingKnifes,
    Item.BalancedKnife: ItemClass.ThrowingKnifes,
    Item.BattleDart: ItemClass.ThrowingKnifes,
    Item.WarDart: ItemClass.ThrowingKnifes,
    Item.FlyingKnife: ItemClass.ThrowingKnifes,
    Item.WingedKnife: ItemClass.ThrowingKnifes,
    Item.ThrowingAxe: ItemClass.ThrowingAxes,
    Item.BalancedAxe: ItemClass.ThrowingAxes,
    Item.Francisca: ItemClass.ThrowingAxes,
    Item.Hurlbat: ItemClass.ThrowingAxes,
    Item.FlyingAxe: ItemClass.ThrowingAxes,
    Item.WingedAxe: ItemClass.ThrowingAxes,
    Item.Javelin: ItemClass.Javelins,
    Item.Pilum: ItemClass.Javelins,
    Item.ShortSpear: ItemClass.Javelins,
    Item.Glaive: ItemClass.Javelins,
    Item.ThrowingSpear: ItemClass.Javelins,
    Item.WarJavelin: ItemClass.Javelins,
    Item.GreatPilum: ItemClass.Javelins,
    Item.Simbilan: ItemClass.Javelins,
    Item.Spiculum: ItemClass.Javelins,
    Item.Harpoon: ItemClass.Javelins,
    Item.HyperionJavelin: ItemClass.Javelins,
    Item.StygianPilum: ItemClass.Javelins,
    Item.BalrogSpear: ItemClass.Javelins,
    Item.GhostGlaive: ItemClass.Javelins,
    Item.WingedHarpoon: ItemClass.Javelins,
    Item.Spear: ItemClass.Spears,
    Item.Trident: ItemClass.Spears,
    Item.Brandistock: ItemClass.Spears,
    Item.Spetum: ItemClass.Spears,
    Item.Pike: ItemClass.Spears,
    Item.WarSpear: ItemClass.Spears,
    Item.Fuscina: ItemClass.Spears,
    Item.WarFork: ItemClass.Spears,
    Item.Yari: ItemClass.Spears,
    Item.Lance: ItemClass.Spears,
    Item.HyperionSpear: ItemClass.Spears,
    Item.StygianPike: ItemClass.Spears,
    Item.Mancatcher: ItemClass.Spears,
    Item.GhostSpear: ItemClass.Spears,
    Item.WarPike: ItemClass.Spears,
    Item.Bardiche: ItemClass.Polearms,
    Item.Voulge: ItemClass.Polearms,
    Item.Scythe: ItemClass.Polearms,
    Item.Poleaxe: ItemClass.Polearms,
    Item.Halberd: ItemClass.Polearms,
    Item.WarScythe: ItemClass.Polearms,
    Item.LochaberAxe: ItemClass.Polearms,
    Item.Bill: ItemClass.Polearms,
    Item.BattleScythe: ItemClass.Polearms,
    Item.Partizan: ItemClass.Polearms,
    Item.BecDeCorbin: ItemClass.Polearms,
    Item.GrimScythe: ItemClass.Polearms,
    Item.OgreAxe: ItemClass.Polearms,
    Item.ColossusVoulge: ItemClass.Polearms,
    Item.Thresher: ItemClass.Polearms,
    Item.CrypticAxe: ItemClass.Polearms,
    Item.GreatPoleaxe: ItemClass.Polearms,
    Item.GiantThresher: ItemClass.Polearms,
    Item.ShortStaff: ItemClass.Staves,
    Item.LongStaff: ItemClass.Staves,
    Item.GnarledStaff: ItemClass.Staves,
    Item.BattleStaff: ItemClass.Staves,
    Item.WarStaff: ItemClass.Staves,
    Item.JoStaff: ItemClass.Staves,
    Item.QuarterStaff: ItemClass.Staves,
    Item.CedarStaff: ItemClass.Staves,
    Item.GothicStaff: ItemClass.Staves,
    Item.RuneStaff: ItemClass.Staves,
    Item.WalkingStick: ItemClass.Staves,
    Item.Stalagmite: ItemClass.Staves,
    Item.ElderStaff: ItemClass.Staves,
    Item.Shillelagh: ItemClass.Staves,
    Item.ArchonStaff: ItemClass.Staves,
    Item.ShortBow: ItemClass.Bows,
    Item.HuntersBow: ItemClass.Bows,
    Item.LongBow: ItemClass.Bows,
    Item.CompositeBow: ItemClass.Bows,
    Item.ShortBattleBow: ItemClass.Bows,
    Item.LongBattleBow: ItemClass.Bows,
    Item.ShortWarBow: ItemClass.Bows,
    Item.LongWarBow: ItemClass.Bows,
    Item.EdgeBow: ItemClass.Bows,
    Item.RazorBow: ItemClass.Bows,
    Item.CedarBow: ItemClass.Bows,
    Item.DoubleBow: ItemClass.Bows,
    Item.ShortSiegeBow: ItemClass.Bows,
    Item.LargeSiegeBow: ItemClass.Bows,
    Item.RuneBow: ItemClass.Bows,
    Item.GothicBow: ItemClass.Bows,
    Item.SpiderBow: ItemClass.Bows,
    Item.BladeBow: ItemClass.Bows,
    Item.ShadowBow: ItemClass.Bows,
    Item.GreatBow: ItemClass.Bows,
    Item.DiamondBow: ItemClass.Bows,
    Item.CrusaderBow: ItemClass.Bows,
    Item.WardBow: ItemClass.Bows,
    Item.HydraBow: ItemClass.Bows,
    Item.LightCrossbow: ItemClass.Crossbows,
    Item.Crossbow: ItemClass.Crossbows,
    Item.HeavyCrossbow: ItemClass.Crossbows,
    Item.RepeatingCrossbow: ItemClass.Crossbows,
    Item.Arbalest: ItemClass.Crossbows,
    Item.SiegeCrossbow: ItemClass.Crossbows,
    Item.Ballista: ItemClass.Crossbows,
    Item.ChuKoNu: ItemClass.Crossbows,
    Item.PelletBow: ItemClass.Crossbows,
    Item.GorgonCrossbow: ItemClass.Crossbows,
    Item.ColossusCrossbow: ItemClass.Crossbows,
    Item.DemonCrossBow: ItemClass.Crossbows,
    Item.Cap: ItemClass.Helms,
    Item.SkullCap: ItemClass.Helms,
    Item.Helm: ItemClass.Helms,
    Item.FullHelm: ItemClass.Helms,
    Item.GreatHelm: ItemClass.Helms,
    Item.Crown: ItemClass.Helms,
    Item.Mask: ItemClass.Helms,
    Item.BoneHelm: ItemClass.Helms,
    Item.WarHat: ItemClass.Helms,
    Item.Sallet: ItemClass.Helms,
    Item.Casque: ItemClass.Helms,
    Item.Basinet: ItemClass.Helms,
    Item.WingedHelm: ItemClass.Helms,
    Item.GrandCrown: ItemClass.Helms,
    Item.DeathMask: ItemClass.Helms,
    Item.GrimHelm: ItemClass.Helms,
    Item.Shako: ItemClass.Helms,
    Item.Hydraskull: ItemClass.Helms,
    Item.Armet: ItemClass.Helms,
    Item.GiantConch: ItemClass.Helms,
    Item.SpiredHelm: ItemClass.Helms,
    Item.Corona: ItemClass.Helms,
    Item.DemonHead: ItemClass.Helms,
    Item.BoneVisage: ItemClass.Helms,
    Item.QuiltedArmor: ItemClass.Armors,
    Item.LeatherArmor: ItemClass.Armors,
    Item.HardLeatherArmor: ItemClass.Armors,
    Item.StuddedLeather: ItemClass.Armors,
    Item.RingMail: ItemClass.Armors,
    Item.ScaleMail: ItemClass.Armors,
    Item.ChainMail: ItemClass.Armors,
    Item.BreastPlate: ItemClass.Armors,
    Item.SplintMail: ItemClass.Armors,
    Item.PlateMail: ItemClass.Armors,
    Item.FieldPlate: ItemClass.Armors,
    Item.GothicPlate: ItemClass.Armors,
    Item.FullPlateMail: ItemClass.Armors,
    Item.AncientArmor: ItemClass.Armors,
    Item.LightPlate: ItemClass.Armors,
    Item.GhostArmor: ItemClass.Armors,
    Item.SerpentskinArmor: ItemClass.Armors,
    Item.DemonhideArmor: ItemClass.Armors,
    Item.TrellisedArmor: ItemClass.Armors,
    Item.LinkedMail: ItemClass.Armors,
    Item.TigulatedMail: ItemClass.Armors,
    Item.MeshArmor: ItemClass.Armors,
    Item.Cuirass: ItemClass.Armors,
    Item.RussetArmor: ItemClass.Armors,
    Item.TemplarCoat: ItemClass.Armors,
    Item.SharktoothArmor: ItemClass.Armors,
    Item.EmbossedPlate: ItemClass.Armors,
    Item.ChaosArmor: ItemClass.Armors,
    Item.OrnatePlate: ItemClass.Armors,
    Item.MagePlate: ItemClass.Armors,
    Item.DuskShroud: ItemClass.Armors,
    Item.Wyrmhide: ItemClass.Armors,
    Item.ScarabHusk: ItemClass.Armors,
    Item.WireFleece: ItemClass.Armors,
    Item.DiamondMail: ItemClass.Armors,
    Item.LoricatedMail: ItemClass.Armors,
    Item.Boneweave: ItemClass.Armors,
    Item.GreatHauberk: ItemClass.Armors,
    Item.BalrogSkin: ItemClass.Armors,
    Item.HellforgePlate: ItemClass.Armors,
    Item.KrakenShell: ItemClass.Armors,
    Item.LacqueredPlate: ItemClass.Armors,
    Item.ShadowPlate: ItemClass.Armors,
    Item.SacredArmor: ItemClass.Armors,
    Item.ArchonPlate: ItemClass.Armors,
    Item.Buckler: ItemClass.Shields,
    Item.SmallShield: ItemClass.Shields,
    Item.LargeShield: ItemClass.Shields,
    Item.KiteShield: ItemClass.Shields,
    Item.TowerShield: ItemClass.Shields,
    Item.GothicShield: ItemClass.Shields,
    Item.BoneShield: ItemClass.Shields,
    Item.SpikedShield: ItemClass.Shields,
    Item.Defender: ItemClass.Shields,
    Item.RoundShield: ItemClass.Shields,
    Item.Scutum: ItemClass.Shields,
    Item.DragonShield: ItemClass.Shields,
    Item.Pavise: ItemClass.Shields,
    Item.AncientShield: ItemClass.Shields,
    Item.GrimShield: ItemClass.Shields,
    Item.BarbedShield: ItemClass.Shields,
    Item.Heater: ItemClass.Shields,
    Item.Luna: ItemClass.Shields,
    Item.Hyperion: ItemClass.Shields,
    Item.Monarch: ItemClass.Shields,
    Item.Aegis: ItemClass.Shields,
    Item.Ward: ItemClass.Shields,
    Item.TrollNest: ItemClass.Shields,
    Item.BladeBarrier: ItemClass.Shields,
    Item.LeatherGloves: ItemClass.Gloves,
    Item.HeavyGloves: ItemClass.Gloves,
    Item.ChainGloves: ItemClass.Gloves,
    Item.LightGauntlets: ItemClass.Gloves,
    Item.Gauntlets: ItemClass.Gloves,
    Item.DemonhideGloves: ItemClass.Gloves,
    Item.SharkskinGloves: ItemClass.Gloves,
    Item.HeavyBracers: ItemClass.Gloves,
    Item.BattleGauntlets: ItemClass.Gloves,
    Item.WarGauntlets: ItemClass.Gloves,
    Item.BrambleMitts: ItemClass.Gloves,
    Item.VampireboneGloves: ItemClass.Gloves,
    Item.Vambraces: ItemClass.Gloves,
    Item.CrusaderGauntlets: ItemClass.Gloves,
    Item.OgreGauntlets: ItemClass.Gloves,
    Item.Boots: ItemClass.Boots,
    Item.HeavyBoots: ItemClass.Boots,
    Item.ChainBoots: ItemClass.Boots,
    Item.LightPlatedBoots: ItemClass.Boots,
    Item.Greaves: ItemClass.Boots,
    Item.DemonhideBoots: ItemClass.Boots,
    Item.SharkskinBoots: ItemClass.Boots,
    Item.MeshBoots: ItemClass.Boots,
    Item.BattleBoots: ItemClass.Boots,
    Item.WarBoots: ItemClass.Boots,
    Item.WyrmhideBoots: ItemClass.Boots,
    Item.ScarabshellBoots: ItemClass.Boots,
    Item.BoneweaveBoots: ItemClass.Boots,
    Item.MirroredBoots: ItemClass.Boots,
    Item.MyrmidonGreaves: ItemClass.Boots,
    Item.Sash: ItemClass.Belts,
    Item.LightBelt: ItemClass.Belts,
    Item.Belt: ItemClass.Belts,
    Item.HeavyBelt: ItemClass.Belts,
    Item.PlatedBelt: ItemClass.Belts,
    Item.DemonhideSash: ItemClass.Belts,
    Item.SharkskinBelt: ItemClass.Belts,
    Item.MeshBelt: ItemClass.Belts,
    Item.BattleBelt: ItemClass.Belts,
    Item.WarBelt: ItemClass.Belts,
    Item.SpiderwebSash: ItemClass.Belts,
    Item.VampirefangBelt: ItemClass.Belts,
    Item.MithrilCoil: ItemClass.Belts,
    Item.TrollBelt: ItemClass.Belts,
    Item.ColossusGirdle: ItemClass.Belts,
    Item.Circlet: ItemClass.Circlets,
    Item.Coronet: ItemClass.Circlets,
    Item.Tiara: ItemClass.Circlets,
    Item.Diadem: ItemClass.Circlets,
    Item.Katar: ItemClass.AssassinKatars,
    Item.WristBlade: ItemClass.AssassinKatars,
    Item.HatchetHands: ItemClass.AssassinKatars,
    Item.Cestus: ItemClass.AssassinKatars,
    Item.Claws: ItemClass.AssassinKatars,
    Item.BladeTalons: ItemClass.AssassinKatars,
    Item.ScissorsKatar: ItemClass.AssassinKatars,
    Item.Quhab: ItemClass.AssassinKatars,
    Item.WristSpike: ItemClass.AssassinKatars,
    Item.Fascia: ItemClass.AssassinKatars,
    Item.HandScythe: ItemClass.AssassinKatars,
    Item.GreaterClaws: ItemClass.AssassinKatars,
    Item.GreaterTalons: ItemClass.AssassinKatars,
    Item.ScissorsQuhab: ItemClass.AssassinKatars,
    Item.Suwayyah: ItemClass.AssassinKatars,
    Item.WristSword: ItemClass.AssassinKatars,
    Item.WarFist: ItemClass.AssassinKatars,
    Item.BattleCestus: ItemClass.AssassinKatars,
    Item.FeralClaws: ItemClass.AssassinKatars,
    Item.RunicTalons: ItemClass.AssassinKatars,
    Item.ScissorsSuwayyah: ItemClass.AssassinKatars,
    Item.EagleOrb: ItemClass.SorceressOrbs,
    Item.SacredGlobe: ItemClass.SorceressOrbs,
    Item.SmokedSphere: ItemClass.SorceressOrbs,
    Item.ClaspedOrb: ItemClass.SorceressOrbs,
    Item.JaredsStone: ItemClass.SorceressOrbs,
    Item.GlowingOrb: ItemClass.SorceressOrbs,
    Item.CrystallineGlobe: ItemClass.SorceressOrbs,
    Item.CloudySphere: ItemClass.SorceressOrbs,
    Item.SparklingBall: ItemClass.SorceressOrbs,
    Item.SwirlingCrystal: ItemClass.SorceressOrbs,
    Item.HeavenlyStone: ItemClass.SorceressOrbs,
    Item.EldritchOrb: ItemClass.SorceressOrbs,
    Item.DemonHeart: ItemClass.SorceressOrbs,
    Item.VortexOrb: ItemClass.SorceressOrbs,
    Item.DimensionalShard: ItemClass.SorceressOrbs,
    Item.StagBow: ItemClass.AmazonBows,
    Item.ReflexBow: ItemClass.AmazonBows,
    Item.AshwoodBow: ItemClass.AmazonBows,
    Item.CeremonialBow: ItemClass.AmazonBows,
    Item.MatriarchalBow: ItemClass.AmazonBows,
    Item.GrandMatronBow: ItemClass.AmazonBows,
    Item.MaidenSpear: ItemClass.AmazonSpears,
    Item.MaidenPike: ItemClass.AmazonSpears,
    Item.CeremonialSpear: ItemClass.AmazonSpears,
    Item.CeremonialPike: ItemClass.AmazonSpears,
    Item.MatriarchalSpear: ItemClass.AmazonSpears,
    Item.MatriarchalPike: ItemClass.AmazonSpears,
    Item.MaidenJavelin: ItemClass.AmazonJavelins,
    Item.CeremonialJavelin: ItemClass.AmazonJavelins,
    Item.MatriarchalJavelin: ItemClass.AmazonJavelins,
    Item.WolfHead: ItemClass.DruidHelms,
    Item.HawkHelm: ItemClass.DruidHelms,
    Item.Antlers: ItemClass.DruidHelms,
    Item.FalconMask: ItemClass.DruidHelms,
    Item.SpiritMask: ItemClass.DruidHelms,
    Item.AlphaHelm: ItemClass.DruidHelms,
    Item.GriffonHeaddress: ItemClass.DruidHelms,
    Item.HuntersGuise: ItemClass.DruidHelms,
    Item.SacredFeathers: ItemClass.DruidHelms,
    Item.TotemicMask: ItemClass.DruidHelms,
    Item.BloodSpirit: ItemClass.DruidHelms,
    Item.SunSpirit: ItemClass.DruidHelms,
    Item.EarthSpirit: ItemClass.DruidHelms,
    Item.SkySpirit: ItemClass.DruidHelms,
    Item.DreamSpirit: ItemClass.DruidHelms,
    Item.JawboneCap: ItemClass.BarbarianHelms,
    Item.FangedHelm: ItemClass.BarbarianHelms,
    Item.HornedHelm: ItemClass.BarbarianHelms,
    Item.AssaultHelmet: ItemClass.BarbarianHelms,
    Item.AvengerGuard: ItemClass.BarbarianHelms,
    Item.JawboneVisor: ItemClass.BarbarianHelms,
    Item.LionHelm: ItemClass.BarbarianHelms,
    Item.RageMask: ItemClass.BarbarianHelms,
    Item.SavageHelmet: ItemClass.BarbarianHelms,
    Item.SlayerGuard: ItemClass.BarbarianHelms,
    Item.CarnageHelm: ItemClass.BarbarianHelms,
    Item.FuryVisor: ItemClass.BarbarianHelms,
    Item.DestroyerHelm: ItemClass.BarbarianHelms,
    Item.ConquerorCrown: ItemClass.BarbarianHelms,
    Item.GuardianCrown: ItemClass.BarbarianHelms,
    Item.Targe: ItemClass.PaladinShields,
    Item.Rondache: ItemClass.PaladinShields,
    Item.HeraldicShield: ItemClass.PaladinShields,
    Item.AerinShield: ItemClass.PaladinShields,
    Item.CrownShield: ItemClass.PaladinShields,
    Item.AkaranTarge: ItemClass.PaladinShields,
    Item.AkaranRondache: ItemClass.PaladinShields,
    Item.ProtectorShield: ItemClass.PaladinShields,
    Item.GildedShield: ItemClass.PaladinShields,
    Item.RoyalShield: ItemClass.PaladinShields,
    Item.SacredTarge: ItemClass.PaladinShields,
    Item.SacredRondache: ItemClass.PaladinShields,
    Item.KurastShield: ItemClass.PaladinShields,
    Item.ZakarumShield: ItemClass.PaladinShields,
    Item.VortexShield: ItemClass.PaladinShields,
    Item.PreservedHead: ItemClass.NecromancerShields,
    Item.ZombieHead: ItemClass.NecromancerShields,
    Item.UnravellerHead: ItemClass.NecromancerShields,
    Item.GargoyleHead: ItemClass.NecromancerShields,
    Item.DemonHeadShield: ItemClass.NecromancerShields,
    Item.MummifiedTrophy: ItemClass.NecromancerShields,
    Item.FetishTrophy: ItemClass.NecromancerShields,
    Item.SextonTrophy: ItemClass.NecromancerShields,
    Item.CantorTrophy: ItemClass.NecromancerShields,
    Item.HierophantTrophy: ItemClass.NecromancerShields,
    Item.MinionSkull: ItemClass.NecromancerShields,
    Item.HellspawnSkull: ItemClass.NecromancerShields,
    Item.OverseerSkull: ItemClass.NecromancerShields,
    Item.SuccubusSkull: ItemClass.NecromancerShields,
    Item.BloodlordSkull: ItemClass.NecromancerShields,
}

ITEM_DIMENSIONS = {
    Item.HandAxe: (1, 3),
    Item.Axe: (2, 3),
    Item.DoubleAxe: (2, 3),
    Item.MilitaryPick: (2, 3),
    Item.WarAxe: (2, 3),
    Item.LargeAxe: (2, 3),
    Item.BroadAxe: (2, 3),
    Item.BattleAxe: (2, 3),
    Item.GreatAxe: (2, 4),
    Item.GiantAxe: (2, 3),
    Item.Wand: (1, 2),
    Item.YewWand: (1, 2),
    Item.BoneWand: (1, 2),
    Item.GrimWand: (1, 2),
    Item.Club: (1, 3),
    Item.Scepter: (1, 3),
    Item.GrandScepter: (1, 3),
    Item.WarScepter: (2, 3),
    Item.SpikedClub: (1, 3),
    Item.Mace: (1, 3),
    Item.MorningStar: (1, 3),
    Item.Flail: (2, 3),
    Item.WarHammer: (2, 3),
    Item.Maul: (2, 4),
    Item.GreatMaul: (2, 3),
    Item.ShortSword: (1, 3),
    Item.Scimitar: (1, 3),
    Item.Sabre: (1, 3),
    Item.Falchion: (1, 3),
    Item.CrystalSword: (2, 3),
    Item.BroadSword: (2, 3),
    Item.LongSword: (2, 3),
    Item.WarSword: (1, 3),
    Item.TwoHandedSword: (1, 4),
    Item.Claymore: (1, 4),
    Item.GiantSword: (1, 4),
    Item.BastardSword: (1, 4),
    Item.Flamberge: (2, 4),
    Item.GreatSword: (2, 4),
    Item.Dagger: (1, 2),
    Item.Dirk: (1, 2),
    Item.Kris: (1, 3),
    Item.Blade: (1, 3),
    Item.ThrowingKnife: (1, 2),
    Item.ThrowingAxe: (1, 2),
    Item.BalancedKnife: (1, 2),
    Item.BalancedAxe: (2, 3),
    Item.Javelin: (1, 3),
    Item.Pilum: (1, 3),
    Item.ShortSpear: (1, 3),
    Item.Glaive: (1, 4),
    Item.ThrowingSpear: (1, 4),
    Item.Spear: (2, 4),
    Item.Trident: (2, 4),
    Item.Brandistock: (2, 4),
    Item.Spetum: (2, 4),
    Item.Pike: (2, 4),
    Item.Bardiche: (2, 4),
    Item.Voulge: (2, 4),
    Item.Scythe: (2, 4),
    Item.Poleaxe: (2, 4),
    Item.Halberd: (2, 4),
    Item.WarScythe: (2, 4),
    Item.ShortStaff: (1, 3),
    Item.LongStaff: (1, 4),
    Item.GnarledStaff: (1, 4),
    Item.BattleStaff: (1, 4),
    Item.WarStaff: (2, 4),
    Item.ShortBow: (2, 3),
    Item.HuntersBow: (2, 3),
    Item.LongBow: (2, 4),
    Item.CompositeBow: (2, 3),
    Item.ShortBattleBow: (2, 3),
    Item.LongBattleBow: (2, 4),
    Item.ShortWarBow: (2, 3),
    Item.LongWarBow: (2, 4),
    Item.LightCrossbow: (2, 3),
    Item.Crossbow: (2, 3),
    Item.HeavyCrossbow: (2, 4),
    Item.RepeatingCrossbow: (2, 3),
    Item.RancidGasPotion: (1, 1),
    Item.OilPotion: (1, 1),
    Item.ChokingGasPotion: (1, 1),
    Item.ExplodingPotion: (1, 1),
    Item.StranglingGasPotion: (1, 1),
    Item.FulminatingPotion: (1, 1),
    Item.DecoyGidbinn: (1, 2),
    Item.TheGidbinn: (1, 2),
    Item.WirtsLeg: (1, 3),
    Item.HoradricMalus: (1, 2),
    Item.HellforgeHammer: (2, 3),
    Item.HoradricStaff: (1, 4),
    Item.StaffOfKings: (1, 3),
    Item.Hatchet: (1, 3),
    Item.Cleaver: (2, 3),
    Item.TwinAxe: (2, 3),
    Item.Crowbill: (2, 3),
    Item.Naga: (2, 3),
    Item.MilitaryAxe: (2, 3),
    Item.BeardedAxe: (2, 3),
    Item.Tabar: (2, 3),
    Item.GothicAxe: (2, 4),
    Item.AncientAxe: (2, 3),
    Item.BurntWand: (1, 2),
    Item.PetrifiedWand: (1, 2),
    Item.TombWand: (1, 2),
    Item.GraveWand: (1, 2),
    Item.Cudgel: (1, 3),
    Item.RuneScepter: (1, 3),
    Item.HolyWaterSprinkler: (1, 3),
    Item.DivineScepter: (2, 3),
    Item.BarbedClub: (1, 3),
    Item.FlangedMace: (1, 3),
    Item.JaggedStar: (1, 3),
    Item.Knout: (2, 3),
    Item.BattleHammer: (2, 3),
    Item.WarClub: (2, 4),
    Item.MartelDeFer: (2, 3),
    Item.Gladius: (1, 3),
    Item.Cutlass: (1, 3),
    Item.Shamshir: (1, 3),
    Item.Tulwar: (1, 3),
    Item.DimensionalBlade: (2, 3),
    Item.BattleSword: (2, 3),
    Item.RuneSword: (2, 3),
    Item.AncientSword: (1, 3),
    Item.Espandon: (1, 4),
    Item.DacianFalx: (1, 4),
    Item.TuskSword: (1, 4),
    Item.GothicSword: (1, 4),
    Item.Zweihander: (2, 4),
    Item.ExecutionerSword: (2, 4),
    Item.Poignard: (1, 2),
    Item.Rondel: (1, 2),
    Item.Cinquedeas: (1, 3),
    Item.Stiletto: (1, 3),
    Item.BattleDart: (1, 2),
    Item.Francisca: (1, 2),
    Item.WarDart: (1, 2),
    Item.Hurlbat: (2, 3),
    Item.WarJavelin: (1, 3),
    Item.GreatPilum: (1, 3),
    Item.Simbilan: (1, 3),
    Item.Spiculum: (1, 4),
    Item.Harpoon: (1, 4),
    Item.WarSpear: (2, 4),
    Item.Fuscina: (2, 4),
    Item.WarFork: (2, 4),
    Item.Yari: (2, 4),
    Item.Lance: (2, 4),
    Item.LochaberAxe: (2, 4),
    Item.Bill: (2, 4),
    Item.BattleScythe: (2, 4),
    Item.Partizan: (2, 4),
    Item.BecDeCorbin: (2, 4),
    Item.GrimScythe: (2, 4),
    Item.JoStaff: (1, 3),
    Item.QuarterStaff: (1, 4),
    Item.CedarStaff: (1, 4),
    Item.GothicStaff: (1, 4),
    Item.RuneStaff: (2, 4),
    Item.EdgeBow: (2, 3),
    Item.RazorBow: (2, 3),
    Item.CedarBow: (2, 4),
    Item.DoubleBow: (2, 3),
    Item.ShortSiegeBow: (2, 3),
    Item.LargeSiegeBow: (2, 4),
    Item.RuneBow: (2, 3),
    Item.GothicBow: (2, 4),
    Item.Arbalest: (2, 3),
    Item.SiegeCrossbow: (2, 3),
    Item.Ballista: (2, 4),
    Item.ChuKoNu: (2, 3),
    Item.KhalimsFlail: (2, 3),
    Item.KhalimsWill: (2, 3),
    Item.Katar: (1, 3),
    Item.WristBlade: (1, 3),
    Item.HatchetHands: (1, 3),
    Item.Cestus: (1, 3),
    Item.Claws: (1, 3),
    Item.BladeTalons: (1, 3),
    Item.ScissorsKatar: (1, 3),
    Item.Quhab: (1, 3),
    Item.WristSpike: (1, 3),
    Item.Fascia: (1, 3),
    Item.HandScythe: (1, 3),
    Item.GreaterClaws: (1, 3),
    Item.GreaterTalons: (1, 3),
    Item.ScissorsQuhab: (1, 3),
    Item.Suwayyah: (1, 3),
    Item.WristSword: (1, 3),
    Item.WarFist: (1, 3),
    Item.BattleCestus: (1, 3),
    Item.FeralClaws: (1, 3),
    Item.RunicTalons: (1, 3),
    Item.ScissorsSuwayyah: (1, 3),
    Item.Tomahawk: (1, 3),
    Item.SmallCrescent: (2, 3),
    Item.EttinAxe: (2, 3),
    Item.WarSpike: (2, 3),
    Item.BerserkerAxe: (2, 3),
    Item.FeralAxe: (2, 3),
    Item.SilverEdgedAxe: (2, 3),
    Item.Decapitator: (2, 3),
    Item.ChampionAxe: (2, 4),
    Item.GloriousAxe: (2, 3),
    Item.PolishedWand: (1, 2),
    Item.GhostWand: (1, 2),
    Item.LichWand: (1, 2),
    Item.UnearthedWand: (1, 2),
    Item.Truncheon: (1, 3),
    Item.MightyScepter: (1, 3),
    Item.SeraphRod: (1, 3),
    Item.Caduceus: (2, 3),
    Item.TyrantClub: (1, 3),
    Item.ReinforcedMace: (1, 3),
    Item.DevilStar: (1, 3),
    Item.Scourge: (2, 3),
    Item.LegendaryMallet: (2, 3),
    Item.OgreMaul: (2, 4),
    Item.ThunderMaul: (2, 3),
    Item.Falcata: (1, 3),
    Item.Ataghan: (1, 3),
    Item.ElegantBlade: (1, 3),
    Item.HydraEdge: (1, 3),
    Item.PhaseBlade: (2, 3),
    Item.ConquestSword: (2, 3),
    Item.CrypticSword: (2, 3),
    Item.MythicalSword: (1, 3),
    Item.LegendSword: (1, 4),
    Item.HighlandBlade: (1, 4),
    Item.BalrogBlade: (1, 4),
    Item.ChampionSword: (1, 4),
    Item.ColossusSword: (2, 4),
    Item.ColossusBlade: (2, 4),
    Item.BoneKnife: (1, 2),
    Item.MithrilPoint: (1, 2),
    Item.FangedKnife: (1, 3),
    Item.LegendSpike: (1, 3),
    Item.FlyingKnife: (1, 2),
    Item.FlyingAxe: (1, 2),
    Item.WingedKnife: (1, 2),
    Item.WingedAxe: (2, 3),
    Item.HyperionJavelin: (1, 3),
    Item.StygianPilum: (1, 3),
    Item.BalrogSpear: (1, 3),
    Item.GhostGlaive: (1, 4),
    Item.WingedHarpoon: (1, 4),
    Item.HyperionSpear: (2, 4),
    Item.StygianPike: (2, 4),
    Item.Mancatcher: (2, 4),
    Item.GhostSpear: (2, 4),
    Item.WarPike: (2, 4),
    Item.OgreAxe: (2, 4),
    Item.ColossusVoulge: (2, 4),
    Item.Thresher: (2, 4),
    Item.CrypticAxe: (2, 4),
    Item.GreatPoleaxe: (2, 4),
    Item.GiantThresher: (2, 4),
    Item.WalkingStick: (1, 3),
    Item.Stalagmite: (1, 4),
    Item.ElderStaff: (1, 4),
    Item.Shillelagh: (1, 4),
    Item.ArchonStaff: (2, 4),
    Item.SpiderBow: (2, 3),
    Item.BladeBow: (2, 3),
    Item.ShadowBow: (2, 4),
    Item.GreatBow: (2, 3),
    Item.DiamondBow: (2, 3),
    Item.CrusaderBow: (2, 4),
    Item.WardBow: (2, 3),
    Item.HydraBow: (2, 4),
    Item.PelletBow: (2, 3),
    Item.GorgonCrossbow: (2, 3),
    Item.ColossusCrossbow: (2, 4),
    Item.DemonCrossBow: (2, 3),
    Item.EagleOrb: (1, 2),
    Item.SacredGlobe: (1, 2),
    Item.SmokedSphere: (1, 2),
    Item.ClaspedOrb: (1, 2),
    Item.JaredsStone: (1, 3),
    Item.StagBow: (2, 4),
    Item.ReflexBow: (2, 4),
    Item.MaidenSpear: (2, 4),
    Item.MaidenPike: (2, 4),
    Item.MaidenJavelin: (1, 3),
    Item.GlowingOrb: (1, 2),
    Item.CrystallineGlobe: (1, 2),
    Item.CloudySphere: (1, 2),
    Item.SparklingBall: (1, 2),
    Item.SwirlingCrystal: (1, 3),
    Item.AshwoodBow: (2, 4),
    Item.CeremonialBow: (2, 4),
    Item.CeremonialSpear: (2, 4),
    Item.CeremonialPike: (2, 4),
    Item.CeremonialJavelin: (1, 3),
    Item.HeavenlyStone: (1, 2),
    Item.EldritchOrb: (1, 2),
    Item.DemonHeart: (1, 2),
    Item.VortexOrb: (1, 2),
    Item.DimensionalShard: (1, 3),
    Item.MatriarchalBow: (2, 4),
    Item.GrandMatronBow: (2, 4),
    Item.MatriarchalSpear: (2, 4),
    Item.MatriarchalPike: (2, 4),
    Item.MatriarchalJavelin: (1, 3),
    Item.Cap: (2, 2),
    Item.SkullCap: (2, 2),
    Item.Helm: (2, 2),
    Item.FullHelm: (2, 2),
    Item.GreatHelm: (2, 2),
    Item.Crown: (2, 2),
    Item.Mask: (2, 2),
    Item.QuiltedArmor: (2, 3),
    Item.LeatherArmor: (2, 3),
    Item.HardLeatherArmor: (2, 3),
    Item.StuddedLeather: (2, 3),
    Item.RingMail: (2, 3),
    Item.ScaleMail: (2, 3),
    Item.ChainMail: (2, 3),
    Item.BreastPlate: (2, 3),
    Item.SplintMail: (2, 3),
    Item.PlateMail: (2, 3),
    Item.FieldPlate: (2, 3),
    Item.GothicPlate: (2, 3),
    Item.FullPlateMail: (2, 3),
    Item.AncientArmor: (2, 3),
    Item.LightPlate: (2, 3),
    Item.Buckler: (2, 2),
    Item.SmallShield: (2, 2),
    Item.LargeShield: (2, 3),
    Item.KiteShield: (2, 3),
    Item.TowerShield: (2, 3),
    Item.GothicShield: (2, 4),
    Item.LeatherGloves: (2, 2),
    Item.HeavyGloves: (2, 2),
    Item.ChainGloves: (2, 2),
    Item.LightGauntlets: (2, 2),
    Item.Gauntlets: (2, 2),
    Item.Boots: (2, 2),
    Item.HeavyBoots: (2, 2),
    Item.ChainBoots: (2, 2),
    Item.LightPlatedBoots: (2, 2),
    Item.Greaves: (2, 2),
    Item.Sash: (2, 1),
    Item.LightBelt: (2, 1),
    Item.Belt: (2, 1),
    Item.HeavyBelt: (2, 1),
    Item.PlatedBelt: (2, 1),
    Item.BoneHelm: (2, 2),
    Item.BoneShield: (2, 3),
    Item.SpikedShield: (2, 3),
    Item.WarHat: (2, 2),
    Item.Sallet: (2, 2),
    Item.Casque: (2, 2),
    Item.Basinet: (2, 2),
    Item.WingedHelm: (2, 2),
    Item.GrandCrown: (2, 2),
    Item.DeathMask: (2, 2),
    Item.GhostArmor: (2, 3),
    Item.SerpentskinArmor: (2, 3),
    Item.DemonhideArmor: (2, 3),
    Item.TrellisedArmor: (2, 3),
    Item.LinkedMail: (2, 3),
    Item.TigulatedMail: (2, 3),
    Item.MeshArmor: (2, 3),
    Item.Cuirass: (2, 3),
    Item.RussetArmor: (2, 3),
    Item.TemplarCoat: (2, 3),
    Item.SharktoothArmor: (2, 3),
    Item.EmbossedPlate: (2, 3),
    Item.ChaosArmor: (2, 3),
    Item.OrnatePlate: (2, 3),
    Item.MagePlate: (2, 3),
    Item.Defender: (2, 2),
    Item.RoundShield: (2, 2),
    Item.Scutum: (2, 3),
    Item.DragonShield: (2, 3),
    Item.Pavise: (2, 3),
    Item.AncientShield: (2, 4),
    Item.DemonhideGloves: (2, 2),
    Item.SharkskinGloves: (2, 2),
    Item.HeavyBracers: (2, 2),
    Item.BattleGauntlets: (2, 2),
    Item.WarGauntlets: (2, 2),
    Item.DemonhideBoots: (2, 2),
    Item.SharkskinBoots: (2, 2),
    Item.MeshBoots: (2, 2),
    Item.BattleBoots: (2, 2),
    Item.WarBoots: (2, 2),
    Item.DemonhideSash: (2, 1),
    Item.SharkskinBelt: (2, 1),
    Item.MeshBelt: (2, 1),
    Item.BattleBelt: (2, 1),
    Item.WarBelt: (2, 1),
    Item.GrimHelm: (2, 2),
    Item.GrimShield: (2, 3),
    Item.BarbedShield: (2, 3),
    Item.WolfHead: (2, 2),
    Item.HawkHelm: (2, 2),
    Item.Antlers: (2, 2),
    Item.FalconMask: (2, 2),
    Item.SpiritMask: (2, 2),
    Item.JawboneCap: (2, 2),
    Item.FangedHelm: (2, 2),
    Item.HornedHelm: (2, 2),
    Item.AssaultHelmet: (2, 2),
    Item.AvengerGuard: (2, 2),
    Item.Targe: (2, 2),
    Item.Rondache: (2, 2),
    Item.HeraldicShield: (2, 4),
    Item.AerinShield: (2, 4),
    Item.CrownShield: (2, 2),
    Item.PreservedHead: (2, 2),
    Item.ZombieHead: (2, 2),
    Item.UnravellerHead: (2, 2),
    Item.GargoyleHead: (2, 2),
    Item.DemonHeadShield: (2, 2),
    Item.Circlet: (2, 2),
    Item.Coronet: (2, 2),
    Item.Tiara: (2, 2),
    Item.Diadem: (2, 2),
    Item.Shako: (2, 2),
    Item.Hydraskull: (2, 2),
    Item.Armet: (2, 2),
    Item.GiantConch: (2, 2),
    Item.SpiredHelm: (2, 2),
    Item.Corona: (2, 2),
    Item.DemonHead: (2, 2),
    Item.DuskShroud: (2, 3),
    Item.Wyrmhide: (2, 3),
    Item.ScarabHusk: (2, 3),
    Item.WireFleece: (2, 3),
    Item.DiamondMail: (2, 3),
    Item.LoricatedMail: (2, 3),
    Item.Boneweave: (2, 3),
    Item.GreatHauberk: (2, 3),
    Item.BalrogSkin: (2, 3),
    Item.HellforgePlate: (2, 3),
    Item.KrakenShell: (2, 3),
    Item.LacqueredPlate: (2, 3),
    Item.ShadowPlate: (2, 3),
    Item.SacredArmor: (2, 3),
    Item.ArchonPlate: (2, 3),
    Item.Heater: (2, 2),
    Item.Luna: (2, 2),
    Item.Hyperion: (2, 3),
    Item.Monarch: (2, 3),
    Item.Aegis: (2, 3),
    Item.Ward: (2, 4),
    Item.BrambleMitts: (2, 2),
    Item.VampireboneGloves: (2, 2),
    Item.Vambraces: (2, 2),
    Item.CrusaderGauntlets: (2, 2),
    Item.OgreGauntlets: (2, 2),
    Item.WyrmhideBoots: (2, 2),
    Item.ScarabshellBoots: (2, 2),
    Item.BoneweaveBoots: (2, 2),
    Item.MirroredBoots: (2, 2),
    Item.MyrmidonGreaves: (2, 2),
    Item.SpiderwebSash: (2, 1),
    Item.VampirefangBelt: (2, 1),
    Item.MithrilCoil: (2, 1),
    Item.TrollBelt: (2, 1),
    Item.ColossusGirdle: (2, 1),
    Item.BoneVisage: (2, 2),
    Item.TrollNest: (2, 3),
    Item.BladeBarrier: (2, 3),
    Item.AlphaHelm: (2, 2),
    Item.GriffonHeaddress: (2, 2),
    Item.HuntersGuise: (2, 2),
    Item.SacredFeathers: (2, 2),
    Item.TotemicMask: (2, 2),
    Item.JawboneVisor: (2, 2),
    Item.LionHelm: (2, 2),
    Item.RageMask: (2, 2),
    Item.SavageHelmet: (2, 2),
    Item.SlayerGuard: (2, 2),
    Item.AkaranTarge: (2, 2),
    Item.AkaranRondache: (2, 2),
    Item.ProtectorShield: (2, 4),
    Item.GildedShield: (2, 4),
    Item.RoyalShield: (2, 2),
    Item.MummifiedTrophy: (2, 2),
    Item.FetishTrophy: (2, 2),
    Item.SextonTrophy: (2, 2),
    Item.CantorTrophy: (2, 2),
    Item.HierophantTrophy: (2, 2),
    Item.BloodSpirit: (2, 2),
    Item.SunSpirit: (2, 2),
    Item.EarthSpirit: (2, 2),
    Item.SkySpirit: (2, 2),
    Item.DreamSpirit: (2, 2),
    Item.CarnageHelm: (2, 2),
    Item.FuryVisor: (2, 2),
    Item.DestroyerHelm: (2, 2),
    Item.ConquerorCrown: (2, 2),
    Item.GuardianCrown: (2, 2),
    Item.SacredTarge: (2, 2),
    Item.SacredRondache: (2, 2),
    Item.KurastShield: (2, 4),
    Item.ZakarumShield: (2, 4),
    Item.VortexShield: (2, 2),
    Item.MinionSkull: (2, 2),
    Item.HellspawnSkull: (2, 2),
    Item.OverseerSkull: (2, 2),
    Item.SuccubusSkull: (2, 2),
    Item.BloodlordSkull: (2, 2),
    Item.Elixir: (1, 1),
    Item.INVALID509: (1, 1),
    Item.INVALID510: (1, 1),
    Item.INVALID511: (1, 1),
    Item.INVALID512: (1, 1),
    Item.StaminaPotion: (1, 1),
    Item.AntidotePotion: (1, 1),
    Item.RejuvenationPotion: (1, 1),
    Item.FullRejuvenationPotion: (1, 1),
    Item.ThawingPotion: (1, 1),
    Item.TomeOfTownPortal: (1, 2),
    Item.TomeOfIdentify: (1, 2),
    Item.Amulet: (1, 1),
    Item.AmuletOfTheViper: (1, 1),
    Item.Ring: (1, 1),
    Item.Gold: (1, 1),
    Item.ScrollOfInifuss: (2, 2),
    Item.KeyToTheCairnStones: (2, 2),
    Item.Arrows: (1, 3),
    Item.Torch: (1, 2),
    Item.Bolts: (1, 3),
    Item.ScrollOfTownPortal: (1, 1),
    Item.ScrollOfIdentify: (1, 1),
    Item.Heart: (1, 1),
    Item.Brain: (1, 1),
    Item.Jawbone: (1, 1),
    Item.Eye: (1, 1),
    Item.Horn: (1, 1),
    Item.Tail: (1, 1),
    Item.Flag: (1, 1),
    Item.Fang: (1, 1),
    Item.Quill: (1, 1),
    Item.Soul: (1, 1),
    Item.Scalp: (1, 1),
    Item.Spleen: (1, 1),
    Item.Key: (1, 1),
    Item.TheBlackTowerKey: (1, 2),
    Item.PotionOfLife: (1, 1),
    Item.AJadeFigurine: (1, 2),
    Item.TheGoldenBird: (1, 2),
    Item.LamEsensTome: (2, 2),
    Item.HoradricCube: (2, 2),
    Item.HoradricScroll: (2, 2),
    Item.MephistosSoulstone: (1, 1),
    Item.BookOfSkill: (2, 2),
    Item.KhalimsEye: (1, 1),
    Item.KhalimsHeart: (1, 1),
    Item.KhalimsBrain: (1, 1),
    Item.Ear: (1, 1),
    Item.ChippedAmethyst: (1, 1),
    Item.FlawedAmethyst: (1, 1),
    Item.Amethyst: (1, 1),
    Item.FlawlessAmethyst: (1, 1),
    Item.PerfectAmethyst: (1, 1),
    Item.ChippedTopaz: (1, 1),
    Item.FlawedTopaz: (1, 1),
    Item.Topaz: (1, 1),
    Item.FlawlessTopaz: (1, 1),
    Item.PerfectTopaz: (1, 1),
    Item.ChippedSapphire: (1, 1),
    Item.FlawedSapphire: (1, 1),
    Item.Sapphire: (1, 1),
    Item.FlawlessSapphire: (1, 1),
    Item.PerfectSapphire: (1, 1),
    Item.ChippedEmerald: (1, 1),
    Item.FlawedEmerald: (1, 1),
    Item.Emerald: (1, 1),
    Item.FlawlessEmerald: (1, 1),
    Item.PerfectEmerald: (1, 1),
    Item.ChippedRuby: (1, 1),
    Item.FlawedRuby: (1, 1),
    Item.Ruby: (1, 1),
    Item.FlawlessRuby: (1, 1),
    Item.PerfectRuby: (1, 1),
    Item.ChippedDiamond: (1, 1),
    Item.FlawedDiamond: (1, 1),
    Item.Diamond: (1, 1),
    Item.FlawlessDiamond: (1, 1),
    Item.PerfectDiamond: (1, 1),
    Item.MinorHealingPotion: (1, 1),
    Item.LightHealingPotion: (1, 1),
    Item.HealingPotion: (1, 1),
    Item.GreaterHealingPotion: (1, 1),
    Item.SuperHealingPotion: (1, 1),
    Item.MinorManaPotion: (1, 1),
    Item.LightManaPotion: (1, 1),
    Item.ManaPotion: (1, 1),
    Item.GreaterManaPotion: (1, 1),
    Item.SuperManaPotion: (1, 1),
    Item.ChippedSkull: (1, 1),
    Item.FlawedSkull: (1, 1),
    Item.Skull: (1, 1),
    Item.FlawlessSkull: (1, 1),
    Item.PerfectSkull: (1, 1),
    Item.Herb: (1, 1),
    Item.SmallCharm: (1, 1),
    Item.LargeCharm: (1, 2),
    Item.GrandCharm: (1, 3),
    Item.INVALID606: (1, 1),
    Item.INVALID607: (1, 1),
    Item.INVALID608: (1, 1),
    Item.INVALID609: (1, 1),
    Item.ElRune: (1, 1),
    Item.EldRune: (1, 1),
    Item.TirRune: (1, 1),
    Item.NefRune: (1, 1),
    Item.EthRune: (1, 1),
    Item.IthRune: (1, 1),
    Item.TalRune: (1, 1),
    Item.RalRune: (1, 1),
    Item.OrtRune: (1, 1),
    Item.ThulRune: (1, 1),
    Item.AmnRune: (1, 1),
    Item.SolRune: (1, 1),
    Item.ShaelRune: (1, 1),
    Item.DolRune: (1, 1),
    Item.HelRune: (1, 1),
    Item.IoRune: (1, 1),
    Item.LumRune: (1, 1),
    Item.KoRune: (1, 1),
    Item.FalRune: (1, 1),
    Item.LemRune: (1, 1),
    Item.PulRune: (1, 1),
    Item.UmRune: (1, 1),
    Item.MalRune: (1, 1),
    Item.IstRune: (1, 1),
    Item.GulRune: (1, 1),
    Item.VexRune: (1, 1),
    Item.OhmRune: (1, 1),
    Item.LoRune: (1, 1),
    Item.SurRune: (1, 1),
    Item.BerRune: (1, 1),
    Item.JahRune: (1, 1),
    Item.ChamRune: (1, 1),
    Item.ZodRune: (1, 1),
    Item.Jewel: (1, 1),
    Item.MalahsPotion: (1, 1),
    Item.ScrollOfKnowledge: (1, 1),
    Item.ScrollOfResistance: (2, 2),
    Item.KeyOfTerror: (1, 2),
    Item.KeyOfHate: (1, 2),
    Item.KeyOfDestruction: (1, 2),
    Item.DiablosHorn: (1, 1),
    Item.BaalsEye: (1, 1),
    Item.MephistosBrain: (1, 1),
    Item.TokenofAbsolution: (1, 1),
    Item.TwistedEssenceOfSuffering: (1, 1),
    Item.ChargedEssenceOfHatred: (1, 1),
    Item.BurningEssenceOfTerror: (1, 1),
    Item.FesteringEssenceOfDestruction: (1, 1),
    Item.StandardOfHeroes: (1, 1),
}
