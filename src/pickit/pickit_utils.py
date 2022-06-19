import enum
import sys
from typing import Union

import numpy as np
from game_stats import GameStats
from logger import Logger
from pickit.pickit_item import PickitItem
from pickit.item_types import *
from utils.misc import is_in_roi, point_str

sys.path.insert(0, "./config")
from pickit_default import PickitConfig

import pprint
pp = pprint.PrettyPrinter(depth=6)

LOW_PRIORITY_ITEMS = set([
    Item.Arrows,
    Item.Bolts,
    Item.SuperHealingPotion,
    Item.GreaterHealingPotion,
    Item.HealingPotion,
    Item.LightHealingPotion,
    Item.MinorHealingPotion,
    Item.SuperManaPotion,
    Item.GreaterManaPotion,
    Item.ManaPotion,
    Item.LightManaPotion,
    Item.MinorManaPotion,
    Item.FullRejuvenationPotion,
    Item.RejuvenationPotion,
    Item.Gold,
    Item.Key,
    Item.ScrollOfIdentify,
    Item.ScrollOfTownPortal,
])

def _parse_pickit_action(opt: Union[Action, tuple[Action, Options], bool], item: dict = None, game_stats: GameStats = None) -> Action:
    result: Action = Action.DontKeep
    if type(opt) is tuple:
        if len(opt) >= 2:
            action: Action = opt[0] if type(opt[0]) is Action else Action(opt[0])
            options = opt[1]
            if options.eth != None:
                is_eth = item != None and item["is_ethereal"]
                if options.eth == EthOption.Any:
                    result = action
                elif options.eth == EthOption.EthOnly and is_eth:
                    result = action
                elif options.eth == EthOption.NonEthOnly and not is_eth:
                    result = action
                Logger.debug(f"    Evaluating eth option {options.eth}, item is eth: {is_eth}, result: {result}")
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
        item_class = ITEM_CLASSES[item_type] if item_type in ITEM_CLASSES else None
        quality = item["quality"]
        type_quality = (item_type, quality)
        class_quality = (item_class, quality) if item_class is not None else None
        

        # Runes, gems
        if item_type in config.BasicItems:
            result = _parse_pickit_action(config.BasicItems[item_type], item, game_stats=game_stats)
            
        # Unique, set, magic, rare (to remain unidentified)
        elif quality <= Quality.Superior and (item_type in config.NormalItems or item_class in config.NormalItems):
            rules = []
            if item_type in config.NormalItems:
                rules += config.NormalItems[item_type]
            if item_class is not None and item_class in config.NormalItems:
                rules += config.NormalItems[item_class]
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
        id_rules = []
        if type_quality in config.IdentifiedItems:
            id_rules += config.IdentifiedItems[type_quality]
            # Logger.debug(f"    Evaluating {len(config.IdentifiedItems[type_quality])} rules for item type and quality {type_quality}...")
        if class_quality is not None and class_quality in config.IdentifiedItems:
            id_rules += config.IdentifiedItems[class_quality]
            # Logger.debug(f"    Evaluating {len(config.IdentifiedItems[class_quality])} rules for item class and quality {class_quality}...")
        if len(id_rules) > 0:
            # If it's identified, evaluate the rules for it and see if any of them pass
            result = Action.DontKeep
            if item["is_identified"]:
                result = Action.DontKeep
                item_obj = PickitItem(item)
                for i, rule in enumerate(id_rules):
                    rule_result = rule(item_obj)
                    action = Action.Keep if type(rule_result) is bool and rule_result else Action(rule_result)
                    # Logger.debug(f"        Result of rule number {i}: result={rule_result}, action={action}")
                    # Logger.debug(f"             action: {action}, type(action): {type(action)}, result: {result}, type(result): {type(result)}")
                    if action > result:
                        result = action
                    if action >= Action.KeepAndNotify:
                        break
            # Otherwise keep it for now, we will ID it later
            else:
                result = Action.Keep
        
        # if item_type not in LOW_PRIORITY_ITEMS:
        #     if result >= Action.Keep: Logger.debug("-" * 80)
        #     Logger.debug(f"--Evaluated {Quality(quality).name} {item_type}, result: {result}")
        #     if result >= Action.Keep: Logger.debug("-" * 80)
    return result

def get_free_inventory_space(inventory_items: list[dict], num_loot_columns: int = 10):
    inventory = np.zeros((4, 10)) + 1
    for j in range(num_loot_columns, 10):
        inventory[0, j] = 0
        inventory[1, j] = 0
        inventory[2, j] = 0
        inventory[3, j] = 0

    looted_item_count = 0
    for item in inventory_items:
        x, y = item["position"]
        w, h = ITEM_DIMENSIONS[item["type"]] if item["type"] in ITEM_DIMENSIONS else (1, 1)
        if item and is_in_roi([-1, -1, num_loot_columns + 1, 4], item["position"]):
            looted_item_count += 1
            for i in range(x, x + w):
                for j in range(y, y + h):
                    inventory[j, i] = 0
    free_column_count = 0
    free_slot_count = 40 - np.sum(inventory)
    for j in range(0, num_loot_columns):
        if inventory[j, 0] == inventory[j, 1] == inventory[j, 2] == inventory[j, 3] == 1:
            free_column_count += 1
    Logger.debug(f"Computed inventory space with {looted_item_count} items in {num_loot_columns} loot columns: {free_slot_count} 1x1 slots, {free_column_count} free full columns")
    return (free_slot_count, free_column_count)
