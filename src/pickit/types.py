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