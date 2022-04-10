from types import FunctionType
from typing import Dict, Tuple, Union, List, Callable
import random
import time
import cv2
import math
import keyboard
import numpy as np
from monsters.monster_rule import MonsterRule
import obs
from pathing import PathFinder, Pather, OldPather
from monsters import MonsterType
from char.skill import Skill
from utils.custom_mouse import mouse
from utils.misc import rotate_vec, unit_vector, wait, cut_roi, is_in_roi, color_filter

from logger import Logger
from config import Config
from screen import Screen
from template_finder import TemplateFinder
from ui import UiManager
from ocr import Ocr

from api.mapassist import MapAssistApi
from obs import ObsRecorder
from monsters import CHAMPS_UNIQUES, get_unlooted_monsters

class IChar:
    def __init__(self,
                 skill_hotkeys: dict,
                 screen: Screen,
                 template_finder: TemplateFinder,
                 ui_manager: UiManager,
                 api: MapAssistApi,
                 obs_recorder: ObsRecorder,
                 old_pather: OldPather,
                 pather: Pather
                ):
        self._skill_hotkeys = skill_hotkeys
        self._char_config = Config().char
        self._template_finder = template_finder
        self._ui_manager = ui_manager
        self._screen = screen
        self._api = api
        self._obs_recorder = obs_recorder
        self._old_pather = old_pather
        self._pather = pather
        self._config = Config()
        self._last_tp = time.time()
        self._ocr = Ocr()
        # Add a bit to be on the save side
        self._cast_duration = self._char_config["casting_frames"] * 0.04 + 0.02
        self._stats_with_weapon_tab1 = None
        self._stats_with_weapon_tab2 = None
        self.can_tp = False
        self.can_tp_with_charges = False

    def discover_capabilities(self):
        can_tp = False
        can_tp_with_charges = False
        if self._skill_hotkeys["teleport"]:
            if self.select_tp():
                wait(0.1)
                if self.skill_is_charged():
                    can_tp_with_charges = True
                else:
                    can_tp = True
        self.can_tp = can_tp
        self.can_tp_with_charges = can_tp_with_charges
        self._cast_duration = self.get_cast_frames() * 0.04 + 0.02

    def get_fcr(self):
        data = self._api.get_data()
        fcr = 0
        if data is not None and "player_stats" in data and data["player_stats"] is not None:
            stats = data["player_stats"]
            for item in stats:
                if item["key"] == "FasterCastRate":
                    fcr = item["value"]
                    break
        Logger.debug(f"Detected player FCR: {fcr}")
        return fcr
    
    def get_frw(self):
        data = self._api.get_data()
        frw = 0
        if data is not None and "player_stats" in data and data["player_stats"] is not None:
            stats = data["player_stats"]
            for item in stats:
                if item["key"] == "FasterRunWalk":
                    frw = item["value"]
                    break
        Logger.debug(f"Detected player FCR: {frw}")
        return frw

    def get_cast_frames(self):
        Logger.debug("Cast frame auto-detect is not implemented for this class, using configured frames instead")
        return self._char_config["casting_frames"]

    def verify_active_weapon_tab(self) -> bool:
        active_weapon_tab = self.get_active_weapon_tab()
        if active_weapon_tab == -1:
            wait(0.3, 0.4)
            keyboard.send(self._config.char["inventory_screen"])
            wait(0.2, 0.25)
            active_weapon_tab = self.get_active_weapon_tab()
        attempts = 0
        while active_weapon_tab == 2 and attempts < 5:
            self.switch_weapon()
            wait(0.2, 0.25)
            attempts += 1
            active_weapon_tab = self.get_active_weapon_tab()
        return active_weapon_tab == 1

    def _build_stats_dict_for_weapon_tab_detection(self):
        data = self._api.get_data()
        if data is not None:
            stats_dict = {}
            for stat_pair in data["player_stats"]:
                key = stat_pair["key"]
                if key in ["Strength", "Dexterity", "Vitality", "Energy"]:
                    stats_dict[key] = stat_pair["value"]
            return stats_dict
        return None

    def _save_stats_for_weapon_tab_detection(self, tab: int):
        if tab == 1 and self._stats_with_weapon_tab1 is not None: return
        if tab == 2 and self._stats_with_weapon_tab2 is not None: return
        stats_dict = self._build_stats_dict_for_weapon_tab_detection()
        if tab == 1: self._stats_with_weapon_tab1 = stats_dict
        elif tab == 2: self._stats_with_weapon_tab2 = stats_dict

    def _try_stats_for_weapon_detection(self) -> int:
        tab1_was_stored = self._stats_with_weapon_tab1 is not None
        tab2_was_stored = self._stats_with_weapon_tab2 is not None
        data = self._api.get_data()
        if data is None or (not tab1_was_stored and not tab2_was_stored): return -1
        stats_dict = self._build_stats_dict_for_weapon_tab_detection()
        strength = stats_dict["Strength"]
        dexterity = stats_dict["Dexterity"]
        energy = stats_dict["Energy"]
        vitality = stats_dict["Vitality"]
        tab1_match = False

        if tab1_was_stored and \
            strength == self._stats_with_weapon_tab1["Strength"] and \
            dexterity == self._stats_with_weapon_tab1["Dexterity"] and \
            energy == self._stats_with_weapon_tab1["Energy"] and \
            vitality == self._stats_with_weapon_tab1["Vitality"]:
            Logger.info(f"Detected weapon tab 1 based on stats in memory")
            tab1_match = True
        tab2_match = False

        if tab2_was_stored and \
            strength == self._stats_with_weapon_tab2["Strength"] and \
            dexterity == self._stats_with_weapon_tab2["Dexterity"] and \
            energy == self._stats_with_weapon_tab2["Energy"] and \
            vitality == self._stats_with_weapon_tab2["Vitality"]:
            Logger.info(f"Detected weapon tab 2 based on stats in memory")
            tab2_match = True

        if tab1_match and tab2_match:
            Logger.info(f"Could not determine weapon tab, stats were equal for both")
        if tab1_match and not tab2_match: return 1
        if tab2_match and not tab1_match: return 2
        return -1

    def get_active_weapon_tab(self) -> int:
        active_slot = self._try_stats_for_weapon_detection()
        if active_slot != -1: return active_slot

        #Check to make sure we are on our main weapon set in slot 1, and not the secondary set in slot 2
        wait(0.4, 0.05)
        keyboard.send(self._config.char["inventory_screen"])
        wait(0.4, 0.05)
        data = self._api.data
        if data is not None and not data["inventory_open"]:
            keyboard.send(self._config.char["inventory_screen"])
            wait(0.25, 0.3)
        
        if self._template_finder.search_and_wait(["WS1"], threshold=0.84, time_out=2.5, roi=[862, 50, 110, 100]).valid:
            Logger.info("Weapon slot 1 is active")
            active_slot = 1
            self._save_stats_for_weapon_tab_detection(1)
        elif self._template_finder.search_and_wait(["WS2"], threshold=0.84, time_out=2.5, roi=[862, 50, 110, 100]).valid:
            Logger.info("Weapon slot 2 is active")
            active_slot = 2
            self._save_stats_for_weapon_tab_detection(2)
        else:
            Logger.warning("Could not determine the active weapon slot")
        data = self._api.data
        if data is not None and data["inventory_open"]:
            keyboard.send(self._config.char["inventory_screen"])
            wait(0.25, 0.3)
        return active_slot

    def switch_weapon(self):
        wait(0.03)
        keyboard.send(self._char_config["weapon_switch"])
        wait(0.25, 0.3)
        self._cast_duration = self.get_cast_frames() * 0.04 + 0.02

    def get_player_gold(self):
        data = self._api.get_data()
        if data is not None and "player_gold" in data:
            return data["player_gold"]
        return -1

    def select_skill(self, skill: str):
        if skill in self._skill_hotkeys and self._skill_hotkeys[skill]:
            keyboard.send(self._skill_hotkeys[skill])

    def pick_up_item(self, pos: Tuple[float, float], item_name: str = None, prev_cast_start: float = 0):
        mouse.move(pos[0], pos[1])
        time.sleep(0.1)
        mouse.click(button="left")
        wait(0.45, 0.5)
        return prev_cast_start

    def select_by_template(
        self,
        template_type:  Union[str, List[str]],
        success_func: Callable = None,
        time_out: float = 8,
        threshold: float = 0.68,
        telekinesis: bool = False
    ) -> bool:
        """
        Finds any template from the template finder and interacts with it
        :param template_type: Strings or list of strings of the templates that should be searched for
        :param success_func: Function that will return True if the interaction is successful e.g. return True when loading screen is reached, defaults to None
        :param time_out: Timeout for the whole template selection, defaults to None
        :param threshold: Threshold which determines if a template is found or not. None will use default form .ini files
        :return: True if success. False otherwise
        """
        if type(template_type) == list and "A5_STASH" in template_type:
            # sometimes waypoint is opened and stash not found because of that, check for that
            if self._template_finder.search("WAYPOINT_MENU", self._screen.grab()).valid:
                keyboard.send("esc")
        start = time.time()
        while time_out is None or time.time() - start < time_out:
            template_match = self._template_finder.search(template_type, self._screen.grab(), threshold=threshold, normalize_monitor=True)
            if template_match.valid:
                Logger.debug(f"Select {template_match.name} ({template_match.score*100:.1f}% confidence)")
                mouse.move(*template_match.center)
                wait(0.2, 0.3)
                mouse.click(button="left")
                # check the successfunction for 2 sec, if not found, try again
                check_success_start = time.time()
                while time.time() - check_success_start < 2:
                    if success_func is None or success_func():
                        return True
        Logger.error(f"Wanted to select {template_type}, but could not find it")
        return False

    def skill_is_charged(self, img: np.ndarray = None) -> bool:
        # if img is None:
        #     img = self._screen.grab()
        # skill_img = cut_roi(img, self._config.ui_roi["skill_right"])
        # charge_mask, _ = color_filter(skill_img, self._config.colors["blue"])
        # if np.sum(charge_mask) > 0:
        #     return True
        # return False
        data = self._api.data
        if data != None and "right_skill_data" in data:
            skill_data = data["right_skill_data"]
            if skill_data != None and "Charges" in skill_data["Charges"] and skill_data["Charges"] > 0:
                return True
        return False

    def is_low_on_teleport_charges(self):
        img = self._screen.grab()
        charges_remaining = self.get_skill_charges()
        if charges_remaining:
            Logger.debug(f"{charges_remaining} teleport charges remain")
            return charges_remaining <= 3
        else:
            charges_present = self.skill_is_charged(img)
            if charges_present:
                Logger.error("is_low_on_teleport_charges: unable to determine skill charges, assume zero")
            return True

    def _remap_skill_hotkey(self, skill_asset, hotkey, skill_roi, expanded_skill_roi):
        x, y, w, h = skill_roi
        x, y = self._screen.convert_screen_to_monitor((x, y))
        mouse.move(x + w/2, y + h / 2)
        mouse.click("left")
        wait(0.3)
        match = self._template_finder.search(skill_asset, self._screen.grab(), threshold=0.84, roi=expanded_skill_roi)
        if match.valid:
            x, y = self._screen.convert_screen_to_monitor(match.center)
            mouse.move(x, y)
            wait(0.3)
            keyboard.send(hotkey)
            wait(0.3)
            mouse.click("left")
            wait(0.3)

    def remap_right_skill_hotkey(self, skill_asset, hotkey):
        return self._remap_skill_hotkey(skill_asset, hotkey, self._config.ui_roi["skill_right"], self._config.ui_roi["skill_right_expanded"])

    def select_tp(self):
        if self._skill_hotkeys["teleport"] and not self._ui_manager.is_right_skill_selected(Skill.Teleport):
            keyboard.send(self._skill_hotkeys["teleport"])
            wait(0.1, 0.15)
        return self._ui_manager.is_right_skill_selected(Skill.Teleport)

    def get_skill_charges(self, img: np.ndarray = None):
        if img is None:
            img = self._screen.grab()
        x, y, w, h = self._config.ui_roi["skill_right"]
        x = x - 1
        y = y + round(h/2)
        h = round(h/2 + 5)
        img = cut_roi(img, [x, y, w, h])
        mask, _ = color_filter(img, self._config.colors["skill_charges"])
        ocr_result = self._ocr.image_to_text(
            images = mask,
            model = "engd2r_inv_th",
            psm = 7,
            word_list = "",
            scale = 1.4,
            crop_pad = False,
            erode = False,
            invert = True,
            threshold = 0,
            digits_only = True,
            fix_regexps = False,
            check_known_errors = False,
            check_wordlist = False,
            word_match_threshold = 0.9
        )[0]
        try:
            return int(ocr_result.text)
        except:
            return None

    def pre_move(self):
        # if teleport hotkey is set and if teleport is not already selected
        if self.can_tp:
            self.select_tp()

    def hold_move(self, pos_monitor: Tuple[float, float], force_tp: bool = False, force_move: bool = False):
        mouse.move(*pos_monitor, delay_factor = [.02,.04])

    def move(self, pos_monitor: Tuple[float, float], force_tp: bool = False, force_move: bool = True):
        factor = self._config.advanced_options["pathing_delay_factor"]
        if self._skill_hotkeys["teleport"] and (force_tp or(self._ui_manager.is_right_skill_selected(Skill.Teleport) and self._ui_manager.is_right_skill_active())):
            mouse.move(pos_monitor[0], pos_monitor[1], randomize=2, delay_factor=[factor*0.1, factor*0.14])
            wait(0.02, 0.03)
            mouse.click(button="right")
            wait(self._cast_duration, self._cast_duration + 0.02)
        else:
            # in case we want to walk we actually want to move a bit before the point cause d2r will always "overwalk"
            pos_screen = self._screen.convert_monitor_to_screen(pos_monitor)
            pos_abs = self._screen.convert_screen_to_abs(pos_screen)
            dist = math.dist(pos_abs, (0, 0))
            min_wd = max(10, self._config.ui_pos["min_walk_dist"])
            max_wd = random.randint(int(self._config.ui_pos["max_walk_dist"] * 0.65), self._config.ui_pos["max_walk_dist"])
            adjust_factor = max(max_wd, min(min_wd, dist - 50)) / max(min_wd, dist)
            pos_abs = [int(pos_abs[0] * adjust_factor), int(pos_abs[1] * adjust_factor)]
            x, y = self._screen.convert_abs_to_monitor(pos_abs)
            mouse.move(x, y, randomize=5, delay_factor=[factor*0.1, factor*0.14])
            wait(0.02, 0.03)
            if force_move:
                keyboard.send(self._config.char["force_move"])
            else:
                mouse.click(button="left")
                wait(0.02, 0.03)

    def reposition(self, target_pos):
        rot_deg = random.randint(-2, 2)
        tele_pos_abs = unit_vector(rotate_vec(target_pos, rot_deg)) * 320 * 3
        tele_pos_abs = self._old_pather._adjust_abs_range_to_screen([tele_pos_abs[0], tele_pos_abs[1]])
        pos_m = self._screen.convert_abs_to_monitor(tele_pos_abs)
        self.pre_move()
        try:
            self.move(pos_m)
            self.move(pos_m)
        except:
            pass
    
    def open_tp(self):
        # will check if tp is available and select the skill
        if not self._ui_manager.has_tps():
            Logger.debug("No TPs")
            return False
        wait(0.1, 0.15)
        mouse.click(button="right")
        wait(self._cast_duration)
        return True

    def tp_town(self):
        if not self.open_tp(): return False
        wait(1, 1.4) # takes quite a while for tp to be visible
        self._pather.click_object("TownPortal")
        if self._pather.wait_for_town(4): return True

        Logger.warning("Failed to TP to town using memory, falling back to pixels")

        roi_mouse_move = [
            int(self._config.ui_pos["screen_width"] * 0.3),
            0,
            int(self._config.ui_pos["screen_width"] * 0.4),
            int(self._config.ui_pos["screen_height"] * 0.7)
        ]
        pos_away = self._screen.convert_abs_to_monitor((-167, -30))
        wait(1, 1.4) # takes quite a while for tp to be visible
        roi = self._config.ui_roi["tp_search"]
        start = time.time()
        retry_count = 0
        while (time.time() - start) < 8:
            if time.time() - start > 3.7 and retry_count == 0:
                retry_count += 1
                Logger.debug("Move to another position and try to open tp again")
                pos_m = self._screen.convert_abs_to_monitor((random.randint(-70, 70), random.randint(-70, 70)))
                self.pre_move()
                self.move(pos_m)
                if self._ui_manager.has_tps():
                    mouse.click(button="right")
                wait(1, 1.4) # takes quite a while for tp to be visible
            img = self._screen.grab()
            template_match = self._template_finder.search(
                ["BLUE_PORTAL","BLUE_PORTAL_2"],
                img,
                threshold=0.66,
                roi=roi,
                normalize_monitor=True
            )
            if template_match.valid:
                pos = template_match.center
                pos = (pos[0], pos[1] + 30)
                # Note: Template is top of portal, thus move the y-position a bit to the bottom
                mouse.move(*pos, randomize=6, delay_factor=[0.9, 1.1])
                wait(0.08, 0.15)
                mouse.click(button="left")
                if self._ui_manager.wait_for_loading_screen(2.0):
                    return True
            # move mouse away to not overlay with the town portal if mouse is in center
            pos_screen = self._screen.convert_monitor_to_screen(mouse.get_position())
            if is_in_roi(roi_mouse_move, pos_screen):
                mouse.move(*pos_away, randomize=40, delay_factor=[0.8, 1.4])
        return False

    def pre_travel(self, do_pre_buff=True, force_switch_back=False):
        if do_pre_buff:
            self.pre_buff(switch_back=force_switch_back or not self._config.char["teleport_weapon_swap"])

    def post_travel(self, skip_weapon_swap=False):
        if self._config.char["teleport_weapon_swap"] and not skip_weapon_swap:
            self.switch_weapon()
            self.verify_active_weapon_tab()

    def prepare_attack(self):
        pass

    def post_attack(self):
        pass
    
    def cast_aoe(self, skill_hotkey: str, button="right"):
        if button == "left":
            keyboard.send(self._char_config["stand_still"], do_release=False)
        keyboard.send(self._skill_hotkeys[skill_hotkey])
        wait(0.02, 0.03)
        mouse.click(button=button)
        wait(self._cast_duration + 0.01)
        if button == "left":
            keyboard.release(self._char_config["stand_still"])
            wait(0.02, 0.03)

    def cast_melee(self, skill_key: str, time_in_s: float, abs_screen_pos: tuple[float, float], mouse_button: str = "left"):
        mouse_pos_m = self._screen.convert_abs_to_monitor(abs_screen_pos)
        Logger.debug(f"Casting {skill_key} in the direction of ({round(mouse_pos_m[0], 2)}, {round(mouse_pos_m[0], 2)})")
        if self._skill_hotkeys[skill_key]:
            keyboard.send(self._skill_hotkeys[skill_key])
            wait(0.05)
            mouse.move(*mouse_pos_m, delay_factor=[0.2, 0.4])
            keyboard.send(self._char_config["stand_still"], do_release=False)
            start = time.time()
            while (time.time() - start) < time_in_s:
                wait(0.06, 0.08)
                mouse.press(button=mouse_button)
                wait(0.1, 0.2)
                mouse.release(button=mouse_button)
            keyboard.send(self._char_config["stand_still"], do_press=False)
    
    def tele_stomp_monster(self, skill_key: str, time_in_s: float, monster: dict, mouse_button: str = "left", stop_when_dead=True, max_distance=4.0) -> bool:
        if self._skill_hotkeys[skill_key]:
            if type(monster) is dict:
                mid = monster['id']
                Logger.debug(f"Attacking monster '{monster['name']}' (ID: {mid}) with {skill_key}, distance: {round(monster['dist'], 2)}, mouse: ({round(monster['position'][0], 2)}, {round(monster['position'][0], 2)})")
                keyboard.send(self._char_config["stand_still"], do_release=False)
                wait(0.03, 0.04)
                keyboard.send(self._skill_hotkeys[skill_key])
                wait(0.03, 0.04)
                start = time.time()
                while (time.time() - start) < time_in_s:
                    monster = self._api.find_monster(mid)
                    if monster is None: break
                    self._pather.move_mouse_to_monster(monster)
                    wait(0.03, 0.04)
                    mouse.press(button=mouse_button)
                    wait(0.03, 0.04)
                    monster = self._api.find_monster(mid)
                    if monster is None or monster["dist"] > max_distance or (monster["mode"] == 12 and stop_when_dead): break
                mouse.release(button=mouse_button)
                wait(0.02, 0.03)
                keyboard.release(self._config.char["stand_still"])
                wait(0.02, 0.03)
                return True
            else:
                Logger.error(f"Invalid monster {monster}")
        return False

    def clear_zone(self, destination=None, pickit_func=None) -> int:
        looted_uniques = set()
        picked_up_items = 0
        pf = PathFinder(self._api)
        nodes = pf.solve_tsp(destination)
        for node in nodes:
            self._pather.traverse(node, self, 0, do_pre_move=True, obj=False, kill=False, time_out=8.0)
            wait(0.1)
            picked_up_items += self.kill_uniques(pickit_func, 16.0, looted_uniques)
        self.post_attack()
        Logger.info(f"Killed and looted {picked_up_items} items from {len(looted_uniques)} champion/unique packs")
        return picked_up_items

    def _pre_buff_cta(self, switch_back=True):
        self.switch_weapon()
        keyboard.send(self._char_config["battle_command"])
        wait(0.04, 0.07)
        mouse.click(button="right")
        wait(self._cast_duration, self._cast_duration + 0.03)
        keyboard.send(self._char_config["battle_orders"])
        wait(0.04, 0.07)
        mouse.click(button="right")
        wait(self._cast_duration, self._cast_duration + 0.03)
        # Make sure the switch back to the original weapon is good
        if switch_back:
            self.switch_weapon()
            self.verify_active_weapon_tab()
    
    def filter_monster(self, monsterlist, area):
        filtered_monster = []
        boss = False
        for monster in monsterlist:
            if monster["boss_id"] != 0 and monster["corpse"] == False:
                filtered_monster.append(monster)
                boss = True    
            if monster["dist"] < area and monster["corpse"] == False:
                filtered_monster.append(monster)
        return filtered_monster, boss
    
    def special_mobtype(self, filtered_monster, mobtype: list):    
        if type(filtered_monster) == list:
            if len(filtered_monster) > 0:
                if(filtered_monster[0]["type"] in mobtype):    
                    return True     
            else:
                return False
        else:
            return False
    
    def kill_around(self,  api, density=7, area=25, special = False):
        special_types = [
            MonsterType.SUPER_UNIQUE,
            MonsterType.UNIQUE,
            MonsterType.CHAMPION,
            MonsterType.POSSESSED,
            MonsterType.GHOSTLY,
            MonsterType.MINION,
        ]
        def _calc_distance(mon):
            if mon["boss_id"] != 0: return 0
            elif mon["type"] in "SuperUnique": return 0.05
            elif any (mobtype in mon["type"] for mobtype in special_types): return 0.1
            elif mon["type"] in "Minion": return 0.2
            return mon["dist"]

        data = self._api.get_data()
        monsterlist = data["monsters"]
        monsterlist.sort(key=_calc_distance)
        filtered_monster = []
        kill = False
        count = 0
        if type(density) == int:
            filtered_monster, boss = self.filter_monster(monsterlist, area)
            if special:
                kill = self.special_mobtype(filtered_monster, special_types)
                if len(filtered_monster)>density or kill or boss: 
                    return filtered_monster[0]
                else:
                    return False
        elif type(density) == list:
            counter = 0
            for dens in density:
                filtered_monster, boss = self.filter_monster(monsterlist, area[counter])
                if special:
                    kill = self.special_mobtype(filtered_monster, special_types)            
                if len(filtered_monster)>density[counter] or kill or boss: 
                    return filtered_monster[0]
                counter += 1
            return False

    def get_monster_distance(self, monster, offset):
        data = self._api.get_data()
        player_p = data['player_pos_world'] + data['player_offset']
        dist = math.dist(player_p, monster["position"]) - (offset [0] + offset [1]) 
        return dist

    def pre_buff(self, switch_back=True):
        pass

    def loot_uniques(self, pickit, time_out: float=16.0, looted_uniques: set=set(), boundary=None) -> int:
        picked_up_items = 0
        start = time.time()
        last_pickit_pos = None
        # Loot all the dead uniques/champs that may be off screen
        if pickit is not None:
            unlooted = get_unlooted_monsters(self._api, CHAMPS_UNIQUES, looted_uniques, boundary, max_distance=60)
            while len(unlooted) > 0 and time.time() - start < time_out:
                data = self._api.get_data()
                if data is not None:
                    corpse = unlooted[0]
                    area_pos = unlooted[0]["position"] - data["area_origin"]
                    if corpse["dist"] < 15 or not self._pather.traverse(area_pos, self, verify_location=False, time_out=6, dest_distance=10):
                        looted_uniques.add(corpse["id"])
                data = self._api.get_data()
                if last_pickit_pos is None or math.dist(last_pickit_pos, data["player_pos_area"]) >= 15:
                    picked_up_items += pickit()
                last_pickit_pos = data["player_pos_area"]
                for m in unlooted:
                    if m["dist"] < 15:
                        looted_uniques.add(m["id"])
                        print(f"Looted champ/unique monster with ID {m['id']}, type: {m['type']}")
                unlooted = get_unlooted_monsters(self._api, CHAMPS_UNIQUES, looted_uniques, boundary, max_distance=60)
        return picked_up_items

    def kill_uniques(self, pickit: FunctionType, time_out: float=9.0, looted_uniques: set=set()) -> bool:
        raise ValueError("Kill uniques not implemented")

    def kill_pindle(self) -> bool:
        raise ValueError("Pindle is not implemented!")

    def kill_shenk(self) -> bool:
        raise ValueError("Shenk is not implemented!")

    def kill_eldritch(self) -> bool:
        raise ValueError("Eldritch is not implemented!")

    def kill_council(self) -> bool:
        raise ValueError("Council is not implemented!")

    def kill_mephisto(self) -> bool:
        raise ValueError("Mephisto is not implemented!")

    def kill_andariel(self) -> bool:
        raise ValueError("Andariel is not implemented!")

    def kill_countess(self) -> bool:
        raise ValueError("Countess is not implemented!")

    def kill_nihlathak(self, end_nodes: list[int]) -> bool:
        raise ValueError("Nihlathak is not implemented!")

    def kill_summoner(self) -> bool:
        raise ValueError("Arcane is not implemented!")

    def kill_diablo(self) -> bool:
        raise ValueError("Diablo is not implemented!")

    def kill_deseis(self, nodes1: list[int], nodes2: list[int], nodes3: list[int]) -> bool:
        raise ValueError("Diablo De Seis is not implemented!")

    def kill_infector(self) -> bool:
        raise ValueError("Diablo Infector is not implemented!")

    def kill_vizier(self, nodes1: list[int], nodes2: list[int]) -> bool:
        raise ValueError("Diablo Vizier is not implemented!")

    def kill_cs_trash(self) -> bool:
        raise ValueError("Diablo CS Trash is not implemented!")
