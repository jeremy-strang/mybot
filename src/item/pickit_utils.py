from item.pickit_item import PickitItem
from item.pickit_types import *
from item.pickit_config import *

import pprint
pp = pprint.PrettyPrinter(depth=6)


def _parse_pickit_action(opt: Union[Action, tuple, bool], is_eth: bool = False) -> Action:
    result = Action.DontKeep
    if type(opt) is tuple:
        if len(opt) >= 2:
            action = opt[0]
            eth_option = opt[1]
            if eth_option == EthOption.Any:
                result = action
            elif eth_option == EthOption.EthOnly and is_eth:
                result = action
            elif eth_option == EthOption.NonEthOnly and not is_eth:
                result = action
        elif len(opt) == 1:
            result = opt[0]
    elif type(opt) is bool:
        return Action.Keep if opt else Action.DontKeep
    else:
        result = opt
    return result

def get_pickit_action(item: dict, config: PickitConfig, potion_needs: dict = None) -> Action:
    result = Action.DontKeep
    if config is not None and item is not None and type(item) is dict:
        item_type = item["type"]
        quality = item["quality"]
        type_quality = (item_type, quality)
        is_eth = Flag.Ethereal in item["flags"]

        # Runes, gems
        if item_type in config.BasicItems:
            result = config.BasicItems[item_type]
            
        # Unique, set, magic, rare (to remain unidentified)
        elif quality <= Quality.Superior and item_type in config.NormalItems:
            rules = config.NormalItems[item_type]
            item_obj = PickitItem(item)
            pp.pprint(item)
            for rule in rules:
                match = rule(item_obj)
                act = _parse_pickit_action(match)
                print(f"   item: {item_type}, quality: {item_obj.quality}, match: {match}, name: {item_obj.name} sock: {item_obj.sockets}")
                if act > result:
                    result = act
                    break
        
        # Potions
        elif potion_needs is not None and item_type in config.ConsumableItems:
            if "Rejuv" in item_type and potion_needs["rejuv"] >= Action.Keep:
                result = config.ConsumableItems[item_type] >= Action.Keep and "Rejuv" in item_type
            if "Heal" in item_type and potion_needs["health"] >= Action.Keep:
                result = config.ConsumableItems[item_type] >= Action.Keep and "Heal" in item_type
            if "Mana" in item_type and potion_needs["mana"] >= Action.Keep:
                result = config.ConsumableItems[item_type] >= Action.Keep and "Mana" in item_type

        # Unique, set, magic, rare (to remain unidentified)
        elif type_quality in config.MagicItems:
            result = _parse_pickit_action(config.MagicItems[type_quality], is_eth)

        # Check if it's an item we want to identify
        if type_quality in config.IdentifiedItems:
            # If it's identified, evaluate the rules for it and see if any of them pass
            if item["is_identified"]:
                result = Action.DontKeep
                item_obj = PickitItem(item)
                for rule in config.IdentifiedItems[type_quality]:
                    ptype = Action.KeepAndNotify if rule(item_obj) else Action.DontKeep
                    if ptype > result:
                        result = ptype
                    if ptype > Action.Keep:
                        break
            # Otherwise keep it for now, we will ID it later
            else:
                result = Action.Keep
    return result
