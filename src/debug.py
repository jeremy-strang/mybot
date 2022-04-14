import json
import math
import time
import traceback
from tracemalloc import stop
from turtle import pos
from char.hammerdin import Hammerdin
from char.skill import Skill
import game_controller
from pickit.pixel_pickit import PixelPickit
from pickit.pickit import Pickit
import keyboard
import os
import sys
import pickle
from monsters.monster_rule import MonsterRule
from npc_manager import Npc
from obs import obs_recorder
from pathing.path_finder import make_path_bfs, PathFinder
from run.baal import Baal
from run.diablo import Diablo
from run.mephisto import Mephisto
from run.nihlathak import Nihlathak
from run.pindleskin import Pindleskin
from run.shenk_eldritch import ShenkEldritch
from run.stony_tomb import StonyTomb
from run.summoner import Summoner
from run.andariel import Andariel
from run.pit import Pit
from run.travincal import Travincal
from run.countess import Countess

from screen import Screen
from bot import Bot
from config import Config
from game_stats import GameStats
from pathing import Location, OldPather
from pathing import Pather
from d2r import D2rApi
import threading
from state_monitor import StateMonitor
from template_finder import TemplateFinder
from town import TownManager, town_manager
from ui import UiManager, BeltManager
from pickit import ItemFinder
from game_stats import GameStats
from char.barbarian.zerker_barb import ZerkerBarb

import threading
from overlay import Overlay
from main import on_exit
from utils.custom_mouse import mouse
from utils.misc import wait
from obs import ObsRecorder
from monsters import sort_and_filter_monsters

import pprint
pp = pprint.PrettyPrinter(depth=6)

class Debug:
    def __init__(self):
        self._game_controller = None
        self._config = Config()
        self._screen = Screen()
        self._game_stats = GameStats()
        self._obs_recorder = ObsRecorder(self._config)
        self._overlay = None
        self._overlay_thread = None

        self._api = D2rApi(self._config.custom_files)
        self._api_thread = threading.Thread(target=self._api.start)
        self._api_thread.daemon = False
        self._api_thread.start()

        self._game_stats = GameStats() 
        self._template_finder = TemplateFinder(self._screen)
        self._old_pather = OldPather(self._screen, self._template_finder)
        self._pather = Pather(self._screen, self._api)
        self._item_finder = ItemFinder(self._config)
        self._bot = Bot(self._screen, self._game_stats, self._template_finder, self._api, self._obs_recorder)
        self._ui_manager = UiManager(self._screen, self._template_finder, self._obs_recorder, self._api, self._game_stats)
        self._belt_manager = BeltManager(self._screen, self._template_finder, self._api)
        self._town_manager = self._bot._town_manager
        self._a1 = self._town_manager.a1
        self._a2 = self._town_manager.a2
        self._a3 = self._town_manager.a3
        self._a4 = self._town_manager.a4

        self._char = Hammerdin(self._config.hammerdin, self._screen, self._template_finder, self._ui_manager, self._api, self._obs_recorder, self._old_pather, self._pather)
        self._pixel_pickit = PixelPickit(self._screen, self._item_finder, self._ui_manager, self._belt_manager, self._api, self._char, self._pather, self._game_stats)
        self._pickit = Pickit(self._screen, self._ui_manager, self._belt_manager, self._char, self._pather, self._api, self._game_stats)
        #self._char = ZerkerBarb(self._config.zerker_barb, self._screen, self._template_finder, self._ui_manager, self._api, self._obs_recorder, self._old_pather, self._pather)
        self._char.discover_capabilities()
        self._pindleskin = self._bot._pindleskin # Pindleskin(screen, old_pather, town_manager, ui_manager, char, pickit, api, pather, obs_recorder)
        self._shenk = self._bot._shenk # ShenkEldritch(screen, old_pather, town_manager, ui_manager, char, pickit, api, pather, obs_recorder)
        self._nihlathak = self._bot._nihlathak # Nihlathak(screen, old_pather, town_manager, ui_manager, char, pickit, api, pather, obs_recorder)
        self._summoner = self._bot._summoner # Summoner(screen, old_pather, town_manager, ui_manager, char, pickit, api, pather, obs_recorder)
        self._travincal = self._bot._travincal # Travincal(screen, old_pather, town_manager, ui_manager, char, pickit, api, pather, obs_recorder)
        self._baal = self._bot._baal # Baal(screen, old_pather, town_manager, ui_manager, char, pickit, api, pather, obs_recorder)
        self._mephisto = self._bot._mephisto # Mephisto(screen, old_pather, town_manager, ui_manager, char, pickit, api, pather, obs_recorder)
        self._andariel = self._bot._andariel # Andariel(screen, old_pather, town_manager, ui_manager, char, pickit, api, pather, obs_recorder)
        self._countess = self._bot._countess # Countess(screen, old_pather, town_manager, ui_manager, char, pickit, api, pather, obs_recorder)
        self._diablo = self._bot._diablo # Diablo(screen, old_pather, town_manager, ui_manager, char, pickit, api, pather, obs_recorder)
        self._pit = self._bot._pit # Pit(screen, old_pather, town_manager, ui_manager, char, pickit, api, pather, obs_recorder)
        self._stony_tomb = self._bot._stony_tomb # StonyTomb(screen, old_pather, town_manager, ui_manager, char, pickit, api, pather, obs_recorder)

    def stop(self):
        self._ui_manager.abort = True
        if self._overlay is not None: self._overlay.stop_overlay()
        on_exit(self._game_controller, ["capslock", "space"])

    def start_overlay(self):
        print("Overlay thread starting...")
        self._overlay = Overlay(self._bot, self._game_stats)
        self._overlay_thread = threading.Thread(target=self._overlay.init)
        self._overlay_thread.daemon = True
        self._overlay_thread.start()
        return self._overlay
    
    def load_pickle(self, file_path: str):
        data = None
        try:
            with open(file_path,"rb") as f:
                data = pickle.load(f)
        except BaseException as e:
            print(f"Error loading pickle file {file_path}:\n{e}")
            traceback.print_exc()
        return data
    
    def start_api(self):
        data = None
        print(("-" * 80) + "\n\nStarting API...")
        while data is None:
            wait(0.2)
            data = self._api.get_data()
        return data

if __name__ == "__main__":
    from utils.coordinates import world_to_abs
    from utils.custom_mouse import mouse
        
    # def stop_debug(game_controller, overlay):
    #     ui_manager.abort = True
    #     if overlay is not None: overlay.stop_overlay()
    #     on_exit(game_controller, ["capslock", "space"])

    # def start_overlay(bot, game_stats):
    #     print("Overlay thread starting...")
    #     overlay = Overlay(bot, game_stats)
    #     overlay_thread = threading.Thread(target=overlay.init)
    #     overlay_thread.daemon = True
    #     overlay_thread.start()
    #     return overlay
    
    # def load_pickle(file_path: str):
    #     data = None
    #     try:
    #         with open(file_path,"rb") as f:
    #             data = pickle.load(f)
    #     except BaseException as e:
    #         print(f"Error loading pickle file {file_path}:\n{e}")
    #         traceback.print_exc()
    #     return data
    debug = None
    try:
        debug = Debug()
        debug.start_api()
        
        # overlay = debug.start_overlay()
        # pp.pprint(config.items)

        def do_stuff(debug):
            print("Doing stuff...")
            wait(.5)
            start = time.time()
            try:
                data = debug._api.get_data()

                # pather.click_object("TownPortal")
                
                debug._pickit.pick_up_items()

                
                # pickled = load_pickle("pickles/pickle_d2r_mem_Travincal_20220411_214023.p")
                # print(f"Loaded pickle data, type: {type(pickled)}")
                # print(f"    current_area:   {pickled['current_area']}")
                # print(f"    map shape:      {pickled['map'].shape}")
                # print(f"    map size:       {pickled['map'].size}")
                # for m in pickled["monsters"]:
                #     if "Unique" in m["type"]:
                #         pp.pprint(m)

                # print(f"monitor? or abs?: {mouse.get_position()}")
                # print(f"convert_monitor_to_screen?: {screen.convert_monitor_to_screen(mouse.get_position())}")
                # print(f"abs_to_screen?: {screen.convert_abs_to_screen(mouse.get_position())}")
                # shenk.battle(False, True, game_stats)
                # pindleskin.approach(Location.A5_TOWN_START)
                
                # items = api.find_items_by_name("Amethyst", "stash_items")
                # for item in items:
                #     pp.pprint(item)
                #     ui_manager._move_mouse_to_stash_pos(item["position"])
                #     wait(0.5)

                # travincal.battle(False)
                # pather.teleport_to_position((142, 103), char)

                # if not pather.go_to_area("Halls of Vaught", "HallsOfVaught", entrance_in_wall=True, randomize=2, time_out=5, offset=[7, -5]):
                #     print("F")
                # pather.click_poi("Halls of Vaught")

                # belt_manager.update_pot_needs()

                # char.tp_town()

                # bot._town_manager.a4.open_wp(Location.A4_TOWN_START)
    
                # if not data["stash_open"]:
                #     bot._town_manager.a3.open_stash(Location.A3_STASH_WP)
                debug._ui_manager.stash_all_items(debug._config.char["num_loot_columns"], debug._item_finder, False)

                # ui_manager.fill_tome_of("Town Portal")
                # ui_manager.throw_out_junk(item_finder)
                # item = pickit2._next_item()
                # pather.move_mouse_to_item(item)

                # bot._town_manager.open_stash(Location.A4_TOWN_START)
                # write_data_to_file(data, api._raw_data_str)
                
                # pot_needs = belt_manager.update_pot_needs()
                # pot_needs = belt_manager.get_pot_needs()
                # print(f"Potion needs: {pot_needs}")
                # bot._town_manager.buy_pots(Location.A3_ORMUS, pot_needs["health"], pot_needs["mana"])

                # bank = None
                # for obj in data["objects"]:w
                #     if obj["name"].startswith("Bank"):
                #         bank = obj
                #         print(f"object id: {obj['id']}, name: {obj['name']}, position: {obj['position']}")
                #         print(bank)
                
                # curr_loc = bot._town_manager.open_stash(bot.get_curr_location())
                
                # api.start_timer()
                # pather.traverse_walking("Kurast Docks", char, obj=False, threshold=16, time_out=4, end_dist=10)
                # api.get_metrics()

                # ui_manager.throw_out_junk(item_finder) 

                # # pit_lvl2 = debug._pather.get_entity_coords_from_str("Pit Level 2", "points_of_interest", False)
                # akara = debug._api.find_npc(Npc.AKARA)
                # pf = PathFinder(debug._api, 25)
                # path = pf.solve_tsp(akara["position_area"], True)
                # debug.start_overlay()
                # nodes = []
                # current = pf.player_node
                # for node in path:
                #     print(f"    distance from current ({current}) to next node ({node}): {math.dist(current, node)}")
                #     bfs_nodes = make_path_bfs(current, node, debug._api.data["map"])
                #     for n in bfs_nodes:
                #         nodes.append(n)
                #     debug._pather.traverse_walking(node, debug._char)
                #     current = node
                # debug._api._current_path = nodes

            except BaseException as e:
                print(e)
                traceback.print_exc()
            # stop_debug(game_controller, overlay)
            print("Done doing stuff")

        dump_pickles = False # debug._config.advanced_options["dump_data_to_pickle_for_debugging"]

        # keyboard.add_hotkey(config.advanced_options["resume_key"], lambda: pickit.pick_up_items(char, True))
        keyboard.add_hotkey(debug._config.advanced_options['save_d2r_data_to_file_key'], lambda: debug._api.write_data_to_file(pickle=dump_pickles))
        keyboard.add_hotkey(debug._config.advanced_options["resume_key"], lambda: do_stuff(debug)) #lambda: pit.battle(True))
        keyboard.add_hotkey(debug._config.advanced_options["exit_key"], lambda: debug.stop())
        keyboard.add_hotkey(debug._config.advanced_options["graphic_debugger_key"], lambda: debug.start_overlay())
        print("Ready!\n\n" + ("-" * 80))
        keyboard.wait()

        print("Press Enter to exit ...")
        input()
    except:
        traceback.print_exc()
    finally:
        if debug:
            debug.stop()

# python src/debug.py   
