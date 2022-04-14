import numpy as np
from typing import List
import keyboard
import itertools
import cv2
from d2r.d2r_api import D2rApi

from utils.misc import cut_roi, wait, color_filter
from utils.custom_mouse import mouse

from logger import Logger
from config import Config
from screen import Screen
from template_finder import TemplateFinder
from ui import UiManager


class BeltManager:
    def __init__(self, screen: Screen, template_finder: TemplateFinder, api: D2rApi):
        self._config = Config()
        self._screen = screen
        self._template_finder = template_finder
        self._api = api
        self._pot_needs = {"rejuv": 0, "health": 0, "mana": 0}
        self._item_pot_map = {
            "misc_rejuvenation_potion": "rejuv",
            "misc_full_rejuvenation_potion": "rejuv",
            "misc_super_healing_potion": "health",
            "misc_greater_healing_potion": "health",
            "misc_super_mana_potion": "mana",
            "misc_greater_mana_potion": "mana",
        }

    def get_pot_needs(self):
        return self._pot_needs

    def should_buy_pots(self):
        return self._pot_needs["health"] > 2 or self._pot_needs["mana"] > 3

    def _potion_type(self, img: np.ndarray) -> str:
        """
        Based on cut out image from belt, determines what type of potion it is.
        :param img: Cut out image of a belt slot
        :return: Any of ["empty", "rejuv", "health", "mana"]
        """
        h, w, _ = img.shape
        roi = [int(w * 0.4), int(h * 0.3), int(w * 0.4), int(h * 0.7)]
        img = cut_roi(img, roi)
        avg_brightness = np.average(img)
        if avg_brightness < 47:
            return "empty"
        score_list = []
        # rejuv
        mask, _ = color_filter(img, self._config.colors["rejuv_potion"])
        score_list.append((float(np.sum(mask)) / mask.size) * (1/255.0))
        # health
        mask, _ = color_filter(img, self._config.colors["health_potion"])
        score_list.append((float(np.sum(mask)) / mask.size) * (1/255.0))
        # mana
        mask, _ = color_filter(img, self._config.colors["mana_potion"])
        score_list.append((float(np.sum(mask)) / mask.size) * (1/255.0))
        # find max score
        max_val = np.max(score_list)
        if max_val > 0.28:
            idx = np.argmax(score_list)
            types = ["rejuv", "health", "mana"]
            return types[idx]
        else:
            return "empty"

    def _cut_potion_img(self, img: np.ndarray, column: int, row: int) -> np.ndarray:
        roi = [
            self._config.ui_pos["potion1_x"] - (self._config.ui_pos["potion_width"] // 2) + column * self._config.ui_pos["potion_next"],
            self._config.ui_pos["potion1_y"] - (self._config.ui_pos["potion_height"] // 2) - int(row * self._config.ui_pos["potion_next"] * 0.92),
            self._config.ui_pos["potion_width"],
            self._config.ui_pos["potion_height"]
        ]
        return cut_roi(img, roi)

    def drink_potion(self, potion_type: str, merc: bool = False, stats: List = []) -> bool:
        key = self._get_potion_key(potion_type)
        if not key:
            Logger.warning(f"No availale potion key for potion type {potion_type}")
            return False
        if merc:
            Logger.debug(f"Give {potion_type} potion in slot {key} to merc. HP: {(stats[0]*100):.1f}%")
            keyboard.send(f"left shift + {self._config.char[key]}")
        else:
            Logger.debug(f"Drink {potion_type} potion in slot {key}. HP: {(stats[0]*100):.1f}%, Mana: {(stats[1]*100):.1f}%")
            keyboard.send(self._config.char[key])
        self.update_pot_needs()
        return True
    
    def _get_potion_key(self, potion_type) -> str:
        data = self._api.get_data()
        if data is not None:
            if "flattened_belt" in data and data["flattened_belt"] is not None:
                belt = data["flattened_belt"]
                if belt is not None and len(belt) > 0:
                    for i in range(min(len(belt), 4)):
                        if len(belt) > i and type(belt[i]) is dict and "name" in belt[i] and potion_type[:4].lower() in belt[i]["name"].lower():
                            return f"potion{i+1}"
        return False

    def picked_up_pot(self, item_name: str):
        """Adjust the _pot_needs when a specific pot was picked up by the pickit
        :param item_name: Name of the item as it is in the pickit
        """
        self.update_pot_needs()
        if item_name not in self._pot_needs:
            if item_name in self._item_pot_map:
                item_name = self._item_pot_map[item_name]
        if item_name in self._pot_needs:
            self._pot_needs[item_name] = max(0, self._pot_needs[item_name] - 1)
        else:
            Logger.warning(f"BeltManager does not know about item: {item_name}")

    def update_pot_needs(self):
        """
        Check how many pots are needed
        """
        self._pot_needs = {"rejuv": 0, "health": 0, "mana": 0}
        wait(0.05, 0.07)
        data = self._api.get_data()
        rows = self._config.char["belt_rows"]
        if data is not None and "belt_rejuv_pots" in data and "belt_health_pots" in data and "belt_mana_pots" in data:
            self._pot_needs["rejuv"] = self._config.char["belt_rejuv_columns"] * rows - data["belt_rejuv_pots"]
            self._pot_needs["health"] = self._config.char["belt_hp_columns"] * rows - data["belt_health_pots"]
            self._pot_needs["mana"] = self._config.char["belt_mp_columns"] * rows - data["belt_mana_pots"]
        
        for potion_type in ["health", "mana", "rejuv"]:
            while self._pot_needs[potion_type] < 0:
                key = self._get_potion_key(potion_type)
                if not key:
                    self._pot_needs[potion_type] = 0
                else:
                    wait(0.04, 0.06)
                    keyboard.send(self._config.char[key])
                    self._pot_needs[potion_type] -= 1
                    wait(0.04, 0.06)

    def fill_up_belt_from_inventory(self, num_loot_columns: int):
        """
        Fill up your belt with pots from the inventory e.g. after death. It will open and close invetory by itself!
        :param num_loot_columns: Number of columns used for loot from left
        """
        keyboard.send(self._config.char["inventory_screen"])
        wait(0.7, 1.0)
        img = self._screen.grab()
        pot_positions = []
        for column, row in itertools.product(range(num_loot_columns), range(4)):
            center_pos, slot_img = UiManager.get_slot_pos_and_img(self._config, img, column, row)
            found = self._template_finder.search(["GREATER_HEALING_POTION", "GREATER_MANA_POTION", "SUPER_HEALING_POTION", "SUPER_MANA_POTION", "FULL_REJUV_POTION", "REJUV_POTION"], slot_img, threshold=0.9).valid
            if found:
                pot_positions.append(center_pos)
        keyboard.press("shift")
        for pos in pot_positions:
            x, y = self._screen.convert_screen_to_monitor(pos)
            mouse.move(x, y, randomize=4, delay_factor=[1.0, 1.5])
            wait(0.2, 0.25)
            mouse.click(button="left")
            wait(0.3, 0.4)
        keyboard.release("shift")
        wait(0.2, 0.25)
        keyboard.send(self._config.char["inventory_screen"])
        wait(0.5)
        self.update_pot_needs()
