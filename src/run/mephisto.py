from char.i_char import IChar
from config import Config
from logger import Logger
from pathing import Location, OldPather
from typing import Union
from pickit.pixel_pickit import PixelPickit
from d2r.d2r_api import D2rApi
from pathing import Pather
from template_finder import TemplateFinder
from town.town_manager import TownManager
from ui import UiManager
from utils.misc import wait, is_in_roi
from utils.custom_mouse import mouse
from screen import Screen
import time
import keyboard
from state_monitor import StateMonitor
from obs import ObsRecorder

COUNCIL_POS_LEFT = (101, 118)
COUNCIL_POS_MID = (150, 66)
COUNCIL_POS_RIGHT = (97, 25)
MEPHISTO_POS = (69, 54)

class Mephisto:
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
        Logger.info("Run Meph")
        if not self._char.can_tp:
            raise ValueError("Meph requires teleport")
        if not self._town_manager.open_wp(start_loc):
            return False
        wait(0.4)
        if self._ui_manager.use_wp(3, 8):
            return Location.A3_MEPH_START
        return False

    def battle(self, do_pre_buff: bool) -> Union[bool, tuple[Location, bool]]:
        if not self._api.wait_for_area("DuranceOfHateLevel2"): return False
        
        self._char.pre_travel(do_pre_buff)

        if not self._pather.traverse("Durance of Hate Level 3", self._char, verify_location=True, slow_finish=True): return False
        if not self._pather.go_to_area("Durance of Hate Level 3", "DuranceOfHateLevel3"): return False

        picked_up_items = False

        pickit_func = lambda: self._pickit.pick_up_items(self._char)
        looted_uniques = set()
        if self._config.mephisto["kill_council"]:
            for pos in [COUNCIL_POS_MID, COUNCIL_POS_LEFT, COUNCIL_POS_RIGHT]:
                self._pather.traverse(pos, self._char, verify_location=True)
                wait(0.1)
                picked_up_items |= self._char.kill_uniques(pickit_func, looted_uniques=looted_uniques, min_attack_time=2)

        self._pather.traverse(MEPHISTO_POS, self._char, verify_location=True)
        self._char.post_travel()

        self._char.kill_mephisto()
        wait(0.2)
        picked_up_items |= self._pickit.pick_up_items(self._char)
        
        if self._config.general["loot_screenshots"]:
            keyboard.send(self._config.char["show_items"])
            wait(0.7)
            self._pickit.take_loot_screenshot()
            keyboard.send(self._config.char["show_items"])
            wait(0.1)

        return (Location.A3_MEPH_END, picked_up_items)
