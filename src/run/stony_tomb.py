from unittest.mock import seal
import cv2
import time
from char.i_char import IChar
from config import Config
from logger import Logger
from pather import Location, Pather
from typing import Union
from item.pickit import PickIt
from template_finder import TemplateFinder
from town.town_manager import TownManager
from ui import UiManager
from utils.misc import wait
from utils.custom_mouse import mouse
from screen import Screen
import math
from api.mapassist import MapAssistApi
from pathing.pather_v2 import PatherV2
from obs import ObsRecorder


class Stony_Tomb:
    def __init__(
        self,
        screen: Screen,
        template_finder: TemplateFinder,
        pather: Pather,
        town_manager: TownManager,
        ui_manager: UiManager,
        char: IChar,
        pickit: PickIt,
        api: MapAssistApi,
        pather_v2: PatherV2,
        obs_recorder: ObsRecorder,
    ):
        self._config = Config()
        self._screen = screen
        self._template_finder = template_finder
        self._pather = pather
        self._town_manager = town_manager
        self._ui_manager = ui_manager
        self._char = char
        self._pickit = pickit
        self._picked_up_items = False
        self.used_tps = 0
        self._api = api
        self._pather_v2 = pather_v2
        self._obs_recorder = obs_recorder

    def approach(self, start_loc: Location) -> Union[bool, Location, bool]:
        Logger.info("Run Stony Tomb")
        if not self._char.capabilities.can_teleport_natively:
            raise ValueError("Pit requires teleport")
        if not self._town_manager.open_wp(start_loc):
            return False
        wait(0.4)
        self._ui_manager.use_wp(2, 2)
        return Location.A2_STONY_WP
    
    def battle(self, do_pre_buff: bool) -> Union[bool, tuple[Location, bool]]:
        #if not self._pather_v2.wait_for_location("a4_diablo_wp"): return False
        
        if do_pre_buff: self._char.pre_buff()

        if self._config.char["teleport_weapon_swap"] and not self._config.char["barb_pre_buff_weapon_swap"]:
            self._char.switch_weapon()

        if not self._pather_v2.traverse("Rocky Waste", self._char): 
            if (self._api.data["current_area"]=='RockyWaste'):
                Logger.info ('Rocky Waste')
            else:
                return False
        count = 0
        while (self._api.data["current_area"]!='RockyWaste'):
            center = self._screen.convert_abs_to_monitor([0,0])
            self._char.pre_move ()
            self._pather_v2.go_to_area ("Rocky Waste", "Rocky Waste")
            wait (0.5, 0.6)
            count +=1
            if count > 3:
                return False
        #self._pather_v2.activate_poi(["255", "392", "393", "255","394","255", "396", "395", "255"], "test")
        counter = 0
        pois = ["Stony Tomb Level 1", "TombsWallTorchRight", "TombsWallTorchLeft", "Stony Tomb Level 2", "SparklyChest"]
        for poi in pois:
            if counter == 0:
                #if do_pre_buff: self._char.pre_buff()
                monster = self._pather_v2.traverse(poi, self._char, kill=False, verify_location=True)
                if self._config.char["teleport_weapon_swap"]:
                    self._char.switch_weapon()
                    self._char.verify_active_weapon_tab()
            elif counter == 1 or counter ==2:
                monster = self._pather_v2.traverse(poi, self._char, kill=True, obj=True, verify_location=False)
            else:
                monster = self._pather_v2.traverse(poi, self._char, kill=True, verify_location= True)
            while (type(monster)==dict):            
                self._char.kill_uniques (monster)
                picked_up_items = self._pickit.pick_up_items (self._char)
                if counter == 1 or counter ==2:
                    monster = self._pather_v2.traverse(poi, self._char, kill=True, obj=True, verify_location=False)
                else:      
                    monster = self._pather_v2.traverse(poi, self._char, kill=True, verify_location= True)
            count = 0
            if counter != 1 and counter != 2:
                while (self._api.data["current_area"]!=poi.replace(" ","")):
                    self._pather_v2.traverse(poi, self._char, kill=True, verify_location= True)
                    if "Stony Tomb Level" in poi:
                        self._pather_v2.go_to_area (poi, poi)
                    elif poi == "SparklyChest":
                        self._pather_v2.activate_poi (poi, poi, char=self._char, offset=[-4, -6]) 
                        wait (0.5, 1.0)
                        picked_up_items = self._pickit.pick_up_items (self._char)
                        break 
                    else:
                        #self._pather_v2.activate_poi (poi, poi, char=self._char)  
                        pass  
                    
                    wait (0.5, 1.5)
                    if count > 3:
                        return False
                    count += 1
            counter += 1
        #kill Diablo
        return (Location.A2_STONY_END, picked_up_items)