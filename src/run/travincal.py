import math
import time
import keyboard
from pytest import skip
from d2r.d2r_api import D2rApi
from char import IChar
from config import Config
from logger import Logger
from pathing import Location, OldPather
from typing import Union
from pickit.pixel_pickit import PixelPickit
from pathing import Pather
from screen import Screen
from template_finder import TemplateFinder
from town.town_manager import TownManager
from ui import UiManager
from utils.custom_mouse import mouse
from utils.misc import wait
from state_monitor import StateMonitor
from obs import ObsRecorder
from constants import Roi

class Travincal:

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
    
    def _check_dangerous_monsters(self):
        wait(0.1)
        data = self._api.get_data()
        if data and self._config.char["chicken_council_conviction"]:
            for m in data["monsters"]:
                if m["dist"] < 100 and "CONVICTION" in str(m["state_strings"]):
                    Logger.info("Detected Conviction Aura on council, will chicken...")
                    return True
        if data and self._config.char["chicken_council_might"]:
            for m in data["monsters"]:
                if m["dist"] < 100 and "MIGHT" in str(m["state_strings"]):
                    Logger.info("Detected Might Aura on council, will chicken...")
                    return True
        return False

    def approach(self, start_loc: Location) -> Union[bool, Location]:
        # Go to Travincal via waypoint
        Logger.info("Run Trav")
        if not self._town_manager.open_wp(start_loc):
            return False
        wait(0.4)
        if self._ui_manager.use_wp(3, 7):
            return Location.A3_TRAV_START
        return False
    
    def _avoid_durance(self):
        # Hack in case we end up in Durance by accidentally clicking the stairs
        data = self._api.get_data()
        if data is not None and data["current_area"] == "DuranceOfHateLevel1":
            if not self._pather.go_to_area("Travincal", "Travincal", True, time_out=5.0):
                self._pather.go_to_area("Travincal", "Travincal", True, time_out=5.0)

    def battle(self, do_pre_buff: bool) -> Union[bool, tuple[Location, bool]]:
        tele_swap = self._char.can_tp and self._config.char["teleport_weapon_swap"]
        if not self._api.wait_for_area("Travincal"): return False
        if do_pre_buff:
            self._char.pre_buff(switch_back=not tele_swap)
        
        Logger.debug("    Travincal battle(): Done prebuffing")
        if tele_swap and not self._config.char["barb_pre_buff_weapon_swap"]:
            self._char.switch_weapon()
        
        self._ui_manager.show_legacy()

        if self._char.can_tp:
            mouse.move(*self._screen.convert_abs_to_monitor((580, -20)), delay_factor=[0.10, 0.15])
            keyboard.send(self._char._skill_hotkeys["teleport"], do_release=False)
            wait((self._char._cast_duration - 0.01) * 6 + 0.02)
            keyboard.release(self._char._skill_hotkeys["teleport"])
            wait(0.3)
            data = self._api.get_data()
            council_dist = math.dist(data["player_pos_area"], (156, 113)) if data else 0
            Logger.debug(f'Council distance: {council_dist}, player position: {data["player_pos_area"]}')
            # if council_dist > 20:
            #     self._pather.traverse((156, 113), self._char, verify_location=False)
        elif not self._char.can_tp:
            self._char.pre_move()
            self._pather.walk_to_position((82, 164), time_out=20, step_size=8, threshold=12)
            self._pather.walk_to_position((159, 144), time_out=20, step_size=8, threshold=12)
        
        if tele_swap:
            self._ui_manager.hide_legacy()
            self._char.switch_weapon()
            self._char.verify_active_weapon_tab()

        skip_nopickup = False
        self._obs_recorder.start_recording_if_enabled()
        self._api.start_timer()

        wait(0.2, 0.3)
        if not self._char.can_tp and self._config.char["enable_combat_walking"]:
            self._char.toggle_run_walk(should_walk=True)
            self._pather.walk_to_position((156, 118), time_out=5, step_size=8, threshold=12)

        if self._check_dangerous_monsters():
            Logger.info(f"Aborting Travincal, dangerous affixes were detected")
            self._char.pre_move()
            if self._char.can_tp:
                self._pather.traverse((60, 188), self._char, verify_location=True)
            else:
                self._pather.walk_to_position((82, 164), time_out=20, step_size=8, threshold=12)
                self._pather.walk_to_position((60, 188), time_out=20, step_size=8, threshold=12)
            return (Location.A3_TRAV_CENTER_STAIRS, False)

        if self._char._char_config['type'] == 'hammerdin':
            self._char.kill_council()
            self._avoid_durance()
        elif self._char._char_config['type'] == 'singer_barb' or self._char._char_config['type'] == 'zerker_barb':
            # First kill council
            self._char.kill_council()
            # Loot once before hork to get anything that might get covered up after hork
            wait(0.1, 0.2)
            self._avoid_durance()
        elif self._char._char_config['type'] == 'light_sorc':
            game_state = StateMonitor(['CouncilMember'], self._api, unique_id=-1, many=True)
            self._char.kill_council(game_state)
            x = game_state._area_pos[0]
            y = game_state._area_pos[1]
            wait(0.05, .1)
            game_state.stop()
            self._avoid_durance()
            self._pather.traverse((x, y), self._char, time_out=4.0)
        else:
            raise ValueError("Unsupport character")
        self._api.get_metrics()

        if not skip_nopickup:
            skip_nopickup = self._ui_manager.disable_no_pickup()
    
        if not self._char.can_tp and self._config.char["enable_combat_walking"]:
            wait(0.1)
            self._char.toggle_run_walk(should_walk=False, skip_verification=True)

        # Check for loot once wherever we ended up after combat
        picked_up_items = self._pickit.pick_up_items(self._char, is_at_trav=True, skip_nopickup=skip_nopickup)
        wait(0.1, 0.15)
        self._avoid_durance()

        # If we can teleport we want to move back inside and also check loot there
        if self._char.can_tp or self._char.can_tp_with_charges:
            self._pather.traverse((156, 113), self._char, time_out=4.0)
            picked_up_items |= self._pickit.pick_up_items(self._char, is_at_trav=True, skip_nopickup=False)
            self._avoid_durance()
        else: # Else we need to make sure we loot both inside and outside the council room
            self._pather.walk_to_position((157, 104), time_out=3)
            picked_up_items |= self._pickit.pick_up_items(self._char, is_at_trav=True, skip_nopickup=skip_nopickup)
            wait(0.1, 0.15)
            self._avoid_durance()
            self._pather.walk_to_position((141, 113), time_out=3)
            picked_up_items |= self._pickit.pick_up_items(self._char, is_at_trav=True, skip_nopickup=False)
            wait(0.1, 0.15)
            self._avoid_durance()
        self._ui_manager.enable_no_pickup()

        if self._config.general["loot_screenshots"]:
            self._pather.teleport_to_position((142, 110), self._char)
            keyboard.send(self._config.char["show_items"])
            time.sleep(0.7)
            self._pickit.take_loot_screenshot()
            keyboard.send(self._config.char["show_items"])
            wait(0.1, 0.15)

        # self._obs_recorder.stop_recording_if_enabled()
        return (Location.A3_TRAV_CENTER_STAIRS, picked_up_items)
