from item.enums import Item, ItemQuality, ItemMode, InventoryPage, BodyLoc, StashType, ItemFlag

BASIC_ITEMS = {
    Item.ElRune: 0,
    Item.EldRune: 0,
    Item.TirRune: 0,
    Item.NefRune: 0,
    Item.EthRune: 0,
    Item.IthRune: 0,
    Item.TalRune: 0,
    Item.RalRune: 0,
    Item.OrtRune: 0,
    Item.ThulRune: 0,
    Item.AmnRune: 0,
    Item.SolRune: 0,
    Item.ShaelRune: 0,
    Item.DolRune: 0,
    Item.HelRune: 0,
    Item.IoRune: 0,
    Item.LumRune: 0,
    Item.KoRune: 0,
    Item.FalRune: 0,

    Item.LemRune: 1,
    Item.PulRune: 1,
    Item.UmRune: 1,
    Item.MalRune: 1,
    Item.IstRune: 1,
    Item.GulRune: 1,

    Item.VexRune: 2,
    Item.OhmRune: 2,
    Item.LoRune: 2,
    Item.SurRune: 2,
    Item.BerRune: 2,
    Item.JahRune: 2,
    Item.ChamRune: 2,
    Item.ZodRune: 2,

    Item.ChippedAmethyst: 0,
    Item.ChippedTopaz: 0,
    Item.ChippedSapphire: 0,
    Item.ChippedEmerald: 0,
    Item.ChippedRuby: 0,
    Item.ChippedDiamond: 0,

    Item.FlawedAmethyst: 0,
    Item.FlawedTopaz: 0,
    Item.FlawedSapphire: 0,
    Item.FlawedEmerald: 0,
    Item.FlawedRuby: 0,
    Item.FlawedDiamond: 0,

    Item.Amethyst: 1,
    Item.Topaz: 1,
    Item.Sapphire: 0,
    Item.Emerald: 0,
    Item.Ruby: 0,
    Item.Diamond: 0,

    Item.FlawlessAmethyst: 0,
    Item.FlawlessTopaz: 0,
    Item.FlawlessSapphire: 0,
    Item.FlawlessEmerald: 0,
    Item.FlawlessRuby: 0,
    Item.FlawlessDiamond: 0,

    Item.PerfectAmethyst: 1,
    Item.PerfectTopaz: 1,
    Item.PerfectSapphire: 1,
    Item.PerfectEmerald: 1,
    Item.PerfectRuby: 1,
    Item.PerfectDiamond: 1,
}

UNIQUE_ITEMS = {
    Item.GrandCharm: 1,
    Item.SmallCharm: 1,
    Item.Amulet: 1,
    Item.Ring: 1,
    Item.Jewel: 1,

    Item.Shako: 1,
    Item.Diadem: 2,
    Item.SacredArmor: 2,
    Item.DemonHead: 1,
    Item.GildedShield: 1,
    Item.SerpentskinArmor: 1,
    Item.Monarch: 1,
    Item.BattleBoots: 1,
    Item.BalrogSkin: 1,
}

SET_ITEMS = {
    Item.LacqueredPlate: 1,
    Item.SacredArmor: 1,
    Item.BrambleMitts: 1,
}

MAGIC_ITEMS = {
    Item.GrandCharm: 1,
    Item.LargeCharm: 0,
    Item.SmallCharm: 1,
    Item.Jewel: 0,

    Item.Monarch: 0,
}

RARE_ITEMS = {
    Item.Jewel: 1,
}

SUPERIOR_ITEMS = {
    (Item.MagePlate, 4): 1,
    (Item.MagePlate, 3): 1,
    (Item.MagePlate, 0): 1,
    (Item.ArchonPlate, 4): 1,
    (Item.ArchonPlate, 3): 1,
    (Item.ArchonPlate, 0): 1,
    (Item.DuskShroud, 4): 1,
    (Item.DuskShroud, 3): 1,
    (Item.DuskShroud, 0): 1,

    (Item.PhaseBlade, 6): 1,
    (Item.PhaseBlade, 5): 1,
    (Item.PhaseBlade, 0): 1,
    (Item.ColossusSword, 5): 1,
    (Item.ColossusSword, 0): 1,
}

NORMAL_ITEMS = {
    (Item.MagePlate, 3): 0,
    (Item.MagePlate, 0): 1,

    (Item.PhaseBlade, 6): 0,
    (Item.PhaseBlade, 5): 1,
    (Item.PhaseBlade, 0): 0,
    (Item.ColossusBlade, 6): 0,
    (Item.ColossusBlade, 5): 0,
    (Item.ColossusBlade, 0): 0,
    (Item.ColossusSword, 5): 1,
    (Item.ColossusSword, 0): 1,
}

SUPERIOR_ETH_ITEMS = {
    (Item.LacqueredPlate, 4): 1,
    (Item.LacqueredPlate, 3): 1,
    (Item.LacqueredPlate, 0): 1,
    (Item.SacredArmor, 4): 1,
    (Item.SacredArmor, 3): 1,
    (Item.SacredArmor, 0): 1,
    (Item.ArchonPlate, 4): 1,
    (Item.ArchonPlate, 3): 1,
    (Item.ArchonPlate, 0): 1,
    (Item.GreatHauberk, 4): 1,
    (Item.GreatHauberk, 3): 1,
    (Item.GreatHauberk, 0): 1,
    (Item.Wyrmhide, 4): 1,
    (Item.Wyrmhide, 3): 1,
    (Item.Wyrmhide, 0): 1,
    (Item.DuskShroud, 4): 1,
    (Item.DuskShroud, 3): 1,
    (Item.DuskShroud, 0): 1,

    (Item.Thresher, 4): 1,
    (Item.Thresher, 0): 0,
    (Item.GreatPoleaxe, 4): 1,
    (Item.GreatPoleaxe, 0): 0,
    (Item.GiantThresher, 4): 1,
    (Item.GiantThresher, 0): 0,
    (Item.CrypticAxe, 4): 1,
    (Item.CrypticAxe, 0): 0,
    (Item.ColossusVoulge, 4): 0,
    (Item.ColossusVoulge, 0): 0,

    (Item.ColossusBlade, 6): 1,
    (Item.ColossusBlade, 5): 0,
    (Item.ColossusBlade, 0): 1,
    (Item.ColossusSword, 5): 0,
    (Item.ColossusSword, 0): 0,
}

NORMAL_ETH_ITEMS = {
    (Item.LacqueredPlate, 4): 0,
    (Item.LacqueredPlate, 3): 0,
    (Item.LacqueredPlate, 0): 0,
    (Item.SacredArmor, 4): 0,
    (Item.SacredArmor, 3): 0,
    (Item.SacredArmor, 0): 0,
    (Item.ArchonPlate, 4): 0,
    (Item.ArchonPlate, 3): 0,
    (Item.ArchonPlate, 0): 0,
    (Item.GreatHauberk, 4): 0,
    (Item.GreatHauberk, 3): 0,
    (Item.GreatHauberk, 0): 0,
    (Item.Wyrmhide, 4): 0,
    (Item.Wyrmhide, 3): 0,
    (Item.Wyrmhide, 0): 0,
    (Item.DuskShroud, 4): 0,
    (Item.DuskShroud, 3): 0,
    (Item.DuskShroud, 0): 0,
    
    (Item.Thresher, 4): 1,
    (Item.Thresher, 0): 1,
    (Item.GreatPoleaxe, 4): 1,
    (Item.GreatPoleaxe, 0): 1,
    (Item.GiantThresher, 4): 1,
    (Item.GiantThresher, 0): 1,
    (Item.CrypticAxe, 4): 1,
    (Item.CrypticAxe, 0): 1,
    (Item.ColossusVoulge, 4): 0,
    (Item.ColossusVoulge, 0): 0,
    (Item.ColossusBlade, 6): 0,
    (Item.ColossusBlade, 5): 0,
    (Item.ColossusBlade, 0): 0,
    (Item.ColossusSword, 5): 0,
    (Item.ColossusSword, 0): 0,
}

def get_pickit_priority(item: dict):
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

    return result
