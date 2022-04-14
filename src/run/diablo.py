from unittest.mock import seal
import cv2
import time
from char.i_char import IChar
from config import Config
from logger import Logger
from pathing import Location, OldPather
from typing import Union, Callable
from pickit.pixel_pickit import PixelPickit
from template_finder import TemplateFinder
from town.town_manager import TownManager
from ui import UiManager
from utils.misc import wait
from utils.custom_mouse import mouse
from screen import Screen
import math
from d2r.d2r_api import D2rApi
from pathing import Pather
from obs import ObsRecorder

class Diablo:
    def __init__(
        self,
        screen: Screen,
        template_finder: TemplateFinder,
        old_pather: OldPather,
        town_manager: TownManager,
        ui_manager: UiManager,
        char: IChar,
        pickit: PixelPickit,
        api: D2rApi,
        pather: Pather,
        obs_recorder: ObsRecorder,
    ):
        self._config = Config()
        self._screen = screen
        self._template_finder = template_finder
        self._old_pather = old_pather
        self._town_manager = town_manager
        self._ui_manager = ui_manager
        self._char = char
        self._pickit = pickit
        self._picked_up_items = False
        self.used_tps = 0
        self._api = api
        self._pather = pather
        self._obs_recorder = obs_recorder

    def approach(self, start_loc: Location) -> Union[bool, Location, bool]:
        Logger.info("Run Diablo")
        if not self._char.can_tp:
            raise ValueError("Diablo requires teleport")
        if not self._town_manager.open_wp(start_loc):
            return False
        wait(0.4)
        self._ui_manager.use_wp(4, 2)
        return Location.A4_DIABLO_WP
    
    def _battle_diablo(self, do_pre_buff: bool = True):
        self._char.pre_travel(do_pre_buff)
        diablo_pos_area = (7796 - self._api.data["area_origin"][0], 5296 - self._api.data["area_origin"][1])
        self._pather.traverse(diablo_pos_area, self._char, verify_location=False)
        diablo = self._api.wait_for_monster("Diablo", 15.0)
        self._char.post_travel()
        if diablo is not None:
            self._char.kill_diablo()
            return True
        return False

    def battle(self, do_pre_buff: bool) -> Union[bool, tuple[Location, bool]]:
        if not self._pather.wait_for_location("RiverOfFlame"): return False
        
        self._char.pre_travel(do_pre_buff)

        current_area = "RiverOfFlame"
        self._pather.traverse("The Chaos Sanctuary", self._char, verify_location=False)

        current_area = self._pather.wander_towards((200, -150), self._char, "ChaosSanctuary", time_out=3)
        if current_area != "ChaosSanctuary":
            if not self._pather.go_to_area("The Chaos Sanctuary", "ChaosSanctuary", False, time_out=5, char=self._char):
                current_area = self._pather.wander_towards((200, -150), self._char, "ChaosSanctuary", time_out=3)
        if current_area != "ChaosSanctuary": return False

        self._char.post_travel()

        #self._pather.activate_poi(["255", "392", "393", "255","394","255", "396", "395", "255"], "test")
        self._pather.traverse([7796 - self._api.data["area_origin"][0], 5296 - self._api.data["area_origin"][1]], self._char, kill=False, obj=True)
        pickit_func = lambda: self._pickit.pick_up_items(self._char)
        pois = ["DiabloSeal1", "DiabloSeal2", "DiabloSeal3", "DiabloSeal5", "DiabloSeal4"]
        looted = set()
        picked_up_items = 0
        def _poi_callback(poi: dict):
            self._pather.traverse(poi["position_area"], self._char, time_out=10)
            self._pather.activate_poi(poi["position"])
            picked_up_items += self._char.kill_uniques(pickit_func, 20, looted_uniques=looted, min_attack_time=4)
            return picked_up_items
        self._char.clear_zone(pickit_func=pickit_func, poi_list=pois, poi_callback=_poi_callback)

        diablo_died = False
        if not self._battle_diablo(True):
            for poi in pois:
                self._pather.traverse(poi, self._char)
                if not self._pather.click_poi(poi, time_out = 3.0):
                    self._pather.walk_to_poi(poi, 2)
                    if not self._pather.activate_poi(poi, char=self._char):
                        self._pather.click_poi(poi, time_out = 3.0)
                picked_up_items += self._char.kill_uniques(pickit_func, 20, looted_uniques=looted, min_attack_time=4)
            diablo_died = self._battle_diablo(False)
        else:
            diablo_died = True

        picked_up_items += pickit_func()
        
        if diablo_died:
            Logger.debug("Diablo died!")
        else:
            Logger.warning("Failed to spawn/kill Diablo")
        return (Location.A4_DIABLO_END, picked_up_items)

        # counter = 0
        # pois = 
        # for poi in pois:
        #     if counter == 2:
        #         print ("DEBUG")
        #     if counter == 2 or counter == 4:
        #         if do_pre_buff: self._char.pre_buff()
        #     monster = self._pather.traverse(poi, self._char, kill=True)
        #     while (type(monster)==dict):
        #         if monster ["boss_id"] == 37:
        #             self._char.kill_uniques (monster, offset=[10,10])            
        #         self._char.kill_uniques (monster)
        #         picked_up_items = self._pickit.pick_up_items (self._char)  
        #         monster = self._pather.traverse(poi, self._char, kill=True)
        #     self._pather.activate_poi(poi, poi, collection="objects", char=self._char)

        #     monster = self._char.kill_around (self._api, special = True)
        #     while (type (monster)==dict):
        #         #self._char.pre_move ()
        #         #self._pather.traverse ([1+monster["position"][0]- self._api.data["area_origin"][0], 1+monster["position"][1]- self._api.data["area_origin"][1]], self._char, pickit = self._pickit)
        #         self._char.kill_uniques (monster)
        #         picked_up_items = self._pickit.pick_up_items (self._char) 
        #         monster = self._pather.traverse(poi, self._char, kill=True)
        #         #self._char.move ([center[0]+300, center[1]-160])
        #     counter += 1
        # #kill Diablo
        # self._pather.traverse([7796- self._api.data["area_origin"][0],5296- self._api.data["area_origin"][1]], self._char, kill=False,obj=True)
        # counter=0
        # while (type (self._char.kill_around (self._api, 1,15,True))!=dict):
        #     counter+=1
        #     wait (0.8, 1)
        #     if counter > 20:
        #         return False
        # monster = self._char.kill_around (self._api, 10,15,True)
        # while (type (monster)==dict):
        #     self._char.kill_uniques (monster, offset = [2, 2])
        #     monster = self._char.kill_around (self._api, 10,15,True)
        # picked_up_items = self._pickit.pick_up_items (self._char)
        # return (Location.A4_DIABLO_END, picked_up_items)
