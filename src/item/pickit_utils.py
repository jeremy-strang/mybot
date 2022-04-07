from item.enums import ItemBase, ItemQuality, ItemMode, InventoryPage, BodyLoc, StashType, ItemFlag

POTIONS = {
    ItemBase.FullRejuvenationPotion: 1,
    ItemBase.RejuvenationPotion: 1,
    ItemBase.SuperHealingPotion: 1,
    ItemBase.SuperManaPotion: 1,
    ItemBase.GreaterHealingPotion: 0,
    ItemBase.GreaterManaPotion: 0,
}

BASIC_ITEMS = {
    ItemBase.KeyOfTerror: 1,
    ItemBase.KeyOfHate: 1,
    ItemBase.KeyOfDestruction: 1,
    
    ItemBase.TwistedEssenceOfSuffering: 1,
    ItemBase.ChargedEssenceOfHatred: 1,
    ItemBase.BurningEssenceOfTerror: 1,
    ItemBase.FesteringEssenceOfDestruction: 1,

    ItemBase.ElRune: 0,
    ItemBase.EldRune: 0,
    ItemBase.TirRune: 0,
    ItemBase.NefRune: 0,
    ItemBase.EthRune: 0,
    ItemBase.IthRune: 0,
    ItemBase.TalRune: 0,
    ItemBase.RalRune: 0,
    ItemBase.OrtRune: 0,
    ItemBase.ThulRune: 0,
    ItemBase.AmnRune: 0,
    ItemBase.SolRune: 0,
    ItemBase.ShaelRune: 0,
    ItemBase.DolRune: 0,
    ItemBase.HelRune: 0,
    ItemBase.IoRune: 0,
    ItemBase.LumRune: 0,
    ItemBase.KoRune: 0,
    ItemBase.FalRune: 0,
    ItemBase.LemRune: 1,
    ItemBase.PulRune: 1,
    ItemBase.UmRune: 1,
    ItemBase.MalRune: 1,
    ItemBase.IstRune: 1,
    ItemBase.GulRune: 1,
    ItemBase.VexRune: 2,
    ItemBase.OhmRune: 2,
    ItemBase.LoRune: 2,
    ItemBase.SurRune: 2,
    ItemBase.BerRune: 2,
    ItemBase.JahRune: 2,
    ItemBase.ChamRune: 2,
    ItemBase.ZodRune: 2,

    ItemBase.ChippedAmethyst: 0,
    ItemBase.ChippedTopaz: 0,
    ItemBase.ChippedSapphire: 0,
    ItemBase.ChippedEmerald: 0,
    ItemBase.ChippedRuby: 0,
    ItemBase.ChippedDiamond: 0,

    ItemBase.FlawedAmethyst: 0,
    ItemBase.FlawedTopaz: 0,
    ItemBase.FlawedSapphire: 0,
    ItemBase.FlawedEmerald: 0,
    ItemBase.FlawedRuby: 0,
    ItemBase.FlawedDiamond: 0,

    ItemBase.Amethyst: 0,
    ItemBase.Topaz: 0,
    ItemBase.Sapphire: 0,
    ItemBase.Emerald: 0,
    ItemBase.Ruby: 0,
    ItemBase.Diamond: 0,

    ItemBase.FlawlessAmethyst: 0,
    ItemBase.FlawlessTopaz: 0,
    ItemBase.FlawlessSapphire: 0,
    ItemBase.FlawlessEmerald: 0,
    ItemBase.FlawlessRuby: 0,
    ItemBase.FlawlessDiamond: 0,

    ItemBase.PerfectAmethyst: 1,
    ItemBase.PerfectTopaz: 1,
    ItemBase.PerfectSapphire: 1,
    ItemBase.PerfectEmerald: 1,
    ItemBase.PerfectRuby: 1,
    ItemBase.PerfectDiamond: 1,
}

UNIQUE_ITEMS = {
    ItemBase.GrandCharm: 1,
    ItemBase.SmallCharm: 1,
    ItemBase.Amulet: 1,
    ItemBase.Ring: 1,
    ItemBase.Jewel: 1,

    ItemBase.DemonhideArmor: 0,
    ItemBase.ChaosArmor: 0,
    ItemBase.StuddedLeather: 0,
    ItemBase.AncientArmor: 0,
    ItemBase.GhostArmor: 0,
    ItemBase.MagePlate: 0,
    ItemBase.OrnatePlate: 0,
    ItemBase.WireFleece: 0,
    ItemBase.KrakenShell: 0,
    ItemBase.BalrogSkin: 0,
    ItemBase.SacredArmor: 1,
    ItemBase.Cuirass: 0,
    ItemBase.TemplarCoat: 1,
    ItemBase.DuskShroud: 1,
    ItemBase.MeshArmor: 0,
    ItemBase.SerpentskinArmor: 1,
    ItemBase.RussetArmor: 0,
    ItemBase.EmbossedPlate: 0,
    ItemBase.Sash: 0,
    ItemBase.Belt: 0,
    ItemBase.MeshBelt: 0,
    ItemBase.VampirefangBelt: 0,
    ItemBase.HeavyBelt: 0,
    ItemBase.SharkskinBelt: 0,
    ItemBase.BattleBelt: 0,
    ItemBase.WarBelt: 1,
    ItemBase.SpiderwebSash: 1,
    ItemBase.MithrilCoil: 1,
    ItemBase.DemonhideBoots: 0,
    ItemBase.LightPlatedBoots: 0,
    ItemBase.BoneweaveBoots: 1,
    ItemBase.MeshBoots: 0,
    ItemBase.SharkskinBoots: 0,
    ItemBase.MyrmidonGreaves: 1,
    ItemBase.WarBoots: 0,
    ItemBase.BattleBoots: 1,
    ItemBase.ScarabshellBoots: 1,
    ItemBase.Boots: 0,
    ItemBase.HeavyGloves: 0,
    ItemBase.ChainGloves: 0,
    ItemBase.VampireboneGloves: 1,
    ItemBase.Gauntlets: 0,
    ItemBase.LightGauntlets: 0,
    ItemBase.OgreGauntlets: 1,
    ItemBase.Vambraces: 0,
    ItemBase.DemonhideGloves: 0,
    ItemBase.HeavyBracers: 0,
    ItemBase.SharkskinGloves: 0,
    ItemBase.BattleGauntlets: 0,
    ItemBase.WarGauntlets: 0,
    ItemBase.SkullCap: 0,
    ItemBase.WarHat: 0,
    ItemBase.GrandCrown: 1,
    ItemBase.BoneVisage: 1,
    ItemBase.SpiredHelm: 1,
    ItemBase.DemonHead: 1,
    ItemBase.Corona: 1,
    ItemBase.Diadem: 1,
    ItemBase.Shako: 1,
    ItemBase.Tiara: 1,
    ItemBase.Casque: 0,
    ItemBase.GrimHelm: 1,
    ItemBase.WingedHelm: 0,
    ItemBase.Basinet: 0,
    ItemBase.Armet: 0,
    ItemBase.DeathMask: 0,
    ItemBase.Sallet: 0,
    ItemBase.SlayerGuard: 1,
    ItemBase.FuryVisor: 1,
    ItemBase.BloodSpirit: 0,
    ItemBase.TotemicMask: 0,
    ItemBase.EarthSpirit: 0,
    ItemBase.SkySpirit: 1,
    ItemBase.Amulet: 1,
    ItemBase.Ring: 1,
    ItemBase.Jewel: 1,
    ItemBase.GrandCharm: 1,
    ItemBase.SuccubusSkull: 1,
    ItemBase.BloodlordSkull: 1,
    ItemBase.HierophantTrophy: 1,
    ItemBase.GrimWand: 0,
    ItemBase.TombWand: 0,
    ItemBase.BurntWand: 1,
    ItemBase.LichWand: 0,
    ItemBase.UnearthedWand: 1,
    ItemBase.Buckler: 0,
    ItemBase.Defender: 0,
    ItemBase.RoundShield: 0,
    ItemBase.GrimShield: 0,
    ItemBase.TrollNest: 0,
    ItemBase.Monarch: 1,
    ItemBase.Luna: 0,
    ItemBase.BarbedShield: 0,
    ItemBase.BladeBarrier: 0,
    ItemBase.Scutum: 0,
    ItemBase.Aegis: 0,
    ItemBase.TrollNest: 0,
    ItemBase.DragonShield: 0,
    ItemBase.Ward: 0,
    ItemBase.ZakarumShield: 1,
    ItemBase.SacredRondache: 0,
    ItemBase.GildedShield: 1,
    ItemBase.WingedAxe: 1,
    ItemBase.WingedKnife: 1,
    ItemBase.FlyingAxe: 0,
    ItemBase.Scourge: 1,
    ItemBase.BoneKnife: 0,
    ItemBase.Dagger: 0,
    ItemBase.ThunderMaul: 0,
    ItemBase.LegendaryMallet: 1,
    ItemBase.Tulwar: 0,
    ItemBase.PhaseBlade: 0,
    ItemBase.ElderStaff: 0,
    ItemBase.ArchonStaff: 1,
    ItemBase.QuarterStaff: 1,
    ItemBase.DivineScepter: 0,
    ItemBase.MightyScepter: 1,
    ItemBase.EttinAxe: 1,
    ItemBase.DimensionalShard: 1,
    ItemBase.EldritchOrb: 1,
    ItemBase.SwirlingCrystal: 0,
    ItemBase.Thresher: 1,
    ItemBase.CrypticAxe: 1,
    ItemBase.OgreAxe: 0,
    ItemBase.MatriarchalJavelin: 0,
    ItemBase.CeremonialJavelin: 1,
    ItemBase.HydraBow: 1,
    ItemBase.CeremonialBow: 0,
    ItemBase.MatriarchalBow: 0,
    ItemBase.BattleCestus: 0,
    ItemBase.GreaterTalons: 0,
    ItemBase.WristSword: 0,
    ItemBase.FeralClaws: 0,
}

SET_ITEMS = {
    ItemBase.Amulet: 0,
    ItemBase.Ring: 0,
    ItemBase.BattleBoots: 0,
    ItemBase.HuntersGuise: 0,
    ItemBase.ShadowPlate: 0,
    ItemBase.MythicalSword: 0,
    ItemBase.OrnatePlate: 0,
    ItemBase.Caduceus: 1,
    ItemBase.VortexShield: 0,
    ItemBase.OrnatePlate: 0,
    ItemBase.WingedHelm: 0,
    ItemBase.RoundShield: 0,
    ItemBase.SacredArmor: 1,
    ItemBase.AvengerGuard: 0,
    ItemBase.WarGauntlets: 0,
    ItemBase.WarBoots: 0,
    ItemBase.OgreMaul: 0,
    ItemBase.WarBelt: 0,
    ItemBase.BrambleMitts: 0,
    ItemBase.GrandMatronBow: 0,
    ItemBase.Diadem: 0,
    ItemBase.KrakenShell: 0,
    ItemBase.BattleGauntlets: 0,
    ItemBase.SharkskinBelt: 0,
    ItemBase.MeshBoots: 0,
    ItemBase.LoricatedMail: 0,
    ItemBase.ScissorsSuwayyah: 0,
    ItemBase.GrimHelm: 0,
    ItemBase.SwirlingCrystal: 0,
    ItemBase.MeshBelt: 0,
    ItemBase.LacqueredPlate: 2,
    ItemBase.DeathMask: 0,
    ItemBase.HeavyBracers: 0,
    ItemBase.TrollBelt: 1,
    ItemBase.CantorTrophy: 0,
    ItemBase.BoneVisage: 0,
    ItemBase.ChaosArmor: 0,
    ItemBase.ChainGloves: 0,
}

MAGIC_ITEMS = {
    ItemBase.GrandCharm: 0,
    ItemBase.LargeCharm: 0,
    ItemBase.SmallCharm: 1,
    ItemBase.Jewel: 0,

    ItemBase.Monarch: 0,
}

RARE_ITEMS = {
    ItemBase.Jewel: 1,
}

SUPERIOR_ITEMS = {
    (ItemBase.MagePlate, 4): 1,
    (ItemBase.MagePlate, 3): 1,
    (ItemBase.MagePlate, 0): 1,
    (ItemBase.ArchonPlate, 4): 1,
    (ItemBase.ArchonPlate, 3): 1,
    (ItemBase.ArchonPlate, 0): 1,
    (ItemBase.DuskShroud, 4): 1,
    (ItemBase.DuskShroud, 3): 1,
    (ItemBase.DuskShroud, 0): 1,

    (ItemBase.PhaseBlade, 6): 1,
    (ItemBase.PhaseBlade, 5): 1,
    (ItemBase.PhaseBlade, 0): 1,
    (ItemBase.ColossusSword, 5): 1,
    (ItemBase.ColossusSword, 0): 1,
}

NORMAL_ITEMS = {
    (ItemBase.MagePlate, 3): 0,
    (ItemBase.MagePlate, 0): 1,

    (ItemBase.PhaseBlade, 6): 0,
    (ItemBase.PhaseBlade, 5): 1,
    (ItemBase.PhaseBlade, 0): 0,
    (ItemBase.ColossusBlade, 6): 0,
    (ItemBase.ColossusBlade, 5): 0,
    (ItemBase.ColossusBlade, 0): 0,
    (ItemBase.ColossusSword, 5): 1,
    (ItemBase.ColossusSword, 0): 1,
}

SUPERIOR_ETH_ITEMS = {
    (ItemBase.LacqueredPlate, 4): 1,
    (ItemBase.LacqueredPlate, 3): 1,
    (ItemBase.LacqueredPlate, 0): 1,
    (ItemBase.SacredArmor, 4): 1,
    (ItemBase.SacredArmor, 3): 1,
    (ItemBase.SacredArmor, 0): 1,
    (ItemBase.ArchonPlate, 4): 1,
    (ItemBase.ArchonPlate, 3): 1,
    (ItemBase.ArchonPlate, 0): 1,
    (ItemBase.GreatHauberk, 4): 1,
    (ItemBase.GreatHauberk, 3): 1,
    (ItemBase.GreatHauberk, 0): 1,
    (ItemBase.Wyrmhide, 4): 1,
    (ItemBase.Wyrmhide, 3): 1,
    (ItemBase.Wyrmhide, 0): 1,
    (ItemBase.DuskShroud, 4): 1,
    (ItemBase.DuskShroud, 3): 1,
    (ItemBase.DuskShroud, 0): 1,

    (ItemBase.Thresher, 4): 1,
    (ItemBase.Thresher, 0): 0,
    (ItemBase.GreatPoleaxe, 4): 1,
    (ItemBase.GreatPoleaxe, 0): 0,
    (ItemBase.GiantThresher, 4): 1,
    (ItemBase.GiantThresher, 0): 0,
    (ItemBase.CrypticAxe, 4): 1,
    (ItemBase.CrypticAxe, 0): 0,
    (ItemBase.ColossusVoulge, 4): 0,
    (ItemBase.ColossusVoulge, 0): 0,

    (ItemBase.ColossusBlade, 6): 1,
    (ItemBase.ColossusBlade, 5): 0,
    (ItemBase.ColossusBlade, 0): 1,
    (ItemBase.ColossusSword, 5): 0,
    (ItemBase.ColossusSword, 0): 0,
}

NORMAL_ETH_ITEMS = {
    (ItemBase.LacqueredPlate, 4): 0,
    (ItemBase.LacqueredPlate, 3): 0,
    (ItemBase.LacqueredPlate, 0): 0,
    (ItemBase.SacredArmor, 4): 0,
    (ItemBase.SacredArmor, 3): 0,
    (ItemBase.SacredArmor, 0): 0,
    (ItemBase.ArchonPlate, 4): 0,
    (ItemBase.ArchonPlate, 3): 0,
    (ItemBase.ArchonPlate, 0): 0,
    (ItemBase.GreatHauberk, 4): 0,
    (ItemBase.GreatHauberk, 3): 0,
    (ItemBase.GreatHauberk, 0): 0,
    (ItemBase.Wyrmhide, 4): 0,
    (ItemBase.Wyrmhide, 3): 0,
    (ItemBase.Wyrmhide, 0): 0,
    (ItemBase.DuskShroud, 4): 0,
    (ItemBase.DuskShroud, 3): 0,
    (ItemBase.DuskShroud, 0): 0,
    
    (ItemBase.Thresher, 4): 1,
    (ItemBase.Thresher, 0): 1,
    (ItemBase.GreatPoleaxe, 4): 1,
    (ItemBase.GreatPoleaxe, 0): 1,
    (ItemBase.GiantThresher, 4): 1,
    (ItemBase.GiantThresher, 0): 1,
    (ItemBase.CrypticAxe, 4): 1,
    (ItemBase.CrypticAxe, 0): 1,
    (ItemBase.ColossusVoulge, 4): 0,
    (ItemBase.ColossusVoulge, 0): 0,
    (ItemBase.ColossusBlade, 6): 0,
    (ItemBase.ColossusBlade, 5): 0,
    (ItemBase.ColossusBlade, 0): 0,
    (ItemBase.ColossusSword, 5): 0,
    (ItemBase.ColossusSword, 0): 0,
}

def get_pickit_priority(item: dict, potion_needs: dict = None):
    result = 0
    if item and type(item) is dict:
        base_item = item["base_item"]
        quality = item["quality"]
        num_sockets = item["num_sockets"]
        socket_key = (base_item, num_sockets)
        is_eth = ItemFlag.Ethereal in item["flags"]
        
        # Runes, gems
        if base_item in BASIC_ITEMS:
            result = BASIC_ITEMS[base_item]

        # Unique, set, magic, rare
        elif quality == ItemQuality.Unique and base_item in UNIQUE_ITEMS:
            result = UNIQUE_ITEMS[base_item]
        elif quality == ItemQuality.Set and base_item in SET_ITEMS:
            result = SET_ITEMS[base_item]
        elif quality == ItemQuality.Magic and base_item in MAGIC_ITEMS:
            result = MAGIC_ITEMS[base_item]
        elif quality == ItemQuality.Rare and base_item in RARE_ITEMS:
            result = RARE_ITEMS[base_item]

        # Socketed items, non-eth
        elif not is_eth and quality == ItemQuality.Superior and socket_key in SUPERIOR_ITEMS:
            result = SUPERIOR_ITEMS[socket_key]
        elif not is_eth and quality == ItemQuality.Normal and socket_key in NORMAL_ITEMS:
            result = NORMAL_ITEMS[socket_key]
        
        # Socketed items, eth
        elif is_eth and quality == ItemQuality.Superior and socket_key in SUPERIOR_ETH_ITEMS:
            result = SUPERIOR_ETH_ITEMS[socket_key]
        elif is_eth and quality == ItemQuality.Normal and socket_key in NORMAL_ETH_ITEMS:
            result = NORMAL_ETH_ITEMS[socket_key]
        elif potion_needs is not None:
            if "Rejuv" in base_item and potion_needs["rejuv"] > 0 and base_item in POTIONS:
                result = POTIONS[base_item] > 0 and "Rejuv" in base_item
            if "Heal" in base_item and potion_needs["health"] > 0 and base_item in POTIONS:
                result = POTIONS[base_item] > 0 and "Heal" in base_item
            if "Mana" in base_item and potion_needs["mana"] > 0 and base_item in POTIONS:
                result = POTIONS[base_item] > 0 and "Mana" in base_item
    return result
