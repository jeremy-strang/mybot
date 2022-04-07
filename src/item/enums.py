
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

class ItemQuality:
    Inferior = "INFERIOR" # Inferior
    Normal = "NORMAL" # Normal
    Superior = "SUPERIOR" # Superior
    Magic = "MAGIC" # Magic
    Set = "SET" # Set
    Rare = "RARE" # Rare
    Unique = "UNIQUE" # Unique
    Craft = "CRAFT" # Crafted
    Tempered = "TEMPERED" # Tempered

class ItemMode:
    Stored = "STORED" # Item is in storage (inventory, cube, stash?)
    Equip = "EQUIP" # Item is equippped
    Inbelt = "INBELT" # Item is in belt rows
    OnGround = "ONGROUND" # Item is on ground
    OnCursor = "ONCURSOR" # Item is on cursor
    Dropping = "DROPPING" # Item is being dropped
    Socketed = "SOCKETED" # Item is socketed in another item

class ItemFlag:
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

class ItemBase:
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
