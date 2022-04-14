from d2r.d2r_api import D2rApi
from char.i_char import IChar
from config import Config
from logger import Logger
from pathing import Location, OldPather
from typing import Union
from pickit.pixel_pickit import PixelPickit
from pathing import Pather
from template_finder import TemplateFinder
from town.town_manager import TownManager
from ui import UiManager
from utils.misc import wait
from dataclasses import dataclass
from screen import Screen
import random
from obs import ObsRecorder


class Nihlathak:
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
        Logger.info("Run Nihlathak")
        if not self._char.can_tp:
            raise ValueError("Nihlathak requires teleport")
        if not self._town_manager.open_wp(start_loc):
            return False
        wait(0.4)
        if self._ui_manager.use_wp(5, 5): # use Halls of Pain Waypoint (5th in A5)
            return Location.A5_NIHLATHAK_START
        return False
    
    def _check_dangerous_monsters(self):
        if self._config.char["chicken_nihlathak_conviction"]:
            data = self._api.get_data()
            for m in data["monsters"]:
                if "Nihlathak" in m["name"] and "CONVICTION" in m["state_strings"]:
                    Logger.info("Detected a Conviction on Nihlathak, will chicken...")
                    self._ui_manager.save_and_exit(does_chicken=True)
                    return True
        return False

    def _go_to_nihlathak(self, dest_dist):
        if not self._pather.traverse("Nihlathak", self._char, verify_location=True, dest_distance=dest_dist):
            if not self._pather.traverse("Nihlathak", self._char, verify_location=True, jump_distance=8, dest_distance=dest_dist): return False
        return True

    def battle(self, do_pre_buff: bool) -> Union[bool, tuple[Location, bool]]:
        is_barb = "_barb" in self._char._char_config["type"]
        if not self._api.wait_for_area("HallsOfPain"): return False
        
        self._char.pre_travel(do_pre_buff)

        if not self._pather.traverse("Halls of Vaught", self._char, verify_location=True):
            if not self._pather.traverse("Halls of Vaught", self._char, verify_location=True, jump_distance=8):
                return False

        self._char.post_travel()

        self._pather.click_poi("Halls of Vaught", offset=(35, -39.5), time_out=5, target_area="HallsOfVaught")
        if not self._api.wait_for_area("HallsOfVaught"):
            self._pather.click_poi("Halls of Vaught", offset=(35, -39.5), time_out=5, target_area="HallsOfVaught")
            if not self._api.wait_for_area("HallsOfVaught"):
                if not self._pather.go_to_area("Halls of Vaught", "HallsOfVaught", entrance_in_wall=False, randomize=2, time_out=25, offset=[44, 0]):
                    if not self._pather.go_to_area("Halls of Vaught", "HallsOfVaught", entrance_in_wall=True, randomize=4, time_out=25, offset=[35, -39.5]):
                        return False

        self._go_to_nihlathak(50)
        if self._check_dangerous_monsters(): return False
        if is_barb: self._char.cast_aoe("howl")

        if not self._go_to_nihlathak(15): return False
        if self._check_dangerous_monsters(): return False
        self._char.kill_nihlathak()
        
        if is_barb: self._char.cast_aoe("howl")
        return (Location.A5_NIHLATHAK_END, self._pickit.pick_up_items(self._char, False))
