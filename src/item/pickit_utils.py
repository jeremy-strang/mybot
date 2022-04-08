from item.pickit_item import PickitItem
from item.types import ItemType, ItemQuality, ItemMode, InventoryPage, BodyLoc, StashType, ItemFlag
from item.pickit_config import *

def get_pickit_priority(item: dict, potion_needs: dict = None):
    result = 0
    if item and type(item) is dict:
        item_type = item["type"]
        quality = item["quality"]
        num_sockets = item["num_sockets"]
        socket_key = (item_type, num_sockets)
        is_eth = ItemFlag.Ethereal in item["flags"]

        # Runes, gems
        if item_type in BASIC_ITEMS:
            result = BASIC_ITEMS[item_type]

        # Unique, set, magic, rare
        elif quality == ItemQuality.Unique and item_type in UNIQUE_ITEMS:
            result = UNIQUE_ITEMS[item_type]
        elif quality == ItemQuality.Set and item_type in SET_ITEMS:
            result = SET_ITEMS[item_type]
        elif quality == ItemQuality.Magic and item_type in MAGIC_ITEMS:
            result = MAGIC_ITEMS[item_type]
        elif quality == ItemQuality.Rare and item_type in RARE_ITEMS:
            result = RARE_ITEMS[item_type]

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
            if "Rejuv" in item_type and potion_needs["rejuv"] > 0 and item_type in POTIONS:
                result = POTIONS[item_type] > 0 and "Rejuv" in item_type
            if "Heal" in item_type and potion_needs["health"] > 0 and item_type in POTIONS:
                result = POTIONS[item_type] > 0 and "Heal" in item_type
            if "Mana" in item_type and potion_needs["mana"] > 0 and item_type in POTIONS:
                result = POTIONS[item_type] > 0 and "Mana" in item_type

        # Check if it's an item we want to identify
        type_quality = (item_type, quality)
        if type_quality in IDENTIFIED_ITEMS:
            # If it's identified, evaluate the rules for it and see if any of them pass
            if item["is_identified"]:
                result = 0
                item_obj = PickitItem(item)
                for rule in IDENTIFIED_ITEMS[type_quality]:
                    prio = 2 if rule(item_obj) else 0
                    if prio > result:
                        result = prio
                    if prio > 1:
                        break
            # Otherwise keep it for now, we will ID it later
            else:
                result = 1
    return result
