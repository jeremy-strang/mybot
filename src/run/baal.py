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
from utils.misc import normalize_text, wait, is_in_roi
from utils.custom_mouse import mouse
from screen import Screen
import time
from obs import ObsRecorder


class Baal:
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
        Logger.info("Run Baal")
        if not self._char.can_tp:
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
                if is_in_roi([70, 0, 50, 95], m["position_area"]):
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

    def _get_active_wave(self):
        data = self._api.get_data()
        if data:
            for m in data["monsters"]:
                name =normalize_text(m["name"])
                if m["mode"] != 12:
                    if name.startswith("warpedfallen") or name.startswith("warpedshaman"):
                        return 1
                    elif name.startswith("baalsubjectmummy") or name.startswith("baalcoldmage"):
                        return 2
                    elif name.startswith("councilmember"):
                        return 3
                    elif name.startswith("venomlord"):
                        return 4
                    elif name.startswith("baalsminion"):
                        return 5
        return False
    
    def _get_throne_monsters(self, corpses: bool = False):
        data = self._api.get_data()
        monsters = []
        if data:
            for m in data["monsters"]:
                if (not corpses and m["mode"] != 12) or (corpses and m["mode"] == 12):
                    monsters.append(m)
        return monsters

    def battle(self, do_pre_buff: bool) -> Union[bool, tuple[Location, bool]]:
        if not self._api.wait_for_area("TheWorldStoneKeepLevel2"): return False
        if do_pre_buff:
            self._char.pre_buff()

        if self._config.char["teleport_weapon_swap"] and not self._config.char["barb_pre_buff_weapon_swap"]:
            self._char.switch_weapon()

        if not self._pather.traverse("Worldstone Keep Level 3", self._char, verify_location=True, slow_finish=True): return False
        if not self._pather.go_to_area("Worldstone Keep Level 3", "TheWorldStoneKeepLevel3"): return False

        if self._config.char["teleport_weapon_swap"]:
            self._char.switch_weapon()
            self._char.verify_active_weapon_tab()
            
        if not self._pather.traverse("Throne of Destruction", self._char, verify_location=True, slow_finish=True): return False

        # if self._check_dangerous_monsters(): return False
        if not self._pather.go_to_area("Throne of Destruction", "ThroneOfDestruction"): return False
        # Attacks start: Clear room
        self._pather.traverse((95, 55), self._char)
        if self._check_dangerous_monsters(): return False

        if self._config.char["send_throne_leecher_tp"]:
            Logger.debug("Sending Throne TP")
            self._pather.traverse((115, 44), self._char)
            wait(0.4)
            self._char.open_tp()
            wait(0.4)
            self._pather.traverse((95, 55), self._char)
        # for _ in range(4):
        #     if not self._char.clear_throne(full=True): return False
        #     self._pather.traverse((95, 45), self._char)
        self._char.clear_throne(full=True)
        self._pather.traverse((95, 45), self._char)
        
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
        
        last_wave = 0
        started_wave5 = False
        cleared_wave5 = False

        self._pather.traverse((115, 44), self._char)
        self._char.pre_buff()
        start = time.time()
        last_pre_buff = start
        monsters_found_time = time.time()
        while not cleared_wave5 and time.time() - start < 300:
            monsters = self._get_throne_monsters()
            if len(monsters) > 0:
                monsters_found_time = time.time()
                if last_wave == 0:
                    picked_up_items |= self._pickit.pick_up_items(self._char)
                active_wave = self._get_active_wave()
                Logger.debug(f"    Found {len(monsters)} monsters, active wave detected: {active_wave}")
                if active_wave:
                    if active_wave == 5:
                        started_wave5 = True
                    self._char.clear_throne(baal_wave=active_wave)
                    last_wave = active_wave
                else:
                    self._char.clear_throne()
                monsters_found_time = time.time()
            else:
                Logger.debug(f"    No monsters found")
                if time.time() - last_pre_buff > 70:
                    self._pather.traverse((115, 44), self._char)
                    wait(0.1, 0.2)
                    self._char.pre_buff()
                    last_pre_buff = time.time()
                if started_wave5:
                    cleared_wave5 = True
                    Logger.warning("    Started wave 5 and now no monsters are found, so it must be clear...")
                    break
                if time.time() - monsters_found_time > 30:
                    Logger.warning("    No monsters found for over 30 seconds, assuming clear...")
                    break
                if not started_wave5:
                    Logger.debug(f"        Idling for next wave")
                    corpses = self._get_throne_monsters(corpses=True)
                    for m in corpses:
                        if "BaalsMinion" in m["name"]:
                            Logger.debug("    Determined wave 5 is dead from corpses")
                            cleared_wave5 = True
                    if cleared_wave5:
                        break
                    _, found_monsters = self._char.baal_idle(monster_filter=wave_monsters, start_time=start_time)
                    if "BaalsMinion" in found_monsters:
                        Logger.debug("Finished last baal wave, go to throne")
                        started_wave5 = True
                else:
                    cleared_wave5 = True
            wait(0.4, 0.5)
        
        wait(1, 2)
        if cleared_wave5:
            Logger.warning("Success! Confirmed wave 5 was cleared")
        else:
            Logger.warning("Did not confirm wave 5 was cleared")
        picked_up_items |= self._pickit.pick_up_items(self._char)

        monsters = self._get_throne_monsters()
        if len(monsters) > 0:
            self._char.clear_throne(full=True)

        self._char.pre_buff()

        # for wave_nr in range(5):
        #     wave_nr += 1
        #     Logger.info(f"Baal Wave: {wave_nr}")
        #     success, found_monsters = self._char.baal_idle(monster_filter=wave_monsters, start_time=start_time)
        #     if not success: return False
        #     self._char.clear_throne(monster_filter=wave_monsters, baal_wave=wave_nr)
        #     self._char.clear_throne()
        #     start_time = time.time()
        #     if wave_nr in [1, 2, 4]:
        #         self._pather.traverse((115, 44), self._char)
        #         self._char.pre_buff()
        #         picked_up_items |= self._pickit.pick_up_items(self._char)
        #     if wave_nr == 3 or wave_nr == 5 or wave_nr == 2 or wave_nr == 4:
        #         picked_up_items |= self._pickit.pick_up_items(self._char)
        #     if "BaalsMinion" in found_monsters:
        #         Logger.debug("Finished last baal wave, go to throne")
        #         break

        # Pick items
        self._pather.traverse((95, 26), self._char)
        picked_up_items |= self._pickit.pick_up_items(self._char)

        if self._config.char["teleport_weapon_swap"]:
            self._char.switch_weapon()

        self._pather.traverse((91, 15), self._char)
        if not self._pather.go_to_area((15089, 5006), "TheWorldstoneChamber"): return False
        self._char.select_skill("teleport")
        if not self._pather.traverse((136, 176), self._char, do_pre_move=False): return False

        if self._config.char["teleport_weapon_swap"]:
            self._char.switch_weapon()
            self._char.verify_active_weapon_tab()
            
        self._char.kill_baal()
        wait(0.5)
        picked_up_items |= self._pickit.pick_up_items(self._char)
        return (Location.A5_BAAL_WORLDSTONE_CHAMBER, picked_up_items)
