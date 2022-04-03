from char.i_char import IChar
from config import Config
from logger import Logger
from pathing import Location, OldPather
from typing import Union
from item.pickit import PickIt
from api.mapassist import MapAssistApi
from pathing import Pather
from town.town_manager import TownManager
from ui import UiManager
from utils.misc import wait, is_in_roi
from utils.custom_mouse import mouse
from screen import Screen
import time

from state_monitor import StateMonitor
from obs import ObsRecorder

class Andariel:
    def __init__(
        self,
        screen: Screen,
        old_pather: OldPather,
        town_manager: TownManager,
        ui_manager: UiManager,
        char: IChar,
        pickit: PickIt,
        api: MapAssistApi,
        pather: Pather,
        obs_recorder: ObsRecorder,
    ):
        self._config = Config()
        self._screen = screen
        self._old_pather = old_pather
        self._town_manager = town_manager
        self._ui_manager = ui_manager
        self._char = char
        self._pickit = pickit
        self._api = api
        self._pather = pather
        self._obs_recorder = obs_recorder

    def approach(self, start_loc: Location) -> Union[bool, Location, bool]:
        Logger.info(f"Run Andy from {start_loc}")
        if not self._char.capabilities.can_teleport_natively:
            raise ValueError("Andy requires teleport")
        if not self._town_manager.open_wp(start_loc):
            return False
        wait(0.4)
        if self._ui_manager.use_wp(1, 8):
            return Location.A1_ANDY_START
        return False

    # "Catacombs Level 3"
    # CatacombsLevel1
    def battle(self, do_pre_buff: bool) -> Union[bool, tuple[Location, bool]]:
        if not self._pather.wait_for_location("CatacombsLevel2"): return False
        
        self._char.pre_travel(do_pre_buff)
        if not self._pather.traverse("Catacombs Level 3", self._char,verify_location=True): return False
        if not self._pather.go_to_area("Catacombs Level 3", "CatacombsLevel3", entrance_in_wall=False): return False
        if not self._pather.traverse("Catacombs Level 4", self._char,verify_location=True): return False
        if not self._pather.go_to_area("Catacombs Level 4", "CatacombsLevel4", entrance_in_wall=False): return False
        self._char.post_travel()

        if self._char._char_config['type'] == 'hammerdin':
            if not self._pather.traverse((65, 85), self._char): return False
            self._char.kill_andariel()
        elif self._char._char_config['type'] in ['light_sorc', 'necro', 'zerker_barb']:
            if not self._pather.traverse((46, 23), self._char): return False
            game_state = StateMonitor(['Andariel'], self._api)
            result = self._char.kill_andariel(game_state)
            if result:
                Logger.info("Andy died...")
            wait(0.1, .2)
            x = game_state._area_pos[0]
            y = game_state._area_pos[1]
            #go to andys body
            self._pather.traverse((x, y), self._char)
            game_state.stop()
        else:
            raise ValueError(f"Andariel is not implemented for characters of type {self._char._char_config['type']}")


        picked_up_items = self._pickit.pick_up_items(self._char)
        return (Location.A1_ANDY_END, picked_up_items)