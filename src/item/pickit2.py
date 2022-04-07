import re
import time
import keyboard
import cv2
from operator import itemgetter

from pytest import skip
from api.mapassist import MapAssistApi
from pathing import Pather

from utils.custom_mouse import mouse
from config import Config
from logger import Logger
from screen import Screen
from item import ItemFinder, Item
from ui import UiManager, belt_manager
from ui import BeltManager
from char import IChar
from item.pickit_utils import get_pickit_priority

class Pickit2:
    def __init__(self,
                 screen: Screen,
                 ui_manager: UiManager,
                 belt_manager: BeltManager,
                 char: IChar,
                 pather: Pather,
                 api: MapAssistApi,
                 ):
        self._screen = screen
        self._ui_manager = ui_manager
        self._belt_manager = belt_manager
        self._char = char
        self._pather = pather
        self._config = Config()
        self._last_closest_item: Item = None
        self._api = api
    
    def _next_item(self, potion_needs: dict = None, skip_ids: set = None) -> dict:
        data = self._api.data
        items_found = []
        if data is not None:
            for item in data["items"]:
                item_priority = get_pickit_priority(item, potion_needs)
                if item["item_mode"] == "ONGROUND" and item_priority > 0:
                    items_found.append(item)
            items_found = sorted(items_found, key = lambda item: item["dist"])
            items_found = sorted(items_found, key = lambda item: get_pickit_priority(item), reverse=True)
            if skip_ids is not None and len(skip_ids) > 0:
                items_found = list(filter(lambda x: x["id"] not in skip, items_found))
            if len(items_found) > 0:
                print("\nMemory pickit order:")
                for item in items_found:
                    print(f"    {item['name']}, dist: {item['dist']}, quality: {item['quality']}, base: {item['base_item']}")
        return items_found[0] if len(items_found) > 0 else None

    def pick_up_items(self, time_out: float = 22, skip_nopickup: bool = False) -> bool:
        start = time.time()
        elapsed = 0
        attempts = 0
        disabled_nopickup = False
        did_time_out = False
        picked_up_items = []
        skipped_ids = set()
        self._belt_manager.update_pot_needs()
        potion_needs = self._belt_manager.get_pot_needs()
        item = self._next_item(potion_needs)
        last_id = item["id"] if item else 0

        if item and not skip_nopickup:
            Logger.info(f"\n{'*'*80}\nMemory pickit found items, disabling /nopickup...")
            self._ui_manager.disable_no_pickup()
            disabled_nopickup = True
        while item and not did_time_out:
            elapsed = time.time() - start
            if elapsed >= time_out:
                did_time_out = True
                Logger.warning(f"Timed out during memory pickit after {elapsed}/{time_out} sec, skipping it this time...")
                break

            if item["id"] == last_id:
                attempts += 1
                if attempts >= 4:
                    if item and not is_potion:
                        skipped_ids.add(item["id"])
                    attempts = 0
                    item = self._next_item(potion_needs, skipped_ids)
                    continue

            last_id = item["id"]
            Logger.info(f"    Picking up {item['name']} (ID: {item['id']}), quality: {item['quality']}...")
            is_potion = "Potion" in item["name"]
            if self._pather.click_item(item, self._char):
                picked_up_items.append(item)
                if is_potion:
                    self._belt_manager.picked_up_pot(item["name"])
            item = self._next_item(potion_needs, skipped_ids)

        if disabled_nopickup:
            Logger.info(f"    Re-enabling /nopickup...")
            self._ui_manager.enable_no_pickup()
            Logger.info(f"    Done picking up {len(picked_up_items)} items\n{'*'*80}")

        return (picked_up_items, list(skipped_ids))
        #     # Check if we need to pick up certain pots more pots
        #     need_pots = self._belt_manager.get_pot_needs()
        #     if need_pots["mana"] <= 0:
        #         item_list = [x for x in item_list if "mana_potion" not in x.name]
        #     if need_pots["health"] <= 0:
        #         item_list = [x for x in item_list if "healing_potion" not in x.name]
        #     if need_pots["rejuv"] <= 0:
        #         item_list = [x for x in item_list if "rejuvenation_potion" not in x.name]

        #     # TODO: Hacky solution for trav only gold pickup, hope we can soon read gold ammount and filter by that...
        #     if self._config.char["gold_trav_only"] and not is_at_trav:
        #         item_list = [x for x in item_list if "misc_gold" not in x.name]

        #     if len(item_list) == 0:
        #         # if twice no item was found, break
        #         found_nothing += 1
        #         if found_nothing > 1:
        #             break
        #         else:
        #             # Maybe we need to move cursor to another position to avoid highlighting items
        #             pos_m = self._screen.convert_abs_to_monitor((0, 0))
        #             mouse.move(*pos_m, randomize=[90, 160])
        #             time.sleep(0.2)
        #     else:
        #         found_nothing = 0

        #         item_list.sort(key=itemgetter('dist'))
        #         closest_item = next((obj for obj in item_list if "misc_gold" not in obj["name"]), None)
        #         if not closest_item:
        #             closest_item = item_list[0]

        #         #this needs to be tested
        #         #closest_item = item_list[0]
        #         #for item in item_list[1:]:
        #             # if we're looting Trav as a non-teleporter, we need to spend less time stuck on
        #             # stuff like gold because we're gonna be looting multiple times from a few different positions
        #         #    if closest_item.dist > item.dist and not \
        #         #        (is_at_trav and not char.can_teleport() and item.name in skip_items):
        #         #        closest_item = item


        #         # check if we trying to pickup the same item for a longer period of time
        #         force_move = False
        #         if curr_item_to_pick is not None:
        #             is_same_item = (curr_item_to_pick.name == closest_item.name and \
        #                 abs(curr_item_to_pick.dist - closest_item.dist) < 20)
        #             if same_item_timer is None or not is_same_item:
        #                 same_item_timer = time.time()
        #                 did_force_move = False
        #             elif time.time() - same_item_timer > 1 and not did_force_move:
        #                 force_move = True
        #                 did_force_move = True
        #             elif time.time() - same_item_timer > 3:
        #                 # backlist this item type for this pickit round
        #                 Logger.warning(f"Could not pick up: {closest_item.name}. Continue with other items")
        #                 skip_items.append(closest_item.name)
        #         curr_item_to_pick = closest_item

        #         # To avoid endless teleport or telekinesis loop
        #         force_pick_up = char.capabilities.can_teleport_natively and \
        #                         self._last_closest_item is not None and \
        #                         self._last_closest_item.name == closest_item.name and \
        #                         abs(self._last_closest_item.dist - closest_item.dist) < 20

        #         x_m, y_m = self._screen.convert_screen_to_monitor(closest_item.center)
        #         if not force_move and (closest_item.dist < self._config.ui_pos["item_dist"] or force_pick_up):
        #             self._last_closest_item = None
        #             # if potion is picked up, record it in the belt manager
        #             if "potion" in closest_item.name:
        #                 self._belt_manager.picked_up_pot(closest_item.name)
        #             # no need to stash potions, scrolls, or gold
        #             if "potion" not in closest_item.name and "tp_scroll" != closest_item.name and "misc_gold" not in closest_item.name:
        #                 found_items = True

        #             prev_cast_start = char.pick_up_item((x_m, y_m), item_name=closest_item.name, prev_cast_start=prev_cast_start)
        #             if not char.capabilities.can_teleport_natively:
        #                 time.sleep(0.2)

        #             if self._ui_manager.is_overburdened():
        #                 found_items = True
        #                 Logger.warning("Inventory full, skipping pickit!")
        #                 self._ui_manager.throw_out_junk(self._item_finder)
        #                 # throw out junk and check again
        #             if self._ui_manager.is_overburdened():
        #                 found_items = True
        #                 Logger.warning("Inventory full, skipping pickit!")
        #                 break
        #             else:
        #                 # send log to discord
        #                 if found_items and closest_item.name not in picked_up_items:
        #                     Logger.info(f"Picking up: {closest_item.name} ({closest_item.score*100:.1f}% confidence)")
        #                 picked_up_items.append(closest_item.name)
        #         else:
        #             char.pre_move()
        #             char.move((x_m, y_m), force_move=True)
        #             if not char.capabilities.can_teleport_natively:
        #                 time.sleep(0.3)
        #             time.sleep(0.2)
        #             # save closeset item for next time to check potential endless loops of not reaching it or of telekinsis/teleport
        #             self._last_closest_item = closest_item
        # keyboard.send(self._config.char["show_items"])
        # elapsed = round(time.time() - start, 1)
        # Logger.debug(f"Done picking {len(picked_up_items)} up items in {elapsed} seconds")
        # return found_items

