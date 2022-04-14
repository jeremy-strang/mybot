import time
import keyboard
import cv2
from operator import itemgetter
from d2r.d2r_api import D2rApi
from game_stats import GameStats
from pickit.pickit import Pickit
from pathing import Pather

from utils.custom_mouse import mouse
from config import Config
from logger import Logger
from screen import Screen
from pickit import ItemFinder, PixelItem
from ui import UiManager
from ui import BeltManager
from char import IChar

class PixelPickit:
    def __init__(self,
                 screen: Screen,
                 item_finder: ItemFinder,
                 ui_manager: UiManager,
                 belt_manager: BeltManager,
                 api: D2rApi,
                 char: IChar,
                 pather: Pather,
                 game_stats: GameStats,
                 ):
        self._item_finder = item_finder
        self._screen = screen
        self._belt_manager = belt_manager
        self._ui_manager = ui_manager
        self._config = Config()
        self._last_closest_item: PixelItem = None
        self._api = api
        self._char = char
        self._pather = pather
        self._pickit2 = Pickit(screen, ui_manager, belt_manager, char, pather, api, game_stats)

    def take_loot_screenshot(self):
        #Creating a screenshot of the current loot
        if self._config.general["loot_screenshots"]:
            img = self._screen.grab()
            cv2.imwrite("./loot_screenshots/info_debug_drop_" + time.strftime("%Y%m%d_%H%M%S") + ".png", img)
            Logger.debug("Took a screenshot of current loot")

    def pick_up_items(self, char: IChar, is_at_trav: bool = False, time_out: float = 22, skip_nopickup: bool = False) -> bool:
        """
        Pick up all items with specified char
        :param char: The character used to pick up the item
        :param is_at_trav: Dirty hack to reduce gold pickup only to trav area, should be removed once we can determine the amount of gold reliably
        :return: Bool if any items were picked up or not. (Does not account for picking up scrolls and pots)
        """
        picked_up_items, skipped_items = self._pickit2.pick_up_items(time_out, skip_nopickup)
        found_items = len(picked_up_items) > 0
        if len(skipped_items) == 0:
            Logger.debug(f"Found {len(picked_up_items)} items during memory pickit, skipping pixel pickit")
            return found_items

        Logger.debug(f"Failed on {len(skipped_items)} items during memory pickit, falling back pixel pickit...")

        start = prev_cast_start = time.time()
        found_nothing = 0
        keyboard.send(self._config.char["show_items"])
        time.sleep(0.7) # sleep needed here to give d2r time to display items on screen on keypress
        #Creating a screenshot of the current loot
        self.take_loot_screenshot()
        time_out = False
        skipped_items = []
        curr_item_to_pick: PixelItem = None
        same_item_timer = None
        did_force_move = False
        while not time_out:
            if (time.time() - start) > 22:
                time_out = True
                Logger.warning("Got stuck during pickit, skipping it this time...")
                break
            img = self._screen.grab()
            item_list = self._item_finder.search(img)

            # Check if we need to pick up certain pots more pots
            need_pots = self._belt_manager.get_pot_needs()
            if need_pots["mana"] <= 0:
                item_list = [x for x in item_list if "mana_potion" not in x.name]
            if need_pots["health"] <= 0:
                item_list = [x for x in item_list if "healing_potion" not in x.name]
            if need_pots["rejuv"] <= 0:
                item_list = [x for x in item_list if "rejuvenation_potion" not in x.name]

            # TODO: Hacky solution for trav only gold pickup, hope we can soon read gold ammount and filter by that...
            if self._config.char["gold_trav_only"] and not is_at_trav:
                item_list = [x for x in item_list if "misc_gold" not in x.name]

            if len(item_list) == 0:
                # if twice no item was found, break
                found_nothing += 1
                if found_nothing > 1:
                    break
                else:
                    # Maybe we need to move cursor to another position to avoid highlighting items
                    pos_m = self._screen.convert_abs_to_monitor((0, 0))
                    mouse.move(*pos_m, randomize=[90, 160])
                    time.sleep(0.2)
            else:
                found_nothing = 0

                item_list.sort(key=itemgetter('dist'))
                closest_item = next((obj for obj in item_list if "misc_gold" not in obj["name"]), None)
                if not closest_item:
                    closest_item = item_list[0]

                #this needs to be tested
                #closest_item = item_list[0]
                #for item in item_list[1:]:
                    # if we're looting Trav as a non-teleporter, we need to spend less time stuck on
                    # stuff like gold because we're gonna be looting multiple times from a few different positions
                #    if closest_item.dist > item.dist and not \
                #        (is_at_trav and not char.can_teleport() and item.name in skip_items):
                #        closest_item = item


                # check if we trying to pickup the same item for a longer period of time
                force_move = False
                if curr_item_to_pick is not None:
                    is_same_item = (curr_item_to_pick.name == closest_item.name and \
                        abs(curr_item_to_pick.dist - closest_item.dist) < 20)
                    if same_item_timer is None or not is_same_item:
                        same_item_timer = time.time()
                        did_force_move = False
                    elif time.time() - same_item_timer > 1 and not did_force_move:
                        force_move = True
                        did_force_move = True
                    elif time.time() - same_item_timer > 3:
                        # backlist this item type for this pickit round
                        Logger.warning(f"Could not pick up: {closest_item.name}. Continue with other items")
                        skipped_items.append(closest_item.name)
                curr_item_to_pick = closest_item

                # To avoid endless teleport or telekinesis loop
                force_pick_up = char.can_tp and \
                                self._last_closest_item is not None and \
                                self._last_closest_item.name == closest_item.name and \
                                abs(self._last_closest_item.dist - closest_item.dist) < 20

                x_m, y_m = self._screen.convert_screen_to_monitor(closest_item.center)
                if not force_move and (closest_item.dist < self._config.ui_pos["item_dist"] or force_pick_up):
                    self._last_closest_item = None
                    # if potion is picked up, record it in the belt manager
                    if "potion" in closest_item.name:
                        self._belt_manager.picked_up_pot(closest_item.name)
                    # no need to stash potions, scrolls, or gold
                    if "potion" not in closest_item.name and "tp_scroll" != closest_item.name and "misc_gold" not in closest_item.name:
                        found_items = True

                    prev_cast_start = char.pick_up_item((x_m, y_m), item_name=closest_item.name, prev_cast_start=prev_cast_start)
                    if not char.can_tp:
                        time.sleep(0.2)

                    if self._ui_manager.is_overburdened():
                        found_items = True
                        Logger.warning("Inventory full, skipping pickit!")
                        self._ui_manager.throw_out_junk()
                        # throw out junk and check again
                    if self._ui_manager.is_overburdened():
                        found_items = True
                        Logger.warning("Inventory full, skipping pickit!")
                        break
                    else:
                        # send log to discord
                        if found_items and closest_item.name not in picked_up_items:
                            Logger.info(f"Picking up: {closest_item.name} ({closest_item.score*100:.1f}% confidence)")
                        picked_up_items.append(closest_item.name)
                else:
                    char.pre_move()
                    char.move((x_m, y_m), force_move=True)
                    if not char.can_tp:
                        time.sleep(0.3)
                    time.sleep(0.2)
                    # save closeset item for next time to check potential endless loops of not reaching it or of telekinsis/teleport
                    self._last_closest_item = closest_item
    
        keyboard.send(self._config.char["show_items"])
        elapsed = round(time.time() - start, 1)
        Logger.debug(f"Done picking {len(picked_up_items)} up items in {elapsed} seconds")
        return found_items
