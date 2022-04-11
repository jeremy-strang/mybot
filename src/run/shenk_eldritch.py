import math
import time
import keyboard
from d2r_mem.d2r_mem_api import D2rMemApi
from char import IChar
from char.skill import Skill
from config import Config
from logger import Logger
from pathing import Location, OldPather
from typing import Union
from pickit.pixel_pickit import PixelPickit
from screen import Screen
from template_finder import TemplateFinder
from town.town_manager import TownManager
from ui import UiManager
from utils.custom_mouse import mouse
from utils.misc import wait
from state_monitor import StateMonitor
from pathing import Pather
from obs import ObsRecorder

class ShenkEldritch:
    def __init__(
        self,
        screen: Screen,
        template_finder: TemplateFinder,
        old_pather: OldPather,
        town_manager: TownManager,
        ui_manager: UiManager,
        char: IChar,
        pickit: PixelPickit,
        api: D2rMemApi,
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
        Logger.info("Run Eldritch")
        # Go to Frigid Highlands
        if not self._town_manager.open_wp(start_loc): return False
        wait(0.4)
        if self._ui_manager.use_wp(5, 1):
            return Location.A5_ELDRITCH_START
        return False

    def battle(self, do_shenk: bool, do_pre_buff: bool, game_stats) -> Union[bool, tuple[Location, bool]]:
        if not self._pather.wait_for_location("FrigidHighlands"): return False
        if do_pre_buff:
            self._char.pre_buff()

        start = time.time()
        eld = self._api.find_monster_by_name("MinionExp")
        if not eld:
            self._pather.wander_towards((-50, -200), iterations=3, time_out=2.5)
        eld = self._api.find_monster_by_name("MinionExp")
        while not eld and time.time() - start < 2:
            wait(0.1)
            eld = self._api.find_monster_by_name("MinionExp")
        
        # Move to Eldritch
        if self._char.can_tp:
            self._pather.traverse(eld["position_area"], self._char)
        else:
            self._pather.walk_to_position(eld["position_area"])
        
        if self._char._char_config['type'] == 'necro':
            game_state = StateMonitor(['MinionExp'], self._api,super_unique=True)
            self._char.kill_eldrich_mem(game_state)
            game_state.stop()
        else:
            self._char.kill_eldritch()
        wait(0.1)
        loc = Location.A5_ELDRITCH_END
        picked_up_items = self._pickit.pick_up_items(self._char)

        # Shenk
        if do_shenk:
            Logger.info("Run Shenk")
            game_stats.update_location("Shk" if self._config.general['discord_status_condensed'] else "Shenk")
            self._curr_loc = Location.A5_SHENK_START
            
            self._pather.traverse("Frigid Highlands", self._char, verify_location=False)
            if not self._pather.traverse("Bloody Foothills", self._char, verify_location=False):
                self._pather.walk_to_poi("Bloody Foothills")
            
            current_area = self._pather.wander_towards((450, 120), self._char, "Bloody Foothills", time_out=1.5)
            if current_area != "BloodyFoothills":
                current_area = self._pather.wander_towards((150, 170), self._char, "Bloody Foothills", time_out=1.5)
            if current_area != "BloodyFoothills" and not self._pather.go_to_area("Bloody Foothills", "BloodyFoothills", entrance_in_wall=False, time_out=6):
                current_area = self._pather.wander_towards((50, 170), self._char, "Bloody Foothills", time_out=2)
                if current_area != "BloodyFoothills":
                    return False

            if self._char._char_config['type'] == 'necro':
                wait(0.1, 0.2)
                if not self._pather.traverse([95, 121], self._char): return False
                game_state = StateMonitor(['OverSeer'], self._api,super_unique=True)
                result = self._char.kill_shenk_mem(game_state)
                game_state.stop()
            else:
                if not self._char.can_tp or not self._pather.traverse((80, 117), self._char):
                    self._pather.walk_to_position((80, 117), time_out=7)
                self._char.kill_shenk()

            loc = Location.A5_SHENK_END
            wait(0.1)
            picked_up_items |= self._pickit.pick_up_items(self._char)

        return (loc, picked_up_items)
