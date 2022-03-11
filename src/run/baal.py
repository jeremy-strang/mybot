from char.i_char import IChar
from config import Config
from logger import Logger
from pather import Location, Pather
from typing import Union
from item.pickit import PickIt
from api.mapassist import MapAssistApi
from pathing import PatherV2
from town.town_manager import TownManager
from ui import UiManager
from utils.misc import wait, is_in_roi
from utils.custom_mouse import mouse
from screen import Screen
import time
from obs import ObsRecorder


class Baal:
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
        Logger.info("Run Baal")
        if not self._char.capabilities.can_teleport_natively:
            raise ValueError("Baal requires teleport")
        if not self._town_manager.open_wp(start_loc):
            return False
        wait(0.4)
        if self._ui_manager.use_wp(5, 8): # use Halls of Pain Waypoint (5th in A5)
            return Location.A5_BAAL_WORLDSTONE_KEEP_LVL2
        return False
    
    def _check_dangerous_monsters(self):
        if self._config.char["chicken_if_dolls"] or self._config.char["chicken_if_souls"]:
            data = self._api.get_data()
            for m in data["monsters"]:
                if "SoulKiller" in m["name"] and self._config.char["chicken_if_dolls"]:
                    Logger.debug("Detected a doll: " + m["name"])
                    Logger.info("Dolls detected, will chicken...")
                    self._ui_manager.save_and_exit(does_chicken=True)
                    return True
                if "BurningSoul" in m["name"] and self._config.char["chicken_if_souls"]:
                    Logger.debug("Detected a soul: " + m["name"])
                    Logger.info("Souls detected, will chicken...")
                    self._ui_manager.save_and_exit(does_chicken=True)
                    return True
        return False


    def battle(self, do_pre_buff: bool) -> Union[bool, tuple[Location, bool]]:
        if not self._pather_v2.wait_for_location("TheWorldStoneKeepLevel2"): return False
        if do_pre_buff:
            self._char.pre_buff()

        if self._config.char["teleport_weapon_swap"] and not self._config.char["barb_pre_buff_weapon_swap"]:
            self._char.switch_weapon()

        if not self._pather_v2.traverse("Worldstone Keep Level 3", self._char,verify_location=True): return False
        if not self._pather_v2.go_to_area("Worldstone Keep Level 3", "TheWorldStoneKeepLevel3"): return False

        if self._config.char["teleport_weapon_swap"]:
            self._char.switch_weapon()
            self._char.verify_active_weapon_tab()
            
        if not self._pather_v2.traverse("Throne of Destruction", self._char,verify_location=True): return False

        if self._check_dangerous_monsters(): return False
        if not self._pather_v2.go_to_area("Throne of Destruction", "ThroneOfDestruction"): return False
        # Attacks start: Clear room
        if not self._pather_v2.traverse((95, 55), self._char): return False
        if self._check_dangerous_monsters(): return False

        if self._config.char["send_throne_leecher_tp"]:
            Logger.debug("Sending Throne TP")
            if not self._pather_v2.traverse((115, 6), self._char): return False
            wait(0.2)
            self._char.open_tp()
            wait(0.2)
            if not self._pather_v2.traverse((95, 55), self._char): return False
        for _ in range(4):
            if not self._char.clear_throne(full=True): return False
            if not self._pather_v2.traverse((95, 45), self._char): return False
        start_time = time.time()
        picked_up_items = self._pickit.pick_up_items(self._char)

        wave_monsters = [
            "WarpedFallen", "WarpedShaman",
            "BaalSubjectMummy", "BaalColdMage",
            "CouncilMember",
            "VenomLord",
            "BaalsMinion"
        ]
        Logger.info("Baal wave starts.....")
        for wave_nr in range(5):
            wave_nr += 1
            Logger.info(f"Baal Wave: {wave_nr}")
            success, found_monsters = self._char.baal_idle(monster_filter=wave_monsters, start_time=start_time)
            if not success: return False
            if not self._char.clear_throne(monster_filter=wave_monsters, baal_wave=wave_nr): return False
            self._char.clear_throne()
            start_time = time.time()
            if wave_nr == 1 or wave_nr == 2:
                if not self._pather_v2.traverse((95, 42), self._char): return False
                self._char.pre_buff()
                picked_up_items |= self._pickit.pick_up_items(self._char)
            if wave_nr == 3 or wave_nr == 5 or wave_nr == 2 or wave_nr == 4:
                picked_up_items |= self._pickit.pick_up_items(self._char)
            if "BaalsMinion" in found_monsters:
                Logger.debug("Finished last baal wave, go to throne")
                break

        # If we are out of mana pots, and greaters are disabled, temporarily enable them for Baal
        data = self._api.get_data()
        greatermp_pickit_type = Config.items["misc_greater_mana_potion"].pickit_type
        do_pick_greatermp = greatermp_pickit_type in (1, 2)
        if not do_pick_greatermp and data is not None and data["belt_mana_pots"] <= 2:
            self._config.items["misc_greater_mana_potion"].pickit_type = 1
            Logger.debug("Temporarily enabling Greater Mana Potion pickup for Baal")

        # Pick items
        if not self._pather_v2.traverse((95, 26), self._char): return False
        picked_up_items |= self._pickit.pick_up_items(self._char)
        # Move to baal room

        if self._config.char["teleport_weapon_swap"]:
            self._char.switch_weapon()
            
        if not self._pather_v2.traverse((91, 15), self._char): return False
        if not self._pather_v2.go_to_area((15089, 5006), "TheWorldstoneChamber"): return False
        self._char.select_skill("teleport")
        if not self._pather_v2.traverse((136, 176), self._char, do_pre_move=False): return False

        if self._config.char["teleport_weapon_swap"]:
            self._char.switch_weapon()
            self._char.verify_active_weapon_tab()
            
        self._char.kill_baal()
        picked_up_items |= self._pickit.pick_up_items(self._char)
        # Restore initial greater mana pot pickit setting
        self._config.items["misc_greater_mana_potion"].pickit_type = greatermp_pickit_type
        return (Location.A5_BAAL_WORLDSTONE_CHAMBER, picked_up_items)


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
    self = bot._baal
    # self._go_to_area((15089, 5006), "TheWorldstoneChamber")
    # self._char.kill_baal()
    self._char.clear_throne(monster_filter=["BaalSubjectMummy", "BaalColdMage"])
    # while 1:
    #     data = self._api.get_data()
    #     if data is not None:
    #         print(data["player_pos_area"])
    #     print("-----")
    #     time.sleep(0.5)
