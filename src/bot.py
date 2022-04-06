from transitions import Machine
import time
import keyboard
import time
import os
import random
import cv2
from copy import copy
from typing import Union
from collections import OrderedDict
from run.stony_tomb import StonyTomb
from transmute import Transmute
from utils.custom_mouse import mouse
from utils.misc import wait
from game_stats import GameStats
from logger import Logger
from config import Config
from screen import Screen
from template_finder import TemplateFinder
from char import IChar
from item import ItemFinder
from item.pickit import PickIt
from ui import UiManager, char_selector
from ui import BeltManager
from ui import CharSelector
from pathing import OldPather, Location
from npc_manager import NpcManager, Npc
from health_manager import HealthManager
from death_manager import DeathManager
from char.sorceress import LightSorc, BlizzSorc, NovaSorc
from char.trapsin import Trapsin
from char.hammerdin import Hammerdin
from char.barbarian.zerker_barb import ZerkerBarb
from char.barbarian.singer_barb import SingerBarb
from char.necro import Necro
from char.basic import Basic
from char.basic_ranged import Basic_Ranged
from obs import ObsRecorder
from utils.misc import wait, hms

from run import Pindleskin, ShenkEldritch, Travincal, Nihlathak, Summoner, Diablo, Baal, Andariel, Countess, Mephisto, Pit
from town import TownManager, A1, A2, A3, A4, A5, town_manager

# Added for dclone ip hunt
from messages import Messenger
from utils.dclone_ip import get_d2r_game_ip

#mapassist api + new old_pather
from pathing import Pather
from api import MapAssistApi

class Bot:

    _MAIN_MENU_MARKERS = ["MAIN_MENU_TOP_LEFT","MAIN_MENU_TOP_LEFT_DARK", "LOBBY_MENU_TOP_LEFT"]
    def __init__(self,
        screen: Screen,
        game_stats: GameStats,
        template_finder: TemplateFinder,
        mapi: MapAssistApi,
        obs_recorder: ObsRecorder,
        pick_corpse: bool = False
    ):
        self._screen = screen
        self._game_stats = game_stats
        self._messenger = Messenger()
        self._config = Config()
        self._template_finder = template_finder
        self._item_finder = ItemFinder()
        self._obs_recorder = obs_recorder
        self._api = mapi
        self._ui_manager = UiManager(self._screen, self._template_finder, self._obs_recorder, self._api, self._game_stats)
        self._belt_manager = BeltManager(self._screen, self._template_finder, self._api)
        self._old_pather = OldPather(self._screen, self._template_finder)
        self._pather = Pather(screen, self._api)
        self._pickit = PickIt(self._screen, self._item_finder, self._ui_manager, self._belt_manager, self._api)
        self._obs_recorder = ObsRecorder(self._config)
        # Memory reading stuff


        # Create Character
        if self._config.char["type"] in ["sorceress", "light_sorc"]:
            self._char: IChar = LightSorc(self._config.light_sorc, self._screen, self._template_finder, self._ui_manager, self._api, self._obs_recorder, self._old_pather, self._pather)
        elif self._config.char["type"] == "blizz_sorc":
            self._char: IChar = BlizzSorc(self._config.blizz_sorc, self._screen, self._template_finder, self._ui_manager, self._api, self._obs_recorder, self._old_pather, self._pather)
        elif self._config.char["type"] == "nova_sorc":
            self._char: IChar = NovaSorc(self._config.nova_sorc, self._screen, self._template_finder, self._ui_manager, self._api, self._obs_recorder, self._old_pather, self._pather)
        elif self._config.char["type"] == "hammerdin":
            self._char: IChar = Hammerdin(self._config.hammerdin, self._screen, self._template_finder, self._ui_manager, self._api, self._obs_recorder, self._old_pather, self._pather)
        elif self._config.char["type"] == "trapsin":
            self._char: IChar = Trapsin(self._config.trapsin, self._screen, self._template_finder, self._ui_manager, self._api, self._obs_recorder, self._old_pather, self._pather)
        elif self._config.char["type"] == "singer_barb":
            self._char: IChar = SingerBarb(self._config.singer_barb, self._screen, self._template_finder, self._ui_manager, self._api, self._obs_recorder, self._old_pather, self._pather)
        elif self._config.char["type"] == "zerker_barb":
            self._char: IChar = ZerkerBarb(self._config.zerker_barb, self._screen, self._template_finder, self._ui_manager, self._api, self._obs_recorder, self._old_pather, self._pather)
        elif self._config.char["type"] == "necro":
            self._char: IChar = Necro(self._config.necro, self._screen, self._template_finder, self._ui_manager, self._api, self._obs_recorder, self._old_pather, self._pather)
        elif self._config.char["type"] == "basic":
            self._char: IChar = Basic(self._config.basic, self._screen, self._template_finder, self._ui_manager, self._api, self._obs_recorder, self._old_pather, self._pather)
        elif self._config.char["type"] == "basic_ranged":
            self._char: IChar = Basic_Ranged(self._config.basic_ranged, self._screen, self._template_finder, self._ui_manager, self._api, self._obs_recorder, self._old_pather, self._pather)
        else:
            Logger.error(f'{self._config.char["type"]} is not supported! Closing down bot.')
            os._exit(1)

        # Create Town Manager
        npc_manager = NpcManager(screen, self._template_finder)
        a5 = A5(self._screen, self._template_finder, self._old_pather, self._char, npc_manager, self._pather, self._api)
        a4 = A4(self._screen, self._template_finder, self._old_pather, self._char, npc_manager, self._pather, self._api)
        a3 = A3(self._screen, self._template_finder, self._old_pather, self._char, npc_manager, self._pather, self._api)
        a2 = A2(self._screen, self._template_finder, self._old_pather, self._char, npc_manager, self._pather, self._api)
        a1 = A1(self._screen, self._template_finder, self._old_pather, self._char, npc_manager, self._pather, self._api)
        self._town_manager = TownManager(self._template_finder, self._ui_manager, self._item_finder, self._api, a1, a2, a3, a4, a5)
        self._route_config = self._config.routes
        self._route_order = self._config.routes_order
        self._npc_manager = npc_manager

        # Create runs
        if self._route_config["run_shenk"] and not self._route_config["run_eldritch"]:
            Logger.error("Running shenk without eldtritch is not supported. Either run none or both")
            os._exit(1)
        self._do_runs = {
            "run_travincal": self._route_config["run_travincal"],
            "run_pindleskin": self._route_config["run_pindleskin"],
            "run_shenk": self._route_config["run_shenk"] or self._route_config["run_eldritch"],
            "run_nihlathak": self._route_config["run_nihlathak"],
            "run_summoner": self._route_config["run_summoner"],
            "run_diablo": self._route_config["run_diablo"],
            "run_baal": self._route_config["run_baal"],
            "run_mephisto": self._route_config["run_mephisto"],
            "run_andariel": self._route_config["run_andariel"],
            "run_countess": self._route_config["run_countess"],
            "run_pit": self._route_config["run_pit"],
            "run_stony_tomb": self._route_config["run_stony_tomb"]
        }
        # Adapt order to the config
        self._do_runs = OrderedDict((k, self._do_runs[k]) for k in self._route_order if k in self._do_runs and self._do_runs[k])
        self._do_runs_reset = copy(self._do_runs)
        Logger.info(f"Doing runs: {self._do_runs_reset.keys()}")
        if self._config.general["randomize_runs"]:
            self.shuffle_runs()
        self._pindleskin = Pindleskin(self._template_finder, self._old_pather, self._town_manager, self._ui_manager, self._char, self._pickit, self._api, self._pather, self._obs_recorder)
        self._shenk = ShenkEldritch(self._template_finder, self._old_pather, self._town_manager, self._ui_manager, self._char, self._pickit, self._api, self._pather, self._obs_recorder)       
        self._nihlathak = Nihlathak(self._screen, self._template_finder, self._old_pather, self._town_manager, self._ui_manager, self._char, self._pickit, self._api, self._pather, self._obs_recorder)
        self._summoner = Summoner(self._screen, self._template_finder, self._old_pather, self._town_manager, self._ui_manager, self._char, self._pickit, self._api, self._pather, self._obs_recorder)
        # mem-reading
        self._travincal = Travincal(self._template_finder, self._old_pather, self._town_manager, self._ui_manager, self._char, self._pickit, self._api, self._pather, self._obs_recorder)
        self._baal = Baal(self._screen, self._old_pather, self._town_manager, self._ui_manager, self._char, self._pickit, self._api, self._pather, self._obs_recorder)
        self._mephisto = Mephisto(self._screen, self._old_pather, self._town_manager, self._ui_manager, self._char, self._pickit, self._api, self._pather, self._obs_recorder)
        #INCLUDED TEMPLATE FOR NOWA, runs with light sorc now
        self._andariel = Andariel(self._screen, self._old_pather, self._town_manager, self._ui_manager, self._char, self._pickit, self._api, self._pather, self._obs_recorder)
        self._countess = Countess(self._screen, self._old_pather, self._town_manager, self._ui_manager, self._char, self._pickit, self._api, self._pather, self._obs_recorder)
        self._diablo = Diablo(self._screen, self._template_finder, self._old_pather, self._town_manager, self._ui_manager, self._char, self._pickit, self._api, self._pather, self._obs_recorder)
        self._pit = Pit(self._screen, self._template_finder, self._old_pather, self._town_manager, self._ui_manager, self._char, self._pickit, self._api, self._pather, self._obs_recorder)
        self._stony_tomb = StonyTomb(self._screen, self._template_finder, self._old_pather, self._town_manager, self._ui_manager, self._char, self._pickit, self._api, self._pather, self._obs_recorder)
        
        # Create member variables
        self._pick_corpse = pick_corpse
        self._picked_up_items = False
        self._curr_loc: Union[bool, Location] = None
        self._tps_left = 10 # assume half full tp book
        self._pre_buffed = False
        self._stopping = False
        self._pausing = False
        self._current_threads = []
        self._no_stash_counter = 0
        self._ran_no_pickup = False
        self._char_selector = CharSelector(self._screen, self._template_finder)

        # Create State Machine
        self._states=['initialization', 'hero_selection', 'town', 'pindleskin', 'shenk', 'travincal', 'nihlathak', 'summoner', 'diablo', 'baal', 'mephisto', 'andariel','countess', 'pit', 'stony_tomb']
        self._transitions = [
            { 'trigger': 'init', 'source': 'initialization', 'dest': '=','before': "on_init"},
            { 'trigger': 'select_character', 'source': 'initialization', 'dest': 'hero_selection', 'before': "on_select_character"},
            { 'trigger': 'start_from_town', 'source': ['initialization', 'hero_selection'], 'dest': 'town', 'before': "on_start_from_town"},
            { 'trigger': 'create_game', 'source': 'hero_selection', 'dest': '=', 'before': "on_create_game"},
            # Tasks within town
            { 'trigger': 'maintenance', 'source': 'town', 'dest': 'town', 'before': "on_maintenance"},
            # Different runs
            { 'trigger': 'run_pindleskin', 'source': 'town', 'dest': 'pindleskin', 'before': "on_run_pindleskin"},
            { 'trigger': 'run_shenk', 'source': 'town', 'dest': 'shenk', 'before': "on_run_shenk"},
            { 'trigger': 'run_travincal', 'source': 'town', 'dest': 'travincal', 'before': "on_run_travincal"},
            { 'trigger': 'run_nihlathak', 'source': 'town', 'dest': 'nihlathak', 'before': "on_run_nihlathak"},
            { 'trigger': 'run_summoner', 'source': 'town', 'dest': 'summoner', 'before': "on_run_summoner"},
            { 'trigger': 'run_baal', 'source': 'town', 'dest': 'baal', 'before': "on_run_baal"},
            { 'trigger': 'run_mephisto', 'source': 'town', 'dest': 'mephisto', 'before': "on_run_mephisto"},
            { 'trigger': 'run_andariel', 'source': 'town', 'dest': 'andariel', 'before': "on_run_andariel"},
            { 'trigger': 'run_diablo', 'source': 'town', 'dest': 'nihlathak', 'before': "on_run_diablo"},
            { 'trigger': 'run_countess', 'source': 'town', 'dest': 'countess', 'before': "on_run_countess"},
            { 'trigger': 'run_pit', 'source': 'town', 'dest': 'pit', 'before': "on_run_pit"},
            { 'trigger': 'run_stony_tomb', 'source': 'town', 'dest': 'stony_tomb', 'before': "on_run_stony_tomb"},
            # End run / game
            { 'trigger': 'end_run', 'source': ['shenk', 'pindleskin', 'nihlathak', 'travincal', 'summoner', 'diablo', 'baal', 'mephisto', 'andariel','countess', 'pit', 'stony_tomb'], 'dest': 'town', 'before': "on_end_run"},
            { 'trigger': 'end_game', 'source': ['town', 'shenk', 'pindleskin', 'nihlathak', 'travincal', 'summoner', 'diablo', 'baal', 'mephisto', 'andariel','countess', 'pit', 'stony_tomb', 'end_run'], 'dest': 'initialization', 'before': "on_end_game"},

        ]
        self.machine = Machine(model=self, states=self._states, initial="initialization", transitions=self._transitions, queued=True)
        self._transmute = Transmute(self._screen, self._template_finder, self._game_stats, self._ui_manager)
    
    # def draw_graph(self):
    #     # Draw the whole graph, graphviz binaries must be installed and added to path for this!
    #     from transitions.extensions import GraphMachine
    #     self.machine = GraphMachine(model=self, states=self._states, initial="initialization", transitions=self._transitions, queued=True)
    #     self.machine.get_graph().draw('my_state_diagram.png', prog='dot')
        
    def get_belt_manager(self) -> BeltManager:
        return self._belt_manager

    def get_curr_location(self):
        return self._curr_loc

    def start(self):
        self._obs_recorder.start_replaybuffer_if_enabled()
        self.trigger_or_stop('init')

    def stop(self):
        self._stopping = True

    def toggle_pause(self):
        self._pausing = not self._pausing
        if self._pausing:
            Logger.info(f"Pause at next state change...")
        else:
            Logger.info(f"Resume")
            self._game_stats.resume_timer()

    def trigger_or_stop(self, name: str, **kwargs):
        if self._pausing:
            Logger.info(f"{self._config.general['name']} is now pausing")
            self._game_stats.pause_timer()
        while self._pausing:
            time.sleep(0.2)
        if not self._stopping:
            self.trigger(name, **kwargs)

    def current_game_length(self):
        return self._game_stats.get_current_game_length()

    def shuffle_runs(self):
        tmp = list(self._do_runs.items())
        random.shuffle(tmp)
        self._do_runs = OrderedDict(tmp)

    def is_last_run(self):
        found_unfinished_run = False
        for key in self._do_runs:
            if self._do_runs[key]:
                found_unfinished_run = True
                break
        return not found_unfinished_run

    def _rebuild_as_asset_to_trigger(trigger_to_assets: dict):
        result = {}
        for key in trigger_to_assets.keys():
            for asset in trigger_to_assets[key]:
                result[asset] = key
        return result

    def on_init(self):
        self._game_stats.log_start_game()
        keyboard.release(self._config.char["stand_still"])
        transition_to_screens = Bot._rebuild_as_asset_to_trigger({
            "select_character": Bot._MAIN_MENU_MARKERS,
            "start_from_town": town_manager.TOWN_MARKERS,
        })
        match = self._template_finder.search_and_wait(list(transition_to_screens.keys()), best_match=True)
        self.trigger_or_stop(transition_to_screens[match.name])

    def on_select_character(self):
        if self._config.general['restart_d2r_when_stuck']:
            # Make sure the correct char is selected
            if self._char_selector.has_char_template_saved():
                self._char_selector.select_char()
            else:
                self._char_selector.save_char_online_status()
                self._char_selector.save_char_template()

        self.trigger_or_stop("create_game")

    def on_create_game(self):
        if self._config.general["games_via_lobby"]:
            found_btn_play = self._template_finder.search_and_wait("CREATE_GAME", time_out= 3, threshold=0.8, best_match=True, normalize_monitor=True)
            if found_btn_play.valid:
                self._ui_manager.create_game_lobby()
                self.trigger_or_stop("start_from_town")
            else:
                found_btn_lobby = self._template_finder.search_and_wait("LOBBY", threshold=0.8, best_match=True, normalize_monitor=True)
                if found_btn_lobby.valid:
                    if not self._ui_manager.goto_lobby(): return
                    found_btn_play = self._template_finder.search_and_wait("CREATE_GAME", time_out= 3, threshold=0.8, best_match=True, normalize_monitor=True)
                    if found_btn_play.valid:
                        self._ui_manager.create_game_lobby()
                        self.trigger_or_stop("start_from_town")
        else:
            # Start a game from hero selection
            self._template_finder.search_and_wait(Bot._MAIN_MENU_MARKERS, roi=self._config.ui_roi["main_menu_top_left"])
            if not self._ui_manager.start_game(): return
            self.trigger_or_stop("start_from_town")

    def handle_item_on_cursor(self):
        Logger.debug(f"Game started with an item on the cursor. Dropping it and running pickit...")
        mouse.move(*self._screen.convert_screen_to_monitor((600, 360)))
        wait(0.1, 0.15)
        mouse.click(button="left")
        self._char.discover_capabilities(force=False)
        self._pickit.pick_up_items(self._char)
        wait(0.1, 0.2)

    def on_start_from_town(self):
        self._curr_loc = self._town_manager.wait_for_town_spawn()
        self.trigger_or_stop("maintenance")

    def on_maintenance(self):
        Logger.debug("Town maintenance...")
        is_loading = True
        merc_alive = False
        health_pct = 1
        mana_pct = 1
        data = self._api.get_data()
        if data is not None:
            if self._api.player_summary is not None:
                self._config.general["player_summary"] = self._api.player_summary
                self._config.general["player_name"] = self._api.player_name
            if data["item_on_cursor"]:
                is_loading = self._ui_manager.wait_for_loading_finish()
                self.handle_item_on_cursor()
                data = self._api.get_data()
            self._pick_corpse = "player_corpse" in data and data["player_corpse"] is not None and type(data["player_corpse"]) is dict
            merc_alive = "merc_alive" in data and data["merc_alive"]
            Logger.info(f"Detected that merc is {'alive' if merc_alive else 'dead'} from memory")
            health_pct = data["player_health_pct"]
            mana_pct = data["player_mana_pct"]
            Logger.debug(f"Maintenance: Loaded player HP/MP from memory, HP: {round(health_pct * 100, 1)}%, MP: {round(mana_pct * 100, 1)}%")

        # Figure out how many pots need to be picked up
        self._belt_manager.update_pot_needs()
        buy_pots = self._belt_manager.should_buy_pots()
        should_heal = health_pct < 0.7 or mana_pct < 0.2
        should_res_merc = not merc_alive and self._config.char["use_merc"]

        # Handle picking up corpse in case of death
        if self._pick_corpse:
            Logger.debug(f"Maintenance: Picking up corpse")
            is_loading = self._ui_manager.wait_for_loading_finish()
            self._char.discover_capabilities(force=False)
            self._pick_corpse = False
            time.sleep(1.6)
            DeathManager.pick_up_corpse(self._screen)
            wait(1.2, 1.5)
            self._belt_manager.fill_up_belt_from_inventory(self._config.char["num_loot_columns"])
            wait(0.5)
            if self._char.capabilities.can_teleport_with_charges and not self._char.select_tp():
                keybind = self._char._skill_hotkeys["teleport"]
                Logger.info(f"Maintenance: Teleport keybind is lost upon death. Rebinding teleport to '{keybind}'")
                self._char.remap_right_skill_hotkey("TELE_ACTIVE", self._char._skill_hotkeys["teleport"])
        else:
            dest = None
            dest_loc = self._curr_loc
            pre_walk_time = 4.5
            if "a1_" in self._curr_loc:
                dest = "Akara" if buy_pots or should_heal else "Rogue Encampment"
                dest_loc = Location.A1_AKARA if buy_pots or should_heal else Location.A1_WP_NORTH
                if self._picked_up_items or should_res_merc:
                    dest = None
                pre_walk_time = 1.5
            elif "a2_" in self._curr_loc:
                dest = "Lysander" if buy_pots or should_heal else "Lut Gholein"
                dest_loc = Location.A2_FARA_STASH if buy_pots or should_heal else Location.A2_WP
                pre_walk_time = 6
            elif "a3_" in self._curr_loc:
                dest = "Ormus" if buy_pots or should_heal else "Kurast Docks"
                dest_loc = Location.A3_ORMUS if buy_pots or should_heal else Location.A3_STASH_WP
                if dest == "Ormus":
                    pre_walk_time = 3
            elif "a4_" in self._curr_loc:
                dest = "Jamella" if buy_pots or should_heal else "The Pandemonium Fortress"
                dest_loc = Location.A4_JAMELLA if buy_pots or should_heal else Location.A4_WP
                if self._picked_up_items or should_res_merc:
                    dest = None
            elif "a5_" in self._curr_loc:
                dest = "Malah" if buy_pots or should_heal else "Harrogath"
                dest_loc = Location.A5_MALAH if buy_pots or should_heal else Location.A5_STASH

            if dest is not None:
                Logger.info(f"Maintenance: Heading toward {dest}, buy pots: {buy_pots}, need to heal: {should_heal}")
                if dest == "Akara":
                    self._pather.traverse_walking("Akara", self._char, obj=False, threshold=10, static_npc=True)
                else:
                    self._pather.traverse_walking(dest, self._char, obj=False, threshold=16, time_out=pre_walk_time, end_dist=10)
                self._curr_loc = dest_loc

        if should_heal or buy_pots:
            if buy_pots:
                if is_loading: is_loading = self._ui_manager.wait_for_loading_finish()
                Logger.info("Maintenance: Buy pots at next possible Vendor")
                self._belt_manager.update_pot_needs()
                pot_needs = self._belt_manager.get_pot_needs()
                Logger.debug(f"Potion needs: {pot_needs}")
                self._curr_loc = self._town_manager.buy_pots(self._curr_loc, pot_needs["health"], pot_needs["mana"])
                wait(0.5)
                self._belt_manager.update_pot_needs()
            else:
                Logger.info("Maintenance: Healing at next possible Vendor")
                if is_loading: is_loading = self._ui_manager.wait_for_loading_finish()
                self._curr_loc = self._town_manager.heal(self._curr_loc)
            
            if not self._curr_loc:
                return self.trigger_or_stop("end_game", failed=True)

        # Check if we should force stash (e.g. when picking up items by accident or after failed runs or chicken/death)
        force_stash = False
        self._no_stash_counter += 1
        if not self._picked_up_items and (self._no_stash_counter > 4 or self._pick_corpse):
            self._no_stash_counter = 0
            if is_loading: is_loading = self._ui_manager.wait_for_loading_finish()
            force_stash = self._ui_manager.should_stash(self._config.char["num_loot_columns"])
        # Stash stuff, either when item was picked up or after X runs without stashing because of unwanted loot in inventory
        if self._picked_up_items or force_stash:
            # Check config/gold and see if we need to enable/disable gold pickup
            if self._config.char["id_items"]:
                Logger.info("Maintenance: Identifying items")
                if is_loading: is_loading = self._ui_manager.wait_for_loading_finish()
                self._curr_loc = self._town_manager.identify(self._curr_loc)
                if not self._curr_loc:
                    if is_loading: is_loading = self._ui_manager.wait_for_loading_finish()
                    return self.trigger_or_stop("end_game", failed=True)
            Logger.info(f"Maintenance: Stashing items, current location: {self._curr_loc}")
            if is_loading: is_loading = self._ui_manager.wait_for_loading_finish()
            self._curr_loc = self._town_manager.stash(self._curr_loc)
            self._check_gold_pickup()
            Logger.info("Maintenance: Running transmutes")
            self._transmute.run_transmutes(force=False)
            keyboard.send("esc")
            if not self._curr_loc:
                return self.trigger_or_stop("end_game", failed=True)
            self._no_stash_counter = 0
            self._picked_up_items = False
            wait(1.0)

        if is_loading: is_loading = self._ui_manager.wait_for_loading_finish()
        self._char.discover_capabilities(force=False)

        # Check if we are out of tps or need repairing
        need_repair = self._ui_manager.repair_needed()
        need_routine_repair = False
        if type(self._config.char["runs_per_repair"]) == int and self._config.char["runs_per_repair"] > 0:
            need_routine_repair = self._game_stats._run_counter % self._config.char["runs_per_repair"] == 0
        need_refill_teleport = not self._char.capabilities.can_teleport_natively and self._char.capabilities.can_teleport_with_charges and (not self._char.select_tp() or self._char.is_low_on_teleport_charges())
        if self._tps_left < random.randint(3, 5) or need_repair or need_routine_repair or need_refill_teleport:
            if need_repair: Logger.info("Maintenance: Repair needed. Gear is about to break")
            elif need_routine_repair: Logger.info(f"Maintenance: Routine repair. Run count={self._game_stats._run_counter}, runs_per_repair={self._config.char['runs_per_repair']}")
            elif need_refill_teleport: Logger.info("Maintenance: Teleport charges ran out. Need to repair")
            else: Logger.info("Maintenance: Repairing and buying TPs at next Vendor")
            self._curr_loc = self._town_manager.repair_and_fill_tps(self._curr_loc)
            if not self._curr_loc:
                return self.trigger_or_stop("end_game", failed=True)
            self._tps_left = 20
            wait(1.0)

        # Check if merc needs to be revived
        if should_res_merc:
            Logger.info(f"Detected that merc is dead in memory, confirming via pixels...")
            if is_loading: is_loading = self._ui_manager.wait_for_loading_finish()
            merc_alive = self._template_finder.search(["MERC_A2", "MERC_A1", "MERC_A5", "MERC_A3"], self._screen.grab(), threshold=0.9, roi=self._config.ui_roi["merc_icon"]).valid
            should_res_merc = not merc_alive and self._config.char["use_merc"]
            Logger.info(f"Confirmed via pixels that merc is {'alive' if merc_alive else 'dead'}")
        if should_res_merc:
            Logger.info("Maintenance: Resurrect merc")
            self._game_stats.log_merc_death()
            self._curr_loc = self._town_manager.resurrect(self._curr_loc)
            if not self._curr_loc:
                return self.trigger_or_stop("end_game", failed=True)

        # Check if gambling is needed
        if self._ui_manager.gambling_needed() and self._config.char["gamble_items"]:
            Logger.info("Maintenance: Gambling")
            for x in range(4):
                self._curr_loc = self._town_manager.gamble(self._curr_loc)
                self._ui_manager.gamble(self._item_finder)
                if (x ==3):
                    self._curr_loc = self._town_manager.stash(self._curr_loc)
                else:
                    self._curr_loc = self._town_manager.stash(self._curr_loc, gamble=True)
            self._ui_manager.set__gold_full(False)
        
        # Run /nopickup command to avoid picking up stuff on accident
        if not self._ran_no_pickup and not self._game_stats._nopickup_active:
            self._ran_no_pickup = True
            if self._ui_manager.enable_no_pickup():
                self._game_stats._nopickup_active = True
                Logger.info("Activated /nopickup")
            else:
                Logger.error("Failed to detect if /nopickup command was applied or not")

        if self._game_stats._run_counter == 0 or self._game_stats._consecutive_runs_failed > 0 or self._game_stats._game_counter == 0 or self._pick_corpse or self._game_stats._did_chicken_last_run:
            Logger.info("Verifying weapon slot 1 is active due to chicken/failed/first run")
            self._char.verify_active_weapon_tab()
        self._game_stats._did_chicken_last_run = False

        # Start a new run
        Logger.info("Town maintenance complete, starting runs")
        started_run = False
        for key in self._do_runs:
            if self._do_runs[key]:
                self.trigger_or_stop(key)
                started_run = True
                break
        if not started_run:
            self.trigger_or_stop("end_game")
    
    def _check_gold_pickup(self):
        stop_above = self._config.char["stop_gold_pickup_above"]
        start_below = self._config.char["start_gold_pickup_below"]
        if stop_above > 0 or start_below > 0:
            gold = self._char.get_player_gold()
            Logger.debug("Player gold: " + str(gold))
            if gold > -1:
                if stop_above > 0 and gold > stop_above:
                    Logger.debug(f"Reached gold threshold of {stop_above}, turning off gold pickup")
                    self._config.turn_off_goldpickup()
                elif start_below > 0 and gold < start_below:
                    Logger.debug(f"Fell below gold threshold of {start_below}, turning on gold pickup")
                    self._config.turn_on_goldpickup()
            else:
                Logger.eror("Failed to detect player gold")

    def on_end_game(self, failed: bool = False):
        if self._config.general["info_screenshots"] and failed:
            cv2.imwrite("./info_screenshots/info_failed_game_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())
        self._curr_loc = False
        self._pre_buffed = False
        self._ui_manager.save_and_exit()
        self._game_stats.log_end_game(failed=failed)

        if self._config.general["max_runtime_before_break_m"] and self._config.general["break_length_m"]:
            elapsed_time = time.time() - self._game_stats._start_time
            Logger.info(f'Session length = {elapsed_time:.2f}s, max_runtime_before_break_m = {self._config.general["max_runtime_before_break_m"]*60:.2f}s.')

            if elapsed_time > (self._config.general["max_runtime_before_break_m"]*60):
                Logger.info(f'Max session length reached, taking a break for {self._config.general["break_length_m"]} minutes.')
                self._messenger.send_message(f'Ran for {hms(elapsed_time)}, taking a break for {self._config.general["break_length_m"]} minutes.')
                if not self._pausing:
                    self.toggle_pause()

                wait(self._config.general["break_length_m"]*60)

                break_msg = f'Break over, now running for {self._config.general["max_runtime_before_break_m"]} more minutes.'
                Logger.info(break_msg)
                self._messenger.send_message(break_msg)
                if self._pausing:
                    self.toggle_pause()
                    self._game_stats._start_time = time.time()
        self._do_runs = copy(self._do_runs_reset)
        if self._config.general["randomize_runs"]:
            self.shuffle_runs()
        wait(0.2, 0.5)
        if failed:
            self._obs_recorder.save_replay_if_enabled()
        self.trigger_or_stop("init")

    def on_end_run(self):
        if not self._config.char["pre_buff_every_run"]:
            self._pre_buffed = True
        success = self._char.tp_town()
        if success:
            self._tps_left -= 1
            self._curr_loc = self._town_manager.wait_for_tp(self._curr_loc)
            if self._curr_loc:
                return self.trigger_or_stop("maintenance")
        if not self._ui_manager.has_tps():
            self._tps_left = 0
        self.trigger_or_stop("end_game", failed=True)

    # ========================== All the runs go here =========================
    def _ending_run_helper(self, res: Union[bool, tuple[Location, bool]]):
        self._game_stats._run_counter += 1
        # either fill member variables with result data or mark run as failed
        failed_run = True
        if res:
            failed_run = False
            self._curr_loc, self._picked_up_items = res
        # in case its the last run or the run was failed, end game, otherwise move to next run
        if self.is_last_run() or failed_run:
            if failed_run:
                self._no_stash_counter = 10 # this will force a check if we should stash on next game
            self.trigger_or_stop("end_game", failed=failed_run)
        else:
            self.trigger_or_stop("end_run")

    def on_run_pindleskin(self):
        res = False
        self._do_runs["run_pindleskin"] = False
        self._game_stats.update_location("Pin" if self._config.general['discord_status_condensed'] else "Pindle")
        self._curr_loc = self._pindleskin.approach(self._curr_loc)
        if self._curr_loc:
            res = self._pindleskin.battle(not self._pre_buffed)
        self._ending_run_helper(res)

    def on_run_shenk(self):
        res = False
        self._do_runs["run_shenk"] = False
        self._curr_loc = self._shenk.approach(self._curr_loc)
        if self._curr_loc:
            res = self._shenk.battle(self._route_config["run_shenk"], not self._pre_buffed, self._game_stats)
        self._ending_run_helper(res)

    def on_run_travincal(self):
        res = False
        self._do_runs["run_travincal"] = False
        self._game_stats.update_location("Trav" if self._config.general['discord_status_condensed'] else "Travincal")
        self._curr_loc = self._travincal.approach(self._curr_loc)
        if self._curr_loc:
            res = self._travincal.battle(not self._pre_buffed)
        self._ending_run_helper(res)

    def on_run_nihlathak(self):
        res = False
        self._do_runs["run_nihlathak"] = False
        self._game_stats.update_location("Nihl" if self._config.general['discord_status_condensed'] else "Nihlathak")
        self._curr_loc = self._nihlathak.approach(self._curr_loc)
        if self._curr_loc:
            res = self._nihlathak.battle(not self._pre_buffed)
        self._ending_run_helper(res)

    def on_run_summoner(self):
        res = False
        self._do_runs["run_summoner"] = False
        self._game_stats.update_location("Summ" if self._config.general['discord_status_condensed'] else "Summoner")
        self._curr_loc = self._summoner.approach(self._curr_loc)
        if self._curr_loc:
            res = self._summoner.battle(not self._pre_buffed)
        self._tps_left -= self._summoner.used_tps
        self._ending_run_helper(res)

    def on_run_diablo(self):
        res = False
        self._do_runs["run_diablo"] = False
        self._game_stats.update_location("Dia" if self._config.general['discord_status_condensed'] else "Diablo")
        self._curr_loc = self._diablo.approach(self._curr_loc)
        if self._curr_loc:
            res = self._diablo.battle(not self._pre_buffed)
        self._tps_left -= 1 # we use one tp at pentagram for calibration
        self._ending_run_helper(res)
    
    def on_run_baal(self):
        res = False
        self._do_runs["run_baal"] = False
        self._game_stats.update_location("Baal")
        self._curr_loc = self._baal.approach(self._curr_loc)
        if self._curr_loc:
            res = self._baal.battle(not self._pre_buffed)
        self._ending_run_helper(res)

    def on_run_mephisto(self):
        res = False
        self._do_runs["run_mephisto"] = False
        self._game_stats.update_location("Meph")
        self._curr_loc = self._mephisto.approach(self._curr_loc)
        if self._curr_loc:
            res = self._mephisto.battle(not self._pre_buffed)
        self._ending_run_helper(res)

    def on_run_andariel(self):
        res = False
        self._do_runs["run_andariel"] = False
        self._game_stats.update_location("Andy")
        self._curr_loc = self._andariel.approach(self._curr_loc)
        if self._curr_loc:
            res = self._andariel.battle(not self._pre_buffed)
        self._ending_run_helper(res)

    def on_run_countess(self):
        res = False
        self._do_runs["run_countess"] = False
        self._game_stats.update_location("Tower")
        self._curr_loc = self._countess.approach(self._curr_loc)
        if self._curr_loc:
            res = self._countess.battle(not self._pre_buffed)
        self._ending_run_helper(res)

    def on_run_pit(self):
        res = False
        self._do_runs["run_pit"] = False
        self._game_stats.update_location("pit")
        self._curr_loc = self._pit.approach(self._curr_loc)
        if self._curr_loc:
            res = self._pit.battle(not self._pre_buffed)
        self._ending_run_helper(res)
        
    def on_run_stony_tomb(self):
        res = False
        self._do_runs["run_stony_tomb"] = False
        self._game_stats.update_location("stony_tomb")
        self._curr_loc = self._stony_tomb.approach(self._curr_loc)
        if self._curr_loc:
            res = self._stony_tomb.battle(not self._pre_buffed)
        self._ending_run_helper(res)
