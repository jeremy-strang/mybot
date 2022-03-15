from types import FunctionType
from typing import Dict, Tuple, Union, List, Callable
import random
import time
import cv2
import math
import keyboard
import numpy as np
from char.capabilities import CharacterCapabilities
import obs
from pathing import PathFinder, Pather, OldPather
from state_monitor import MonsterType
from utils.custom_mouse import mouse
from utils.misc import wait, cut_roi, is_in_roi, color_filter

from logger import Logger
from config import Config
from screen import Screen
from template_finder import TemplateFinder
from ui import UiManager
from ocr import Ocr

from api.mapassist import MapAssistApi
from obs import ObsRecorder
from utils.monsters import CHAMPS_UNIQUES, find_monster, get_unlooted_monsters

class IChar:
    _CrossGameCapabilities: Union[None, CharacterCapabilities] = None

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
        self._cast_duration = self._char_config["casting_frames"] * 0.04 + 0.015
        self.capabilities = None

    def _discover_capabilities(self) -> CharacterCapabilities:
        if self._skill_hotkeys["teleport"]:
            if self.select_tp():
                if self.skill_is_charged():
                    return CharacterCapabilities(can_teleport_natively=False, can_teleport_with_charges=True)
                else:
                    return CharacterCapabilities(can_teleport_natively=True, can_teleport_with_charges=False)
            return CharacterCapabilities(can_teleport_natively=False, can_teleport_with_charges=True)
        else:
            return CharacterCapabilities(can_teleport_natively=False, can_teleport_with_charges=False)

    def discover_capabilities(self, force = False):
        if IChar._CrossGameCapabilities is None or force:
            capabilities = self._discover_capabilities()
            self.capabilities = capabilities
        self._cast_duration = self.get_cast_frames() * 0.04 + 0.02
        Logger.info(f"Capabilities: {self.capabilities}")
        self.on_capabilities_discovered(self.capabilities)

    def on_capabilities_discovered(self, capabilities: CharacterCapabilities):
        pass

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
            wait(0.4, 0.5)
            keyboard.send(self._config.char["inventory_screen"])
            wait(0.25, 0.3)
            active_weapon_tab = self.get_active_weapon_tab()
        attempts = 0
        while active_weapon_tab == 2 and attempts < 5:
            self.switch_weapon()
            wait(0.15, 0.25)
            attempts += 1
            active_weapon_tab = self.get_active_weapon_tab()
        return active_weapon_tab == 1

    def get_active_weapon_tab(self) -> int:
        active_slot = -1
        #Check to make sure we are on our main weapon set in slot 1, and not the secondary set in slot 2
        keyboard.send(self._config.char["inventory_screen"])
        wait(0.25, 0.3)
        
        if self._template_finder.search_and_wait(["WS1"], threshold=0.84, time_out=4, roi=[862, 50, 110, 100]).valid:
            Logger.info("Weapon slot 1 is active")
            active_slot = 1
        elif self._template_finder.search_and_wait(["WS2"], threshold=0.84, time_out=4, roi=[862, 50, 110, 100]).valid:
            Logger.info("Weapon slot 2 is active")
            active_slot = 2
        else:
            Logger.warning("Could not determine the active weapon slot")
        keyboard.send(self._config.char["inventory_screen"])
        wait(0.25, 0.3)
        return active_slot

    def switch_weapon(self):
        wait(0.03)
        keyboard.send(self._char_config["weapon_switch"])
        wait(0.25, 0.3)
        self._cast_duration = self.get_cast_frames() * 0.04 + 0.02
        # Update our cast frames when weapon swapping based on our FCR with those weapons

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
        if img is None:
            img = self._screen.grab()
        skill_img = cut_roi(img, self._config.ui_roi["skill_right"])
        charge_mask, _ = color_filter(skill_img, self._config.colors["blue"])
        if np.sum(charge_mask) > 0:
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
       if self._skill_hotkeys["teleport"] and not self._ui_manager.is_right_skill_selected(["TELE_ACTIVE", "TELE_INACTIVE"]):
            keyboard.send(self._skill_hotkeys["teleport"])
            wait(0.1, 0.2)
       return self._ui_manager.is_right_skill_selected(["TELE_ACTIVE", "TELE_INACTIVE"])

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
        if not self.capabilities:
            self.discover_capabilities(True)
        # if teleport hotkey is set and if teleport is not already selected
        if self.capabilities.can_teleport_natively:
            self.select_tp()

    def hold_move(self, pos_monitor: Tuple[float, float], force_tp: bool = False, force_move: bool = False):
        mouse.move(*pos_monitor, delay_factor = [.02,.04])

    def move(self, pos_monitor: Tuple[float, float], force_tp: bool = False, force_move: bool = False):
        factor = self._config.advanced_options["pathing_delay_factor"]
        if self._skill_hotkeys["teleport"] and (force_tp or(self._ui_manager.is_right_skill_selected(["TELE_ACTIVE"]) and self._ui_manager.is_right_skill_active())):
            mouse.move(pos_monitor[0], pos_monitor[1], randomize=2, delay_factor=[factor*0.1, factor*0.14])
            wait(0.02, 0.03)
            mouse.click(button="right")
            wait(0.02, 0.03)
            mouse.release(button="right")
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
            wait(0.012, 0.02)
            if force_move:
                keyboard.send(self._config.char["force_move"])
            else:
                mouse.click(button="left")
    
    def open_tp(self):
        # will check if tp is available and select the skill
        if not self._ui_manager.has_tps():
            Logger.debug("No TPs")
            return False
        mouse.click(button="right")
        return True

    def tp_town(self):
        if not self.open_tp(): return False
        roi_mouse_move = [
            int(self._config.ui_pos["screen_width"] * 0.3),
            0,
            int(self._config.ui_pos["screen_width"] * 0.4),
            int(self._config.ui_pos["screen_height"] * 0.7)
        ]
        pos_away = self._screen.convert_abs_to_monitor((-167, -30))
        wait(0.8, 1.3) # takes quite a while for tp to be visible
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
                wait(0.8, 1.3) # takes quite a while for tp to be visible
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

    def pre_travel(self, do_pre_buff=True):
        if do_pre_buff:
            self.pre_buff(switch_back=not self._config.char["teleport_weapon_swap"])

    def post_travel(self):
        if self._config.char["teleport_weapon_swap"]:
            self.switch_weapon()
            self.verify_active_weapon_tab()

    def prepare_attack(self):
        pass

    def post_attack(self):
        pass

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
    
    def cast_melee_to_monster(self, skill_key: str, time_in_s: float, monster: dict, mouse_button: str = "left") -> bool:
        if self._skill_hotkeys[skill_key]:
            if type(monster) is dict:
                mid = monster['id']
                Logger.debug(f"Meleeing monster {mid} with {skill_key} ({round(monster['position'][0], 2)}, {round(monster['position'][0], 2)})")
                keyboard.send(self._char_config["stand_still"], do_release=False)
                wait(0.03, 0.4)
                keyboard.send(self._skill_hotkeys[skill_key])
                wait(0.03, 0.4)
                start = time.time()
                while (time.time() - start) < time_in_s:
                    monster = find_monster(mid, self._api)
                    self._pather.move_mouse_to_monster(monster)
                    wait(0.03, 0.04)
                    mouse.press(button=mouse_button)
                    wait(0.03, 0.04)
                    monster = find_monster(mid, self._api)
                    if monster is None or monster["mode"] == 12:
                        break
                mouse.release(button=mouse_button)
                wait(0.03, 0.04)
                keyboard.release(self._config.char["stand_still"])
                wait(0.03, 0.04)
                return True
            else:
                Logger.error(f"Invalid monster {monster}")
        return False

    def clear_zone(self, dest_world=None, pickit_func=None) -> int:
        looted_uniques = set()
        picked_up_items = 0
        pf = PathFinder(self._api)
        nodes = pf.solve_tsp(dest_world)
        for node in nodes:
            self._pather.traverse(node, self, 0, do_pre_move=True, obj=False, kill=False, time_out=10.0)
            picked_up_items += self.kill_uniques(lambda: pickit_func(), 20.0, looted_uniques)
        self.post_attack()
        return picked_up_items

    def _pre_buff_cta(self, extra_cast_delay: float = 0.0):
        # Save current skill img
        skill_before = cut_roi(self._screen.grab(), self._config.ui_roi["skill_right"])
        # Try to switch weapons and select bo until we find the skill on the right skill slot
        start = time.time()
        switch_sucess = False
        while time.time() - start < 4:
            keyboard.send(self._char_config["weapon_switch"])
            wait(0.3, 0.35)
            keyboard.send(self._char_config["battle_command"])
            wait(0.1, 0.19)
            if self._ui_manager.is_right_skill_selected(["BC", "BO"]):
                switch_sucess = True
                break
        if not switch_sucess:
            Logger.warning("You dont have Battle Command bound, or you do not have CTA. ending CTA buff")
        else:
            # We switched succesfully, let's pre buff
            delay = self._cast_duration + extra_cast_delay
            Logger.debug("Casting Battle Command with key: " + self._char_config["battle_command"])
            mouse.click(button="right")
            wait(delay + 0.16, delay + 0.18)
            keyboard.send(self._char_config["battle_orders"])
            wait(0.1, 0.19)
            Logger.debug("Casting Battle Orders with key: " + self._char_config["battle_orders"])
            mouse.click(button="right")
            wait(delay + 0.16, delay + 0.18)
            if "shout" in self._skill_hotkeys:
                keyboard.send(self._skill_hotkeys["shout"])
                wait(0.1, 0.19)
                Logger.debug("Casting Shout with key: " + self._skill_hotkeys["shout"])
                mouse.click(button="right")
                wait(delay + 0.16, delay + 0.18)

        # Make sure the switch back to the original weapon is good
        start = time.time()
        while time.time() - start < 4:
            keyboard.send(self._char_config["weapon_switch"])
            wait(0.3, 0.35)
            skill_after = cut_roi(self._screen.grab(), self._config.ui_roi["skill_right"])
            _, max_val, _, _ = cv2.minMaxLoc(cv2.matchTemplate(skill_after, skill_before, cv2.TM_CCOEFF_NORMED))
            if max_val > 0.9:
                break
            else:
                Logger.warning("Failed to switch weapon, try again")
                wait(0.5)
    
    def filter_monster(self, monsterlist, area):
        filtered_monster = []
        boss = False
        for monster in monsterlist:
            if monster["bossID"] != 0 and monster["corpse"] == False:
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
            if mon["bossID"] != 0: return 0
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

    def kill_pindle(self) -> bool:
        raise ValueError("Pindle is not implemented!")

    def kill_shenk(self) -> bool:
        raise ValueError("Shenk is not implemented!")

    def kill_eldritch(self) -> bool:
        raise ValueError("Eldritch is not implemented!")

    def kill_council(self) -> bool:
        raise ValueError("Council is not implemented!")

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

    def loot_uniques(self, pickit, time_out: float=20.0, looted_uniques: set=set(), boundary=None) -> int:
        picked_up_items = 0
        start = time.time()
        # Loot all the dead uniques/champs that may be off screen
        if pickit is not None:
            unlooted = get_unlooted_monsters(self._api, CHAMPS_UNIQUES, looted_uniques, boundary, max_distance=50)
            while len(unlooted) > 0 and time.time() - start < time_out:
                data = self._api.get_data()
                if data is not None:
                    if not self._pather.traverse(unlooted[0]["position"] - data["area_origin"], self, verify_location=False, time_out=6, dest_distance=10):
                        looted_uniques.add(unlooted[0]["id"])
                picked_up_items += pickit()
                for m in unlooted:
                    if m["dist"] < 15:
                        looted_uniques.add(m["id"])
                        print(f"Looted champ/unique monster with ID {m['id']}")
                unlooted = get_unlooted_monsters(self._api, CHAMPS_UNIQUES, looted_uniques, boundary, max_distance=50)
        return picked_up_items

    def kill_uniques(self, pickit: FunctionType, time_out: float=9.0, looted_uniques: set=set()) -> bool:
        raise ValueError("Kill uniques not implemented")

if __name__ == "__main__":
    import os
    import keyboard
    keyboard.add_hotkey('f12', lambda: os._exit(1))
    print(f"Get on D2R screen and press F11 when ready")
    keyboard.wait("f11")
    from utils.misc import cut_roi
    from config import Config
    from template_finder import TemplateFinder
    from ui import UiManager
    from ocr import Ocr
    from obs import ObsRecorder

    config = Config()
    obs_recorder = ObsRecorder(config)
    skill_hotkeys = {}
    char_config = config.char
    screen = Screen()
    template_finder = TemplateFinder(screen)
    ui_manager = UiManager(self._screen, self._template_finder, self._obs_recorder, self._pather, self._game_stats)
    ocr = Ocr()

    i_char = IChar({}, screen, template_finder, ui_manager)

    while True:
        print(i_char.get_skill_charges(screen.grab()))
        wait(1)
        raise ValueError("Diablo CS Trash is not implemented!")

