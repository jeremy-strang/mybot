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

class Mephisto:
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
        Logger.info("Run Meph")
        if not self._char.capabilities.can_teleport_natively:
            raise ValueError("Meph requires teleport")
        if not self._town_manager.open_wp(start_loc):
            return False
        wait(0.4)
        if self._ui_manager.use_wp(3, 8):
            return Location.A3_MEPH_START
        return False

    def battle(self, do_pre_buff: bool) -> Union[bool, tuple[Location, bool]]:
        if not self._pather.wait_for_location("DuranceOfHateLevel2"): return False
        if do_pre_buff:
            self._char.pre_buff()

        if self._config.char["teleport_weapon_swap"] and not self._config.char["barb_pre_buff_weapon_swap"]:
            self._char.switch_weapon()

        if not self._pather.traverse("Durance of Hate Level 3", self._char,verify_location=True): return False
        if not self._pather.go_to_area("Durance of Hate Level 3", "DuranceOfHateLevel3"): return False
        if not self._pather.traverse((69, 54), self._char, verify_location=True): return False

        if self._config.char["teleport_weapon_swap"]:
            self._char.switch_weapon()
            self._char.verify_active_weapon_tab()

        self._char.kill_mephisto()
        picked_up_items = self._pickit.pick_up_items(self._char)
        return (Location.A3_MEPH_END, picked_up_items)
