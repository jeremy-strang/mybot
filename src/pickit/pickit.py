import re
import time
import keyboard
import cv2
from operator import itemgetter

from pytest import skip
from d2r_mem.d2r_mem_api import D2rMemApi
from game_stats import GameStats
from pickit.types import ItemMode
from pathing import Pather

from utils.custom_mouse import mouse
from config import Config
from logger import Logger
from screen import Screen
from pickit import PixelItem
from ui import UiManager, belt_manager
from ui import BeltManager
from char import IChar
from pickit.pickit_utils import get_pickit_action
from utils.misc import wait

class Pickit:
    def __init__(self,
                 screen: Screen,
                 ui_manager: UiManager,
                 belt_manager: BeltManager,
                 char: IChar,
                 pather: Pather,
                 api: D2rMemApi,
                 game_stats: GameStats,
                 ):
        self._screen = screen
        self._ui_manager = ui_manager
        self._belt_manager = belt_manager
        self._char = char
        self._pather = pather
        self._config = Config()
        self._last_closest_item: PixelItem = None
        self._api = api
        self._game_stats = game_stats
    
    def _next_item(self, potion_needs: dict = None, skip_ids: set = None) -> dict:
        data = self._api.data
        items_found = []
        if data is not None:
            for item in data["items"]:
                item_priority = get_pickit_action(item, self._config.pickit_config, potion_needs=potion_needs, game_stats=self._game_stats)
                if item["mode"] == ItemMode.OnGround and item_priority > 0:
                    items_found.append(item)
            items_found = sorted(items_found, key = lambda item: item["dist"])
            items_found = sorted(items_found, key = lambda item: get_pickit_action(item, self._config.pickit_config, game_stats=self._game_stats), reverse=True)
            if skip_ids is not None and len(skip_ids) > 0:
                items_found = list(filter(lambda x: x["id"] not in skip_ids, items_found))
            if len(items_found) > 0:
                Logger.debug("Memory pickit order:")
                for item in items_found:
                    Logger.debug(f"    {item['name']}, dist: {round(item['dist'], 1)}, quality: {item['quality']}, base: {item['type']}, position: {item['position']}")
        return items_found[0] if len(items_found) > 0 else None

    def pick_up_items(self, time_out: float = 22.0, skip_nopickup: bool = False) -> bool:
        # Wait a bit for items to load
        wait(0.3, 0.4)
        start = time.time()
        elapsed = 0
        attempts = 0
        disabled_nopickup = False
        did_time_out = False
        picked_up_items = []
        skipped_items = []
        skipped_ids = set()
        self._belt_manager.update_pot_needs()
        potion_needs = self._belt_manager.get_pot_needs()
        item = self._next_item(potion_needs)
        last_id = 0
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

            is_potion = "Potion" in item["name"]
            if item["id"] == last_id:
                attempts += 1
                Logger.debug(f"Attempted to pick up the same item {attempts} times so far")
                # If we're on the same item for the third time, make sure nopickup is disabled
                if attempts == 3:
                    time_before_disable = time.time()
                    self._ui_manager.disable_no_pickup()
                    wait(0.1, 0.2)
                    start += time.time() - time_before_disable
                
                # If we hit five attempts, skip the item
                if attempts >= 5:
                    skipped_ids.add(item["id"])
                    if not is_potion:
                        skipped_items.append(item)
                    attempts = 0
                    item = self._next_item(potion_needs, skipped_ids)
                    continue

            last_id = item["id"]
            Logger.info(f"    Picking up {item['name']} (ID: {item['id']}), quality: {item['quality']}...")
            click_time_out = 6
            if is_potion:
                click_time_out = 2
            elif get_pickit_action(item, self._config.pickit_config, game_stats=self._game_stats) > 1:
                click_time_out = 15
            if self._pather.click_item(item, self._char, time_out=click_time_out):
                if is_potion:
                    if "Rejuv"in item["name"]:
                        self._belt_manager.picked_up_pot("rejuv")
                    if "Heal"in item["name"]:
                        self._belt_manager.picked_up_pot("health")
                    if "Mana"in item["name"]:
                        self._belt_manager.picked_up_pot("mana")
                else:
                    picked_up_items.append(item)
            item = self._next_item(potion_needs, skipped_ids)

        if disabled_nopickup:
            Logger.info(f"    Re-enabling /nopickup...")
            self._ui_manager.enable_no_pickup()
            Logger.info(f"    Done picking up {len(picked_up_items)} items\n{'*'*80}")

        return (picked_up_items, skipped_items)
