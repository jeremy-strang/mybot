from typing import List
import keyboard
import time
import cv2
import itertools
import os
import numpy as np
from api.mapassist import MapAssistApi
from pickit.item_finder import PixelItem
from pickit.pickit_item import PickitItem
from pickit.types import Action, Stat
import obs
from obs import obs_recorder
from char.skill import Skill

from utils.custom_mouse import mouse
from utils.misc import wait, cut_roi, color_filter

from logger import Logger
from config import Config, ItemProps
from screen import Screen
from pickit import ItemFinder
from template_finder import TemplateFinder

from messages import Messenger
from game_stats import GameStats
from obs import ObsRecorder
from api import MapAssistApi

import random 
import string

from pickit.pickit_utils import get_pickit_action

class UiManager():
    """Everything that is clicking on some static 2D UI or is checking anything in regard to it should be placed here."""

    def __init__(self, screen: Screen, template_finder: TemplateFinder, obs_recorder: ObsRecorder, api: MapAssistApi, game_stats: GameStats = None):
        self._config = Config()
        self._template_finder = template_finder
        self._messenger = Messenger()
        self._obs_recorder = obs_recorder
        self._api = api
        self._game_stats = game_stats
        self._screen = screen
        self._gold_full = False
        self._gambling_round = 1
        self._curr_stash = {
            "items": 3 if self._config.char["fill_shared_stash_first"] else 0,
            "gold": 0
        } #0: personal, 1: shared1, 2: shared2, 3: shared3

    def use_wp(self, act: int, idx: int):
        """
        Use Waypoint. The menu must be opened when calling the function.
        :param act: Index of the desired act starting at 1 [A1 = 1, A2 = 2, A3 = 3, ...]
        :param idx: Index of the waypoint from top. Note that it start at 0!
        """
        str_to_idx_map = {"WP_A1_ACTIVE": 1, "WP_A2_ACTIVE": 2, "WP_A3_ACTIVE": 3, "WP_A4_ACTIVE": 4, "WP_A5_ACTIVE": 5}
        template_match = self._template_finder.search([*str_to_idx_map], self._screen.grab(), threshold=0.7, best_match=True, roi=self._config.ui_roi["wp_act_roi"])
        curr_active_act = str_to_idx_map[template_match.name] if template_match.valid else -1
        if curr_active_act != act:
            pos_act_btn = (self._config.ui_pos["wp_act_i_btn_x"] + self._config.ui_pos["wp_act_btn_width"] * (act - 1), self._config.ui_pos["wp_act_i_btn_y"])
            x, y = self._screen.convert_screen_to_monitor(pos_act_btn)
            mouse.move(x, y, randomize=8)
            mouse.click(button="left")
            wait(0.3, 0.4)
        pos_wp_btn = (self._config.ui_pos["wp_first_btn_x"], self._config.ui_pos["wp_first_btn_y"] + self._config.ui_pos["wp_btn_height"] * idx)
        x, y = self._screen.convert_screen_to_monitor(pos_wp_btn)
        mouse.move(x, y, randomize=[60, 9], delay_factor=[0.9, 1.4])
        wait(0.4, 0.5)
        mouse.click(button="left")
        # wait till loading screen is over
        if self.wait_for_loading_screen(5):
            while 1:
                if not self.wait_for_loading_screen(0.2):
                    return True
        return False

    def is_right_skill_active(self) -> bool:
        """
        :return: Bool if skill is red/available or not. Skill must be selected on right skill slot when calling the function.
        """
        # for template in skill_list:
        #     if self._template_finder.search(template, self._screen.grab(), threshold=0.84, roi=self._config.ui_roi["skill_right"]).valid:
        #         return True
        # return False
        # roi = [
        #     self._config.ui_pos["skill_right_x"] - (self._config.ui_pos["skill_width"] // 2),
        #     self._config.ui_pos["skill_y"] - (self._config.ui_pos["skill_height"] // 2),
        #     self._config.ui_pos["skill_width"],
        #     self._config.ui_pos["skill_height"]
        # ]
        # img = cut_roi(self._screen.grab(), roi)
        # avg = np.average(img)
        # return avg > 75.0
        data = self._api.data
        if data != None:
            if data["used_skill"] != data["right_skill"]:
                return True
        return False

    def is_right_skill_selected(self, skill: Skill) -> bool:
        """
        :return: Bool if skill is currently the selected skill on the right skill slot.
        """
        # for template in skill_list:
        #     if self._template_finder.search(template, self._screen.grab(), threshold=0.84, roi=self._config.ui_roi["skill_right"]).valid:
        #         return True
        # return False
        data = self._api.data
        if data != None:
            if data["right_skill"] == skill:
                return True
        return False

    def is_left_skill_selected(self, skill: Skill) -> bool:
        """
        :return: Bool if skill is currently the selected skill on the left skill slot.
        """
        # for template in template_list:
        #     if self._template_finder.search(template, self._screen.grab(), threshold=0.84, roi=self._config.ui_roi["skill_left"]).valid:
        #         return True
        # return False
        data = self._api.data
        if data != None:
            if data["left_skill"] == skill:
                return True
        return False

    def is_overburdened(self) -> bool:
        """
        :return: Bool if the last pick up overburdened your char. Must be called right after picking up an item.
        """
        img = cut_roi(self._screen.grab(), self._config.ui_roi["is_overburdened"])
        _, filtered_img = color_filter(img, self._config.colors["gold"])
        templates = [cv2.imread("assets/templates/inventory_full_msg_0.png"), cv2.imread("assets/templates/inventory_full_msg_1.png")]
        for template in templates:
            _, filtered_template = color_filter(template, self._config.colors["gold"])
            res = cv2.matchTemplate(filtered_img, filtered_template, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, _ = cv2.minMaxLoc(res)
            if max_val > 0.8:
                return True
        return False

    def wait_for_loading_screen(self, time_out: float = None) -> bool:
        """
        Waits until loading screen apears
        :param time_out: Maximum time to search for a loading screen
        :return: True if loading screen was found within the timeout. False otherwise
        """
        start = time.time()
        while True:
            img = self._screen.grab()
            is_loading_black_roi = np.average(img[:, 0:self._config.ui_roi["loading_left_black"][2]]) < 1.5
            if is_loading_black_roi:
                return True
            if time_out is not None and time.time() - start > time_out:
                return False
    
    def wait_for_loading_finish(self, time_out: float = 45.0) -> bool:
        """
        Waits until loading screen is finished
        :param time_out: Maximum time to wait for loading screen to finish
        :return: True if time out
        """
        is_loading = True
        start = time.time()
        while is_loading and time.time() - start < time_out:
            is_loading = self._template_finder.search("LOADING", self._screen.grab()).valid
            if is_loading: wait(0.3, 0.4)
            else: return False
        return True

    def save_and_exit(self, does_chicken: bool = False) -> bool:
        """
        Performes save and exit action from within game
        :return: Bool if action was successful
        """
        start = time.time()
        while (time.time() - start) < 15:
            Logger.debug(f"Saving and exiting (chicken: {does_chicken})")
            esc_menu_open = False
            templates = ["SAVE_AND_EXIT_NO_HIGHLIGHT", "SAVE_AND_EXIT_HIGHLIGHT"]

            try_api_start = time.time()
            data = None
            while data is None and time.time() - try_api_start < 1.0:
                if self._api is not None:
                    data = self._api.get_data()
                wait(0.5)

            if data is not None:
                if data["esc_menu_open"]:
                    esc_menu_open = True
                    Logger.debug("    Escape menu detected already open from memory")
                elif data["inventory_open"] or \
                        data["character_open"] or \
                        data["skill_select_open"] or \
                        data["skill_tree_open"] or \
                        data["npc_interact_open"] or \
                        data["npc_shop_open"] or \
                        data["quest_log_open"] or \
                        data["waypoint_open"] or \
                        data["party_open"] or \
                        data["mercenary_inventory_open"]:
                    Logger.debug("    Some other menu detected already open from memory, closing it...")
                    keyboard.send("esc")
                    wait(0.25)

            if not esc_menu_open:
                Logger.debug("    Opening escape menu...")
                keyboard.send("esc")
                wait(0.3)
                if self._api is not None:
                    data = self._api.get_data()
                    if data is not None and data["esc_menu_open"]:
                        esc_menu_open = True
            if esc_menu_open:
                Logger.debug(f"    Escape menu detected from memory, skipping template search")
            else:
                if not self._template_finder.search(templates, self._screen.grab(), roi=self._config.ui_roi["save_and_exit"], threshold=0.85).valid:
                    keyboard.send("esc")
                    wait(0.3)
            exit_btn_pos = (self._config.ui_pos["save_and_exit_x"], self._config.ui_pos["save_and_exit_y"])
            x_m, y_m = self._screen.convert_screen_to_monitor(exit_btn_pos)
            away_x_m, away_y_m = self._screen.convert_abs_to_monitor((-167, 0))
            while self._template_finder.search_and_wait(templates, roi=self._config.ui_roi["save_and_exit"], time_out=1.5, take_ss=False).valid:
                delay = [0.9, 1.1]
                if does_chicken:
                    delay = [0.3, 0.4]
                mouse.move(x_m, y_m, randomize=[38, 7], delay_factor=delay)
                wait(0.03, 0.06)
                mouse.press(button="left")
                wait(0.06, 0.1)
                mouse.release(button="left")
                if does_chicken:
                    # lets just try again just in case
                    wait(0.05, 0.08)
                    # mouse.click(button="left")
                wait(1.5, 2.0)
                mouse.move(away_x_m, away_y_m, randomize=40, delay_factor=[0.6, 0.9])
                wait(0.1, 0.5)
                
                if does_chicken:
                    self._obs_recorder.save_replay_if_enabled()
            return True
        return False

    def goto_lobby(self) -> bool:
        """
        Go from charselection to lobby
        :return: Bool if action was successful
        """
        while 1:
            Logger.debug("Wait for Lobby button")
            img = self._screen.grab()
            found_btn_lobby = self._template_finder.search(["LOBBY"], img, threshold=0.8, best_match=True, normalize_monitor=True)
            if found_btn_lobby.valid:
                Logger.debug(f"Found Lobby Btn")
                mouse.move(*found_btn_lobby.center, randomize=[35, 7], delay_factor=[1.0, 1.8])
                wait(0.1, 0.15)
                mouse.click(button="left")
                break
        return True
    
    def create_game_lobby(self) -> bool:
        Logger.debug("Creating game via Lobby")
        while 1:
            img = self._screen.grab()
            found_btn_create = self._template_finder.search(["CREATE_GAME"], img, threshold=0.8, best_match=True, normalize_monitor=True)    
            if found_btn_create.valid:   
                Logger.debug(f"Found Lobby Btn")
                mouse.move(*found_btn_create.center, randomize=[35, 7], delay_factor=[1.0, 1.8])
                wait(0.1, 0.15)
                mouse.click(button="left")
                wait(1, 1.15)
                break
        while 1:
            img = self._screen.grab()
            found_btn_game_name = self._template_finder.search(["GAME_NAME"], img, threshold=0.8, best_match=True, normalize_monitor=True)
            if found_btn_game_name.valid:
                mouse.move(found_btn_game_name.center[0], found_btn_game_name.center[1]+20, randomize=[3, 4], delay_factor=[1.0, 1.8])
                wait(0.4, 7)
                mouse.click(button="left")   
                wait(0.1, 0.15)
                break
        gn = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(15))
        pw = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(10))
        for char in gn:
            keyboard.send(char)
            wait (0.05, 0.1)
        keyboard.send("Tab")
        for char in pw:
            keyboard.send(char)
            wait (0.05, 0.1)
        while 1:
            img = self._screen.grab()
            found_btn_create = self._template_finder.search(["CREATE_GAME2"], img, threshold=0.95, best_match=True, normalize_monitor=True)
            if found_btn_create.valid:
                Logger.debug(f"Found Play Btn2")
                mouse.move(*found_btn_create.center, randomize=[35, 7], delay_factor=[1.0, 1.8])
                wait(0.1, 0.15)
                mouse.click(button="left")
                break
        return True
                 
    def start_game(self) -> bool:
        """
        Starting a game. Will wait and retry on server connection issue.
        :return: Bool if action was successful
        """
        Logger.debug("Wait for Play button")
        start = time.time()
        while 1:
            img = self._screen.grab()
            found_btn_off = self._template_finder.search(["PLAY_BTN", "PLAY_BTN_GRAY"], img, roi=self._config.ui_roi["offline_btn"], threshold=0.8, best_match=True, normalize_monitor=True)
            found_btn_on = self._template_finder.search(["PLAY_BTN", "PLAY_BTN_GRAY"], img, roi=self._config.ui_roi["online_btn"], threshold=0.8, best_match=True, normalize_monitor=True)
            found_btn = found_btn_off if found_btn_off.valid else found_btn_on
            if found_btn.name == "PLAY_BTN":
                Logger.debug(f"Found Play Btn")
                mouse.move(*found_btn.center, randomize=[35, 7], delay_factor=[0.2, 0.3])
                wait(0.1, 0.15)
                mouse.click(button="left")
                break
            wait_time = 1.5 if time.time() - start > 20 else 0.2
            wait(wait_time, wait_time + 0.2)

        difficulty=self._config.general["difficulty"].upper()
        difficulty_key="r" if difficulty == "normal" else "n" if difficulty == "nightmare" else "h"
        while 1:
            template_match = self._template_finder.search_and_wait(["LOADING", f"{difficulty}_BTN"], time_out=8, roi=self._config.ui_roi["difficulty_select"], threshold=0.9, normalize_monitor=True)
            if not template_match.valid:
                Logger.debug(f"Could not find {difficulty}_BTN, try from start again")
                return self.start_game()
            if template_match.name == "LOADING":
                Logger.debug(f"Found {template_match.name} screen")
                return True
            keyboard.send(difficulty_key)
            # mouse.move(*template_match.center, randomize=[50, 9], delay_factor=[1.0, 1.8])
            # wait(0.15, 0.2)
            # mouse.click(button="left")
            break

        # check for server issue
        wait(2.0)
        server_issue = self._template_finder.search("SERVER_ISSUES", self._screen.grab()).valid
        if server_issue:
            Logger.warning("Server connection issue. waiting 20s")
            x, y = self._screen.convert_screen_to_monitor((self._config.ui_pos["issue_occured_ok_x"], self._config.ui_pos["issue_occured_ok_y"]))
            mouse.move(x, y, randomize=10, delay_factor=[2.0, 4.0])
            mouse.click(button="left")
            wait(1, 2)
            keyboard.send("esc")
            wait(18, 22)
            return self.start_game()
        else:
            return True

    @staticmethod
    def _slot_has_item(slot_img: np.ndarray) -> bool:
        """
        Check if a specific slot in the inventory has an item or not based on color
        :param slot_img: Image of the slot
        :return: Bool if there is an item or not
        """
        slot_img = cv2.cvtColor(slot_img, cv2.COLOR_BGR2HSV)
        avg_brightness = np.average(slot_img[:, :, 2])
        return avg_brightness > 16.0

    @staticmethod
    def get_slot_pos_and_img(config: Config, img: np.ndarray, column: int, row: int) -> tuple[tuple[int, int],  np.ndarray]:
        """
        Get the pos and img of a specific slot position in Inventory. Inventory must be open in the image.
        :param config: The config which should be used
        :param img: Image from screen.grab() not cut
        :param column: Column in the Inventory
        :param row: Row in the Inventory
        :return: Returns position and image of the cut area as such: [[x, y], img]
        """
        top_left_slot = (config.ui_pos["inventory_top_left_slot_x"], config.ui_pos["inventory_top_left_slot_y"])
        slot_width = config.ui_pos["slot_width"]
        slot_height= config.ui_pos["slot_height"]
        slot = (top_left_slot[0] + slot_width * column, top_left_slot[1] + slot_height * row)
        # decrease size to make sure not to have any borders of the slot in the image
        offset_w = int(slot_width * 0.12)
        offset_h = int(slot_height * 0.12)
        min_x = slot[0] + offset_w
        max_x = slot[0] + slot_width - offset_w
        min_y = slot[1] + offset_h
        max_y = slot[1] + slot_height - offset_h
        slot_img = img[min_y:max_y, min_x:max_x]
        center_pos = (int(slot[0] + (slot_width // 2)), int(slot[1] + (slot_height // 2)))
        return center_pos, slot_img
    
    @staticmethod
    def get_slot_pos(config: Config, column: int, row: int) -> tuple[int, int]:
        """
        Get the pos and img of a specific slot position in Inventory
        :param config: The config which should be used
        :param column: Column in the Inventory
        :param row: Row in the Inventory
        :return: Returns position and image of the cut area as such: [[x, y], img]
        """
        top_left_slot = (config.ui_pos["inventory_top_left_slot_x"], config.ui_pos["inventory_top_left_slot_y"])
        slot_width = config.ui_pos["slot_width"]
        slot_height= config.ui_pos["slot_height"]
        slot = (top_left_slot[0] + slot_width * column, top_left_slot[1] + slot_height * row)
        # decrease size to make sure not to have any borders of the slot in the image
        offset_w = int(slot_width * 0.12)
        offset_h = int(slot_height * 0.12)
        min_x = slot[0] + offset_w
        max_x = slot[0] + slot_width - offset_w
        min_y = slot[1] + offset_h
        max_y = slot[1] + slot_height - offset_h
        center_pos = (int(slot[0] + (slot_width // 2)), int(slot[1] + (slot_height // 2)))
        return center_pos

    def _inventory_has_items(self, img, num_loot_columns: int, num_ignore_columns=0) -> bool:
        """
        Check if Inventory has any items
        :param img: Img from screen.grab() with inventory open
        :param num_loot_columns: Number of columns to check from left
        :return: Bool if inventory still has items or not
        """
        for column, row in itertools.product(range(num_ignore_columns, num_loot_columns), range(4)):
            _, slot_img = self.get_slot_pos_and_img(self._config, img, column, row)
            if self._slot_has_item(slot_img):
                return True
        return False

    def _move_mouse_to_inventory_item(self, item):
        if item:
            item_pos = (item["position"][0], item["position"][1])
            slot_pos = self.get_slot_pos(self._config, *item_pos)
            x_m, y_m = self._screen.convert_screen_to_monitor(slot_pos)
            mouse.move(x_m, y_m, randomize=10, delay_factor=[0.5, 0.7])

    def _move_mouse_to_stash_pos(position: tuple[float, float]):
        STASH_ROI = ( 683, 150, 339, 343)
        STASH_SPACING_X = STASH_ROI[2] / 9
        STASH_SPACING_Y = STASH_ROI[3] / 9
        x = int(STASH_ROI[0] + STASH_SPACING_X * position[0])
        y = int(STASH_ROI[1] + STASH_SPACING_Y * position[1])
        mouse.move(x, y, randomize=2, delay_factor=[0.3, 0.4])
    
    def _move_mouse_to_inv_pos(position: tuple[float, float]):
        INV_ROI = (1515, 407, 340, 111)
        INV_SPACING_X = INV_ROI[2] / 9
        INV_SPACING_Y = INV_ROI[3] / 3
        x = int(INV_ROI[0] + INV_SPACING_X * position[0])
        y = int(INV_ROI[1] + INV_SPACING_Y * position[1])
        mouse.move(x, y, randomize=2, delay_factor=[0.3, 0.4])

    def _identify_inventory_item(self, item) -> dict:
        if item and not item["is_identified"]:
            tome, quantity = self.get_tome_of("Identify")
            if tome and quantity > 0:
                self._move_mouse_to_inventory_item(tome)
                wait(0.1, 0.2)
                mouse.click(button="right")
                wait(0.5)
                self._move_mouse_to_inventory_item(item)
                wait(0.1, 0.2)
                mouse.click(button="left")
                wait(0.5)
                item = self._api.find_item(item["id"], "inventory_items")
                if item and item["is_identified"]:
                    self._move_mouse_to_inventory_item(item)
                    Logger.debug(f"Successfully identified item {item['name']} at position {item['position']}!")
                else:
                    Logger.debug(f"Failed to identify item {item['name']} at position {item['position']}")
        return item

    def _keep_item(self, inv_pos: tuple[int, int] = None, center = None) -> list[PickitItem]:
        """
        Check if an item should be kept, the item should be hovered and in own inventory when function is called
        :param inv_pos: tuple[int, int] Position of the item in the inventory
        :return: list[PickitItem] list of items for some reason
        """
        if inv_pos != None and self._api.data:
            mem_items = []
            for item in self._api.find_items_by_position(inv_pos, "inventory_items"):
                if item:
                    action = get_pickit_action(item, self._config.pickit_config)
                    if action >= Action.Keep and not "Potion" in item["name"]:
                        pickit_item = PickitItem(item, action)
                        keep = True
                        if not item["is_identified"] and (item["type"], item["quality"]) in self._config.pickit_config.IdentifiedItems:
                            item = self._identify_inventory_item(item)
                            # Recalc action after identifying
                            action = get_pickit_action(item, self._config.pickit_config)
                            pickit_item = PickitItem(item, action)
                            keep = action >= Action.Keep
                            if not keep:
                                if self._config.general["info_screenshots"]:
                                    cv2.imwrite("./info_screenshots/discared_item_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())
                                self._game_stats.log_item_discard(pickit_item.get_summary(), False)
                        if keep:
                            Logger.info(f"Keeping item '{item['name']}' from memory  (ID: {item['id']}, hovered: {item['is_hovered']}, identified: {item['is_identified']}, position: {item['position']})")
                            mem_items.append(pickit_item)
            if len(mem_items) > 0:
                return [mem_items[0]]
        return []

    def _move_to_stash_tab(self, stash_idx: int):
        """Move to a specifc tab in the stash
        :param stash_idx: idx of the stash starting at 0 (personal stash)
        """
        str_to_idx_map = {"STASH_0_ACTIVE": 0, "STASH_1_ACTIVE": 1, "STASH_2_ACTIVE": 2, "STASH_3_ACTIVE": 3}
        template_match = self._template_finder.search([*str_to_idx_map], self._screen.grab(), threshold=0.7, best_match=True, roi=self._config.ui_roi["stash_btn_roi"])
        curr_active_stash = str_to_idx_map[template_match.name] if template_match.valid else -1
        if curr_active_stash != stash_idx:
            # select the start stash
            personal_stash_pos = (self._config.ui_pos["stash_personal_btn_x"], self._config.ui_pos["stash_personal_btn_y"])
            stash_btn_width = self._config.ui_pos["stash_btn_width"]
            next_stash_pos = (personal_stash_pos[0] + stash_btn_width * stash_idx, personal_stash_pos[1])
            x_m, y_m = self._screen.convert_screen_to_monitor(next_stash_pos)
            mouse.move(x_m, y_m, randomize=[30, 7], delay_factor=[1.0, 1.5])
            wait(0.2, 0.3)
            mouse.click(button="left")
            wait(0.3, 0.4)

    def stash_all_items(self, num_loot_columns: int, item_finder: ItemFinder, gamble = False):
        """
        Stashing all items in inventory. Stash UI must be open when calling the function.
        :param num_loot_columns: Number of columns used for loot from left
        """
        if self._api.data and self._api.data["stash_open"]:
            Logger.debug("    Detected stash menu using memory")
        else:
            Logger.debug("    Could not detect stash menu from memory, searching for inventory gold btn...")
            # Move cursor to center
            x, y = self._screen.convert_abs_to_monitor((0, 0))
            mouse.move(x, y, randomize=[40, 200], delay_factor=[1.0, 1.5])
            # Wait till gold btn is found
            gold_btn = self._template_finder.search_and_wait("INVENTORY_GOLD_BTN", roi=self._config.ui_roi["gold_btn"], time_out=20, normalize_monitor=True)
            if not gold_btn.valid:
                Logger.error("        Could not determine to be in stash menu. Continue...")
                return
            Logger.debug("       Found inventory gold btn")
        if not gamble:
            # stash gold
            if self._config.char["stash_gold"]:
                inventory_no_gold = self._template_finder.search("INVENTORY_NO_GOLD", self._screen.grab(), roi=self._config.ui_roi["inventory_gold"], threshold=0.83)
                if inventory_no_gold.valid:
                    Logger.debug("Skipping gold stashing")
                else:
                    Logger.debug("Stashing gold")
                    self._move_to_stash_tab(min(3, self._curr_stash["gold"]))
                    mouse.move(*gold_btn.center, randomize=4)
                    wait(0.1, 0.15)
                    mouse.press(button="left")
                    wait(0.25, 0.35)
                    mouse.release(button="left")
                    wait(0.4, 0.6)
                    keyboard.send("enter") #if stash already full of gold just nothing happens -> gold stays on char -> no popup window
                    wait(1.0, 1.2)
                    # move cursor away from button to interfere with screen grab
                    mouse.move(-120, 0, absolute=False, randomize=15)
                    inventory_no_gold = self._template_finder.search("INVENTORY_NO_GOLD", self._screen.grab(), roi=self._config.ui_roi["inventory_gold"], threshold=0.83)
                    if not inventory_no_gold.valid:
                        Logger.info("Stash tab is full of gold, selecting next stash tab.")
                        self._curr_stash["gold"] += 1
                        if self._config.general["info_screenshots"]:
                            cv2.imwrite("./info_screenshots/info_gold_stash_full_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())
                        if self._curr_stash["gold"] > 3:
                            #decide if gold pickup should be disabled or gambling is active
                            if self._config.char["gamble_items"]:
                                self._gold_full = True
                            else:
                                # turn off gold pickup
                                self._config.turn_off_goldpickup()
                                # inform user about it
                                msg = "All stash tabs and character are full of gold, turn of gold pickup"
                                Logger.info(msg)
                                if self._config.general["custom_message_hook"]:
                                    self._messenger.send_message(msg=f"{self._config.general['name']}: {msg}")
                        else:
                            # move to next stash
                            wait(0.5, 0.6)
                            return self.stash_all_items(num_loot_columns, item_finder)
        else:
            self.transfer_shared_to_private_gold(self._gambling_round)
        # stash stuff
        x, y = self._screen.convert_abs_to_monitor((0, 0))
        mouse.move(x, y, randomize=[40, 200], delay_factor=[1.0, 1.5])
        self._move_to_stash_tab(self._curr_stash["items"])
        center_m = self._screen.convert_abs_to_monitor((0, 0))
        items = self._api.find_looted_items(num_loot_columns)
        if items != None:
            Logger.debug(f"    Found {len(items)} inventory items in {num_loot_columns} loot columns to check")
            for item in items:
                item_pos = (item["position"][0], item["position"][1])
                column, row = item_pos
                slot_pos = self.get_slot_pos(self._config, *item_pos)
                x_m, y_m = self._screen.convert_screen_to_monitor(slot_pos)
                found_items = self._keep_item(inv_pos=(column, row), center=center_m)
                mouse.move(x_m, y_m, randomize=10, delay_factor=[1.0, 1.3])
                wait(0.4, 0.5)
                hovered_item = self._screen.grab()
                if len(found_items) > 0 and self._api.data and self._api.data["stash_open"]:
                    Logger.debug(f"    Keeping item found at position {column}, {row}...")
                    keyboard.send("ctrl", do_release=False)
                    wait(0.05, 0.08)
                    mouse.click(button="left")
                    wait(0.05, 0.08)
                    keyboard.release("ctrl")
                    wait(0.5)
                    # To avoid logging multiple times the same item when stash tab is full
                    # check the _keep_item again. In case stash is full we will still find the same item
                    if len(self._keep_item(item_pos, center_m)) > 0:
                        Logger.debug("    Wanted to stash a item, but its still in inventory. Assumes full stash. Move to next.")
                        break
                    else:
                        send_msg = found_items[0].action == 2
                        self._game_stats.log_item_keep(found_items[0].name, send_msg, hovered_item)
                # else:
                #     # make sure there is actually an item
                #     time.sleep(0.3)
                #     curr_pos = mouse.get_position()
                #     # move mouse away from inventory, for some reason it was sometimes included in the grabed img
                #     x, y = self._screen.convert_abs_to_monitor((0, 0))
                #     mouse.move(x, y, randomize=[40, 200], delay_factor=[1.0, 1.5])
                #     item_check_img = self._screen.grab()
                #     mouse.move(*curr_pos, randomize=2)
                #     wait(0.4, 0.6)
                #     slot_pos, slot_img = self.get_slot_pos_and_img(self._config, item_check_img, column, row)
                #     if self._slot_has_item(slot_img):
                #         if self._config.general["info_screenshots"]:
                #             cv2.imwrite("./info_screenshots/info_discard_item_" + time.strftime("%Y%m%d_%H%M%S") + ".png", hovered_item)
                #         mouse.press(button="left")
                #         wait(0.2, 0.4)
                #         mouse.release(button="left")
                #         mouse.move(*center_m, randomize=20)
                #         wait(0.2, 0.3)
                #         mouse.press(button="left")
                #         wait(0.2, 0.3)
                #         mouse.release(button="left")
                #         wait(0.5, 0.5)

        Logger.debug("Check if stash is full")
        time.sleep(0.6)
        # move mouse away from inventory, for some reason it was sometimes included in the grabed img
        x, y = self._screen.convert_abs_to_monitor((0, 0))
        mouse.move(x, y, randomize=[40, 200], delay_factor=[1.0, 1.5])
        img = self._screen.grab()
        if self._inventory_has_items(img, num_loot_columns):
            Logger.info("Stash page is full, selecting next stash")
            if self._config.general["info_screenshots"]:
                cv2.imwrite("./info_screenshots/debug_info_inventory_not_empty_" + time.strftime("%Y%m%d_%H%M%S") + ".png", img)

            # if filling shared stash first, we decrement from 3, otherwise increment
            self._curr_stash["items"] += -1 if self._config.char["fill_shared_stash_first"] else 1
            if (self._config.char["fill_shared_stash_first"] and self._curr_stash["items"] < 0) or self._curr_stash["items"] > 3:
                Logger.error("All stash is full, quitting")
                if self._config.general["custom_message_hook"]:
                    self._messenger.send_stash()
                os._exit(1)
            else:
                # move to next stash
                wait(0.5, 0.6)
                return self.stash_all_items(num_loot_columns, item_finder)

        Logger.debug("Done stashing")
        wait(0.1)
        if self._api.data and self._api.data["stash_open"]:
            keyboard.send("esc")
        wait(0.4, 0.5)

    def throw_out_junk(self, keep_open: bool = False):
        if self._api.data != None:
            wait(0.05, 0.08)
            num_loot_columns = self._config.char["num_loot_columns"]
            items = self._api.find_looted_items(num_loot_columns)
            if items != None:
                Logger.debug(f"    Found {len(items)} inventory items in {num_loot_columns} loot columns to check")
                inv_open = self._api.data["inventory_open"]
                vendor_open = self._api.data["npc_shop_open"]
                if not inv_open:
                    keyboard.send(self._config.char["inventory_screen"])
                    wait(0.5, 0.6)
                    inv_open = self._api.data != None and self._api.data["inventory_open"]
                    vendor_open = self._api.data != None and self._api.data["npc_shop_open"]
                if inv_open:
                    msg = "Selling" if vendor_open else "Throwing out"
                    Logger.info(f"{msg} junk...")
                    center_m = self._screen.convert_abs_to_monitor((0, 0))
                    for item in items:
                        item_pos = (item["position"][0], item["position"][1])
                        column, row = item_pos
                        slot_pos = self.get_slot_pos(self._config, *item_pos)
                        x_m, y_m = self._screen.convert_screen_to_monitor(slot_pos)
                        found_items = self._keep_item(inv_pos=(column, row), center=center_m)
                        mouse.move(x_m, y_m, randomize=10, delay_factor=[1.0, 1.3])
                        wait(0.4, 0.5)
                        inv_open = self._api.data != None and self._api.data["inventory_open"]
                        vendor_open = self._api.data != None and self._api.data["npc_shop_open"]
                        if len(found_items) == 0 and inv_open:
                            Logger.debug(f"   {msg} item '{item['name']}' found at position {column}, {row}...")
                            keyboard.send("ctrl", do_release=False)
                            wait(0.05, 0.08)
                            mouse.click(button="left")
                            wait(0.05, 0.08)
                            keyboard.release("ctrl")
                            wait(0.5)
                    
                    inv_open = self._api.data != None and self._api.data["inventory_open"]
                    vendor_open = self._api.data != None and self._api.data["npc_shop_open"]
                    if not keep_open and (inv_open or vendor_open):
                        keyboard.send("esc")
                        wait(0.3, 0.4)
        # Logger.info("Throwing out junk")
        # wait(0.2, 0.3)
        # keyboard.send(self._config.char["inventory_screen"])
        # wait(0.5, 0.6)
        # num_loot_columns = self._config.char["num_loot_columns"]
        # for column, row in itertools.product(range(num_loot_columns), range(4)):
        #     img = self._screen.grab()
        #     slot_pos, slot_img = self.get_slot_pos_and_img(self._config, img, column, row)
        #     if self._slot_has_item(slot_img):
        #         x_m, y_m = self._screen.convert_screen_to_monitor(slot_pos)
        #         mouse.move(x_m, y_m, randomize=10, delay_factor=[1.0, 1.3])
        #         # Sheck item again and discard it or stash it
        #         wait(0.4, 0.6)
        #         hovered_item = self._screen.grab()
        #         found_items = self._keep_item(item_finder, hovered_item, inv_pos=(column, row), center=(x_m, y_m))
        #         if len(found_items) == 0:
        #             keyboard.release(self._config.char["show_items"])
        #             wait(0.1, 0.2)
        #             keyboard.release(self._config.char["stand_still"])
        #             wait(0.1, 0.2)
        #             keyboard.send("ctrl", do_release=False)
        #             wait(0.1, 0.2)
        #             mouse.click(button="left")
        #             wait(0.1, 0.2)
        #             keyboard.release("ctrl")
        #             wait(0.3)
        # keyboard.send(self._config.char["inventory_screen"])
        # wait(0.3, 0.4)

    def transfer_shared_to_private_gold(self, count: int):
        for x in range (3):
            self._move_to_stash_tab (count)
            stash_gold_btn = self._template_finder.search("INVENTORY_GOLD_BTN", self._screen.grab(), roi=self._config.ui_roi["gold_btn_stash"], threshold=0.83)
            if stash_gold_btn.valid:
                x,y = self._screen.convert_screen_to_monitor(stash_gold_btn.center)
                mouse.move(x, y, randomize=4)
                wait (0.4, 0.5)
                mouse.press(button="left")
                wait (0.1, 0.15)
                mouse.release(button="left")
                wait (0.1, 0.15)
                keyboard.send ("Enter")
                wait (0.1, 0.15)
                self._move_to_stash_tab (0)
                inventory_gold_btn = self._template_finder.search("INVENTORY_GOLD_BTN", self._screen.grab(), roi=self._config.ui_roi["gold_btn"], threshold=0.83)
                if inventory_gold_btn.valid:
                    x,y = self._screen.convert_screen_to_monitor(inventory_gold_btn.center)
                    mouse.move(x, y, randomize=4)
                    wait (0.4, 0.5)
                    mouse.press(button="left")
                    wait (0.1, 0.15)
                    mouse.release(button="left")
                    wait (0.1, 0.15)
                    keyboard.send ("Enter")
                    wait (0.1, 0.15)
        self._gambling_round += 1

    def should_stash(self) -> bool:
        looted_items = self._api.find_looted_items(self._config.char["num_loot_columns"])
        if looted_items != None and len(looted_items) > 0:
            looted_items = list(filter(lambda item: item != None and "Potion" not in item["name"], looted_items))
            return len(looted_items) > 0
        return False
        # wait(0.2, 0.3)
        # keyboard.send(self._config.char["inventory_screen"])
        # wait(0.7, 1.0)
        # should_stash = self._inventory_has_items(self._screen.grab(), num_loot_columns)
        # keyboard.send(self._config.char["inventory_screen"])
        # wait(0.4, 0.6)
        # return should_stash

    def close_vendor_screen(self):
        keyboard.send("esc")
        # just in case also bring cursor to center and click
        # x, y = self._screen.convert_screen_to_monitor((self._config.ui_pos["center_x"], self._config.ui_pos["center_y"]))
        # mouse.move(x, y, randomize=25, delay_factor=[1.0, 1.5])
        # mouse.click(button="left")

    def repair_and_fill_up_tp(self) -> bool:
        """
        Repair and fills up TP buy selling tome and buying. Vendor inventory needs to be open!
        :return: Bool if success
        """
        repair_btn = self._template_finder.search_and_wait("REPAIR_BTN", roi=self._config.ui_roi["repair_btn"], time_out=4, normalize_monitor=True)
        if not repair_btn.valid:
            return False
        self.throw_out_junk(keep_open=True)
        mouse.move(*repair_btn.center, randomize=12, delay_factor=[1.0, 1.5])
        wait(0.1, 0.15)
        mouse.click(button="left")
        wait(0.1, 0.15)
        x, y = self._screen.convert_screen_to_monitor((self._config.ui_pos["vendor_misc_x"], self._config.ui_pos["vendor_misc_y"]))
        mouse.move(x, y, randomize=[20, 6], delay_factor=[1.0, 1.5])
        wait(0.1, 0.15)
        mouse.click(button="left")
        # another click to dismiss popup message in case you have not enough gold to repair, preventing tome not being bought back
        wait(0.1, 0.15)
        mouse.click(button="left")
        wait(0.5, 0.6)
        tp_tome = self._template_finder.search_and_wait(["TP_TOME", "TP_TOME_RED"], roi=self._config.ui_roi["right_inventory"], time_out=3, normalize_monitor=True)
        if not tp_tome.valid:
            return False
        keyboard.send("ctrl", do_release=False)
        mouse.move(*tp_tome.center, randomize=8, delay_factor=[1.0, 1.5])
        wait(0.1, 0.15)
        mouse.press(button="left")
        wait(0.25, 0.35)
        mouse.release(button="left")
        wait(0.5, 0.6)
        keyboard.send("ctrl", do_press=False)
        tp_tome = self._template_finder.search_and_wait("TP_TOME", roi=self._config.ui_roi["left_inventory"], time_out=3, normalize_monitor=True)
        if not tp_tome.valid:
            return False
        keyboard.send("ctrl", do_release=False)
        mouse.move(*tp_tome.center, randomize=8, delay_factor=[1.0, 1.5])
        wait(0.1, 0.15)
        mouse.click(button="right")
        wait(0.1, 0.15)
        keyboard.send("ctrl", do_press=False)
        # delay to make sure the tome has time to transfer to other inventory before closing window
        tp_tome = self._template_finder.search_and_wait("TP_TOME", roi=self._config.ui_roi["right_inventory"], time_out=3)
        if not tp_tome.valid:
            return False
        return True

    def get_tome_of(self, name: str):
        tomes = self._api.find_items_by_name(f"Tome of {name}")
        if tomes is not None and len(tomes) > 0:
            for tome in tomes:
                if tome and "stats" in tome:
                    for pair in tome["stats"]:
                        if pair["key"] == Stat.Quantity:
                            return (tome, pair["value"])
        return (None, 0)

    def fill_tome_of(self, name: str) -> bool:
        # Ghetto mixed pixel/memory implementation because I am lazy
        tome, quantity = self.get_tome_of(name)
        if tome is not None and quantity < 15:
            scrolls = self._api.find_items_by_name(f"Scroll of {name}", "vendor_items")
            if scrolls and len(scrolls) > 0:
                scroll_search = self._template_finder.search_and_wait(f"SCROLL_OF_{name.upper().replace(' ', '_')}", roi=self._config.ui_roi["left_inventory"], time_out=3, normalize_monitor=True)
                if scroll_search.valid:
                    mouse.move(*scroll_search.center, randomize=3, delay_factor=[0.7, 1])
                    keyboard.send(hotkey="shift", do_release=False)
                    wait(0.04, 0.06)
                    mouse.click(button="right")
                    wait(0.04, 0.06)
                    keyboard.release(hotkey="shift")
                    wait(0.9, 1.1)
                return True
        return False

    def has_tps(self) -> bool:
        tome, quantity = self.get_tome_of("Town Portal")
        if tome and quantity > 0:
            Logger.debug(f"Detected TP scroll quantity from items in memory, quantity: {quantity}, position: {tome['position']}")
            return True
        elif self._config.char["tp"]:
            keyboard.send(self._config.char["tp"])
            template_match = self._template_finder.search_and_wait(
                ["TP_ACTIVE", "TP_INACTIVE"],
                roi=self._config.ui_roi["skill_right"],
                best_match=True,
                threshold=0.79,
                time_out=4)
            if not template_match.valid:
                Logger.warning("You are out of TP scrolls")
                if self._config.general["info_screenshots"]:
                    cv2.imwrite("./info_screenshots/debug_out_of_tps_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())
            return template_match.valid
        else:
            return False

    def repair_needed(self) -> bool:
        template_match = self._template_finder.search(
            "REPAIR_NEEDED",
            self._screen.grab(),
            roi=self._config.ui_roi["repair_needed"],
            use_grayscale=True)
        return template_match.valid

    def gambling_needed(self) -> bool:
        return self._gold_full

    def set__gold_full(self, bool: bool):
        self._gold_full = bool
        self._gambling_round = 1

    def gamble(self, item_finder: ItemFinder):
        gold = True
        gamble_on = True
        if self._config.char["num_loot_columns"]%2==0:
            ignore_columns = self._config.char["num_loot_columns"]-1
        else:
            ignore_columns = self._config.char["num_loot_columns"]-2
        template_match = self._template_finder.search_and_wait("REFRESH", threshold=0.79, time_out=4)
        if template_match.valid:
            #Gambling window is open. Starting to spent some coins
            while (gamble_on and gold):
                if (self._inventory_has_items (self._screen.grab(),self._config.char["num_loot_columns"], ignore_columns) and self._inventory_has_items (self._screen.grab(),2)):
                    gamble_on = False
                    self.close_vendor_screen ()
                    break
                for item in self._config.char["gamble_items"]:
                    template_match_item = self._template_finder.search (item.upper(), self._screen.grab(), roi=self._config.ui_roi["left_inventory"], normalize_monitor=True)
                    while not template_match_item.valid:
                        #Refresh gambling screen
                        template_match = self._template_finder.search ("REFRESH", self._screen.grab(), normalize_monitor=True)
                        if (template_match.valid):
                            mouse.move(*template_match.center, randomize=12, delay_factor=[1.0, 1.5])
                            wait(0.1, 0.15)
                            mouse.click(button="left")
                            wait(0.1, 0.15)
                        template_match_item = self._template_finder.search (item.upper(), self._screen.grab(), roi=self._config.ui_roi["left_inventory"], normalize_monitor=True)
                    #item found in gambling menu
                    mouse.move(*template_match_item.center, randomize=12, delay_factor=[1.0, 1.5])
                    wait(0.1, 0.15)
                    mouse.click(button="right")
                    wait(0.1, 0.15)
                    template_match = self._template_finder.search ("no_gold".upper(), self._screen.grab(), threshold= 0.90)
                    #check if gold is av
                    if template_match.valid:
                        gold = False
                        self.close_vendor_screen()
                        break
                    for column, row in itertools.product(range(self._config.char["num_loot_columns"]), range(4)):
                        img = self._screen.grab()
                        slot_pos, slot_img = self.get_slot_pos_and_img(self._config, img, column, row)
                        if self._slot_has_item(slot_img):
                            x_m, y_m = self._screen.convert_screen_to_monitor(slot_pos)
                            mouse.move(x_m, y_m, randomize=10, delay_factor=[1.0, 1.3])
                            # check item again and discard it or stash it
                            wait(1.2, 1.4)
                            hovered_item = self._screen.grab()
                            if not self._keep_item(item_finder, hovered_item):
                                keyboard.send('ctrl', do_release=False)
                                wait(0.1, 0.15)
                                mouse.click (button="left")
                                wait(0.1, 0.15)
                                keyboard.send('ctrl', do_press=False)
            #Stashing needed
        else:
            Logger.warning("gambling failed")

    def enable_no_pickup(self) -> bool:
        """
        Checks the best match between enabled and disabled an retrys if already set.
        :return: Returns True if we succesfully set the nopickup option
        """
        wait(0.03, 0.05)
        keyboard.send('enter')
        wait(0.08, 0.14)
        keyboard.write('/nopickup', delay=0.07)
        wait(0.02, 0.04)
        keyboard.send('enter')
        wait(0.17, 0.22)
        no_pickup = self._template_finder.search_and_wait(["ITEM_PICKUP_ENABLED", "ITEM_PICKUP_DISABLED"], roi=self._config.ui_roi["no_pickup"], best_match=True, time_out=3)
        if not no_pickup.valid:
            return False
        if no_pickup.name == "ITEM_PICKUP_DISABLED":
            return True
        keyboard.send('enter')
        wait(0.17, 0.22)
        keyboard.send('up')
        wait(0.08, 0.14)
        keyboard.send('enter')
        wait(0.08, 0.14)
        return True
    
    def disable_no_pickup(self) -> bool:
        """
        Checks the best match between enabled and disabled an retrys if already set.
        :return: Returns True if we succesfully set the nopickup option
        """
        wait(0.03, 0.05)
        keyboard.send('enter')
        wait(0.08, 0.14)
        keyboard.write('/nopickup', delay=0.07)
        wait(0.03, 0.05)
        keyboard.send('enter')
        wait(0.17, 0.22)
        no_pickup = self._template_finder.search_and_wait(["ITEM_PICKUP_ENABLED", "ITEM_PICKUP_DISABLED"], roi=self._config.ui_roi["no_pickup"], best_match=True, time_out=3)
        if not no_pickup.valid:
            return False
        if no_pickup.name == "ITEM_PICKUP_ENABLED":
            return True
        keyboard.send('enter')
        wait(0.17, 0.22)
        keyboard.send('up')
        wait(0.08, 0.14)
        keyboard.send('enter')
        wait(0.08, 0.14)
        return True

    def buy_pots(self, healing_pots: int = 0, mana_pots: int = 0):
        """
        Buy pots from vendors. Vendor inventory needs to be open!
        :param healing_pots: Number of healing pots to buy
        :param mana_pots: Number of mana pots to buy
        """
        self.throw_out_junk(keep_open=True)
        h_pot = self._template_finder.search_and_wait("SUPER_HEALING_POTION", roi=self._config.ui_roi["left_inventory"], time_out=3, normalize_monitor=True)
        if h_pot.valid is False:  # If not available in shop, try to shop next best potion.
            h_pot = self._template_finder.search_and_wait("GREATER_HEALING_POTION", roi=self._config.ui_roi["left_inventory"], time_out=3, normalize_monitor=True)
        if h_pot.valid:
            mouse.move(*h_pot.center, randomize=3, delay_factor=[1.0, 1.5])
            for _ in range(healing_pots):
                mouse.click(button="right")
                wait(0.9, 1.1)

        m_pot = self._template_finder.search_and_wait("SUPER_MANA_POTION", roi=self._config.ui_roi["left_inventory"], time_out=3, normalize_monitor=True)
        if m_pot.valid is False:  # If not available in shop, try to shop next best potion.
            m_pot = self._template_finder.search_and_wait("GREATER_MANA_POTION", roi=self._config.ui_roi["left_inventory"], time_out=3, normalize_monitor=True)
        if m_pot.valid:
            mouse.move(*m_pot.center, randomize=3, delay_factor=[1.0, 1.5])
            for _ in range(mana_pots):
                mouse.click(button="right")
                wait(0.9, 1.1)
        
        self.fill_tome_of("Identify")
        self.fill_tome_of("Town Portal")
        