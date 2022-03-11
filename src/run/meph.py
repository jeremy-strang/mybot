from char.i_char import IChar
from config import Config
from logger import Logger
from pather import Location, Pather
from typing import Union
from item.pickit import PickIt
from api.mapassist import MapAssistApi
from pathing.pather_v2 import PatherV2
from town.town_manager import TownManager
from ui import UiManager
from utils.misc import wait, is_in_roi
from utils.custom_mouse import mouse
from screen import Screen
import time
from state_monitor import StateMonitor
from obs import ObsRecorder


class Meph:
    def __init__(
        self,
        screen: Screen,
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
        self._pather = pather
        self._town_manager = town_manager
        self._ui_manager = ui_manager
        self._char = char
        self._pickit = pickit
        self._api = api
        self._pather_v2 = pather_v2
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
        if not self._pather_v2.wait_for_location("DuranceOfHateLevel2"): return False
        if do_pre_buff:
            self._char.pre_buff()

        if self._config.char["teleport_weapon_swap"] and not self._config.char["barb_pre_buff_weapon_swap"]:
            self._char.switch_weapon()

        if not self._pather_v2.traverse("Durance of Hate Level 3", self._char,verify_location=True): return False
        if not self._pather_v2.go_to_area("Durance of Hate Level 3", "DuranceOfHateLevel3"): return False
        if not self._pather_v2.traverse((69, 54), self._char,verify_location=True): return False

        if self._config.char["teleport_weapon_swap"]:
            self._char.switch_weapon()
            self._char.verify_active_weapon_tab()

        if self._char._char_config['type'] == 'hammerdin':
            self._char.kill_meph()
        elif self._char._char_config['type'] == 'light_sorc' or self._char._char_config['type'] == 'necro':
            game_state = StateMonitor(['Mephisto'],self._api)
            result = self._char.kill_meph(game_state)
            x = game_state._area_pos[0]
            y = game_state._area_pos[1]
            #go to mephs body
            self._pather_v2.traverse((x, y), self._char)
            game_state.stop()
        else:
            raise ValueError("Andy hdin or light sorc or necro")




        picked_up_items = self._pickit.pick_up_items(self._char)
        return (Location.A3_MEPH_END, picked_up_items)


if __name__ == "__main__":
    import keyboard
    import os
    keyboard.add_hotkey('f12', lambda: os._exit(1))
    keyboard.wait("f11")
    from bot import Bot
    from config import Config
    from game_stats import GameStats
    config = Config()
    screen = Screen(config.general["monitor"])
    game_stats = GameStats()
    bot = Bot(screen, game_stats)
    self = bot._meph
    # self._pather_v2.wait_for_location("DuranceOfHateLevel2")
    # self._pather_v2.traverse("Durance of Hate Level 3", self._char)
    # self._go_to_area("Durance of Hate Level 3", "DuranceOfHateLevel3")
    # # if not self._pather_v2.traverse((136, 176), self._char): return False
    # self._char.kill_meph(self._api, self._pather_v2)
    # picked_up_items = self._pickit.pick_up_items(self._char)
    while 1:
        data = self._api.get_data()
        if data is not None:
            print(data["player_pos_area"])
        print("-----")
        time.sleep(0.5)
