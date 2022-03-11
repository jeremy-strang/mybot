from char.i_char import IChar
from config import Config
from logger import Logger
from pather import Location, Pather
from typing import Union
from item.pickit import PickIt
from api import MapAssistApi
from pathing import PatherV2
from town.town_manager import TownManager
from ui import UiManager
from utils.misc import wait, is_in_roi
from utils.custom_mouse import mouse
from screen import Screen
import time
from state_monitor import StateMonitor
from obs import ObsRecorder

class Tower:
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
        Logger.info("Run Tower")
        if not self._char.capabilities.can_teleport_natively:
            raise ValueError("Tower requires teleport")
        if not self._town_manager.open_wp(start_loc):
            return False
        wait(0.4)
        if self._ui_manager.use_wp(1, 4):
            return Location.A1_TOWER_START
        return False

    def battle(self, do_pre_buff: bool) -> Union[bool, tuple[Location, bool]]:
        if not self._pather_v2.wait_for_location("BlackMarsh"): return False
        if do_pre_buff:
            self._char.pre_buff()

        if self._config.char["teleport_weapon_swap"] and not self._config.char["barb_pre_buff_weapon_swap"]:
            self._char.switch_weapon()

        if not self._pather_v2.traverse("Forgotten Tower", self._char): return False
        if not self._pather_v2.go_to_area("Forgotten Tower", "ForgottenTower", entrance_in_wall=False,randomize=3): return False
        if not self._pather_v2.wait_for_location("ForgottenTower"): return False
        if not self._pather_v2.traverse("Tower Cellar Level 1", self._char): return False
        if not self._pather_v2.go_to_area("Tower Cellar Level 1", "TowerCellarLevel1", entrance_in_wall=False,randomize=4): return False
        if not self._pather_v2.traverse("Tower Cellar Level 2", self._char): return False
        if not self._pather_v2.go_to_area("Tower Cellar Level 2", "TowerCellarLevel2", entrance_in_wall=False,randomize=4): return False
        if not self._pather_v2.traverse("Tower Cellar Level 3", self._char): return False
        if not self._pather_v2.go_to_area("Tower Cellar Level 3", "TowerCellarLevel3", entrance_in_wall=False,randomize=4): return False
        if not self._pather_v2.traverse("Tower Cellar Level 4", self._char): return False
        if not self._pather_v2.go_to_area("Tower Cellar Level 4", "TowerCellarLevel4", entrance_in_wall=False,randomize=4): return False
        if not self._pather_v2.traverse("Tower Cellar Level 5", self._char): return False
        if not self._pather_v2.go_to_area("Tower Cellar Level 5", "TowerCellarLevel5", entrance_in_wall=False,randomize=4): return False

        if self._config.char["teleport_weapon_swap"]:
            self._char.switch_weapon()
            self._char.verify_active_weapon_tab()

        if not self._pather_v2.traverse("GoodChest", self._char): return False

        #need to add super unique names to the look up table 
        # ill just use the countess id for now
        #351218274,
        #4206342633
        game_state = StateMonitor(['DarkStalker'], self._api,super_unique=True)
        result = self._char.kill_tower(game_state)
        if result:
            Logger.info("Countess died...")
        wait(0.2, .4)
        x = game_state._area_pos[0]
        y = game_state._area_pos[1]
        #go to andys body
        self._pather_v2.traverse((x, y), self._char)
        game_state.stop()
        #del game_state
        picked_up_items = self._pickit.pick_up_items(self._char)
        return (Location.A1_TOWER_END, picked_up_items)

if __name__ == "__main__":
    import keyboard
    import os
    import sys
    keyboard.add_hotkey('f12', lambda: os._exit(1))
    keyboard.wait("f11")
    from bot import Bot
    from config import Config
    from game_stats import GameStats
    from pathing import PatherV2
    from api import MapAssistApi
    import threading
    from template_finder import TemplateFinder
    from ui import UiManager, char_selector
    from game_stats import GameStats
    from char.sorceress import LightSorc, BlizzSorc, NovaSorc
    from obs import ObsRecorder

    config = Config()
    obs_recorder = ObsRecorder(config)
    screen = Screen()
    game_stats = GameStats()

    api = MapAssistApi()
    api_thread = threading.Thread(target=api.start)
    api_thread.daemon = False
    api_thread.start()
    #mapassist api + new pather
    game_stats = GameStats() 
    template_finder = TemplateFinder(screen)
    ui_manager = UiManager(screen, template_finder, obs_recorder, game_stats)
    pather = Pather(screen, template_finder)

    bot = Bot(screen, game_stats, template_finder ,api)
    self = bot._andy



    pather_v2 = PatherV2(screen, api)

    char = LightSorc(config.light_sorc, screen, template_finder, ui_manager, pather)
    char.discover_capabilities()

    #pather_v2.traverse("Forgotten Tower", char)
    #sys.exit()
    while 1:
        data = self._api.get_data()
        if data is not None:
            print(data["player_pos_area"])
            #for obj in data['static_npcs']:
            #    print(obj)
        print("-----")
        time.sleep(0.5)
