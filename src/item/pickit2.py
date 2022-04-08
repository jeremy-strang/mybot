import re
import time
import keyboard
import cv2
from operator import itemgetter

from pytest import skip
from api.mapassist import MapAssistApi
from item.types import ItemMode
from pathing import Pather

from utils.custom_mouse import mouse
from config import Config
from logger import Logger
from screen import Screen
from item import Item
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
                if item["item_mode"] == ItemMode.OnGround and item_priority > 0:
                    items_found.append(item)
            items_found = sorted(items_found, key = lambda item: item["dist"])
            items_found = sorted(items_found, key = lambda item: get_pickit_priority(item), reverse=True)
            if skip_ids is not None and len(skip_ids) > 0:
                items_found = list(filter(lambda x: x["id"] not in skip, items_found))
            if len(items_found) > 0:
                Logger.debug("Memory pickit order:")
                for item in items_found:
                    Logger.debug(f"    {item['name']}, dist: {round(item['dist'], 1)}, quality: {item['quality']}, base: {item['type']}, position: {item['position']}")
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
            click_time_out = 6
            if is_potion:
                click_time_out = 2
            elif get_pickit_priority(item) > 1:
                click_time_out = 15
            if self._pather.click_item(item, self._char):
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

        return (picked_up_items, list(skipped_ids))
