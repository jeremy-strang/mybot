import sys
from typing import Union
from game_stats import GameStats
from logger import Logger
from pickit.pickit_item import PickitItem
from pickit.types import *

sys.path.insert(0, "./config")
from pickit_default import PickitConfig

import pprint
pp = pprint.PrettyPrinter(depth=6)

def _parse_pickit_action(opt: Union[Action, tuple[Action, Options], bool], item: dict = None, game_stats: GameStats = None) -> Action:
    result: Action = Action.DontKeep
    if type(opt) is tuple:
        if len(opt) >= 2:
            action: Action = opt[0] if type(opt[0]) is Action else Action(opt[0])
            options = opt[1]
            if options.eth != None:
                is_eth = item != None and not item["is_ethereal"]
                if options.eth == EthOption.Any:
                    result = action
                elif options == EthOption.EthOnly and is_eth:
                    result = action
                elif options == EthOption.NonEthOnly and not is_eth:
                    result = action
            # Logger.debug(f"parsing item {item['name']}, options.max_quantity: {options.max_quantity}, game_stats.kept_item_quanties[item['name']]: {game_stats.kept_item_quanties[item['name']]}")
            if options.min_defense != None and item["defense"] < options.min_defense:
                result = Action.DontKeep
            if result != Action.DontKeep and options.max_quantity is not None and game_stats is not None \
                and item["name"] in game_stats.kept_item_quanties and game_stats.kept_item_quanties[item["name"]] >= options.max_quantity:
                result = Action.DontKeep
        elif len(opt) == 1:
            result = opt[0] if type(opt[0]) is Action else Action(opt[0])
    elif type(opt) is bool:
        return Action.Keep if opt else Action.DontKeep
    else:
        result = opt if type(opt) is Action else Action(opt)
    return result

def get_pickit_action(item: dict, config: PickitConfig, potion_needs: dict = None, game_stats: GameStats = None) -> Action:
    # pp.pprint(item)
    result = Action.DontKeep
    if config is not None and item is not None and type(item) is dict:
        item_type = item["type"]
        quality = item["quality"]
        type_quality = (item_type, quality)
        # Runes, gems
        if item_type in config.BasicItems:
            result = _parse_pickit_action(config.BasicItems[item_type], item, game_stats=game_stats)
            
        # Unique, set, magic, rare (to remain unidentified)
        elif quality <= Quality.Superior and item_type in config.NormalItems:
            rules = config.NormalItems[item_type]
            item_obj = PickitItem(item)
            for rule in rules:
                match = rule(item_obj)
                act = _parse_pickit_action(match, game_stats=game_stats)
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
        elif type_quality in config.UnidentifiedItems:
            result = _parse_pickit_action(config.UnidentifiedItems[type_quality], item, game_stats=game_stats)

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
