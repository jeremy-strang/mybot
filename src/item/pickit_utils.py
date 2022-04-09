from item.pickit_item import PickitItem
from item.types import *
from item.pickit_config import *

def get_pickit_priority(item: dict, config: PickitConfig, potion_needs: dict = None):
    result = PickitType.DontKeep
    if config is not None and item is not None and type(item) is dict:
        item_type = item["type"]
        quality = item["quality"]
        type_quality = (item_type, quality)

        # Runes, gems
        if item_type in config.BasicItems:
            result = config.BasicItems[item_type]
            
        # Unique, set, magic, rare (to remain unidentified)
        elif quality <= ItemQuality.Superior and item_type in config.NormalItems:
            rules = config.NormalItems[item_type]
            for rule in rules:
                is_match = rule(item)
                if is_match:
                    result = PickitType.Keep
        
        # Potions
        elif potion_needs is not None and item_type in config.ConsumableItems:
            if "Rejuv" in item_type and potion_needs["rejuv"] >= PickitType.Keep:
                result = config.ConsumableItems[item_type] >= PickitType.Keep and "Rejuv" in item_type
            if "Heal" in item_type and potion_needs["health"] >= PickitType.Keep:
                result = config.ConsumableItems[item_type] >= PickitType.Keep and "Heal" in item_type
            if "Mana" in item_type and potion_needs["mana"] >= PickitType.Keep:
                result = config.ConsumableItems[item_type] >= PickitType.Keep and "Mana" in item_type

        # Unique, set, magic, rare (to remain unidentified)
        elif type_quality in config.MagicItems:
            result = config.MagicItems[type_quality]

        # Check if it's an item we want to identify
        if type_quality in config.IdentifiedItems:
            # If it's identified, evaluate the rules for it and see if any of them pass
            if item["is_identified"]:
                result = PickitType.DontKeep
                item_obj = PickitItem(item)
                for rule in config.IdentifiedItems[type_quality]:
                    ptype = PickitType.KeepAndNotify if rule(item_obj) else PickitType.DontKeep
                    if ptype > result:
                        result = ptype
                    if ptype > PickitType.Keep:
                        break
            # Otherwise keep it for now, we will ID it later
            else:
                result = PickitType.Keep
    return result
