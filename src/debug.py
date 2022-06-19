import json
import math
from re import M
import time
import traceback
from tracemalloc import stop
from turtle import pos

import psutil
from char.hammerdin import Hammerdin
from char.skill import Skill
import game_controller
from pickit.item_types import Item, Quality
from pickit.pickit_utils import get_free_inventory_space
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
from d2r import D2rApi, D2rMenu
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
from utils.misc import point_str, restore_d2r_window_visibility, wait, set_d2r_always_on_top
from obs import ObsRecorder
from monsters import sort_and_filter_monsters

import pprint
pp = pprint.PrettyPrinter(depth=6)

class Debug:
    def try_join_game(self):
        start = time.time()
        while time.time() - start < 180:
            mouse.move(*self._screen.convert_abs_to_monitor((347, 72)), delay_factor=(0.1, 0.2))
            mouse.click(button="left")
            wait(0.2)
            mouse.move(*self._screen.convert_abs_to_monitor((347, 72)), delay_factor=(0.1, 0.2))
            mouse.click(button="left")
            wait(5)

    def do_stuff(self):
        # self._a3.find_vendor_and_open_trade(Npc.ASHEARA, menu_selection="resurrect", confirm_menu=None, y_offset=-55)
        
        npc_name = Npc.ASHEARA
        menu_selection = "resurrect"
        if not self._a3.interact_with_npc(npc_name, menu_selection):
            if self._a3._npc_manager.open_npc_menu(npc_name):
                self._a3._npc_manager.press_npc_btn(npc_name, menu_selection)

        # if self._api.player_summary is not None:
        #     self._config.general["player_summary"] = self._api.player_summary
        #     self._config.general["player_name"] = self._api.player_name
        # self._config.general["player_experience"] = self._api.player_experience
        # self._config.general["player_level_progress"] = self._api.player_level_progress
        # self._config.general["player_level"] = self._api.player_level
        # self._game_stats.log_exp(self._api.player_experience)
        # self._game_stats._send_status_update()

        # self.try_join_game()
        # data = self._api.wait_for_data()
        # print(f"Player location: {point_str(self._api.data['player_pos_area'])}")
        # print(f"Map shape: {data['map'].shape}")

        # mouse.move(*self._screen.convert_abs_to_monitor((0, 0)))
        # wait(1)
        
        # x, y = mouse.get_position()
        # print(f"Mouse pos:          ({x}, {y})")
        # print(f"Mouse pos (screen): ({self._screen.convert_monitor_to_screen((x, y))})")
        # print(f"Mouse pos (abs):    ({self._screen.convert_monitor_to_abs((x, y))})")
        # self.find_coronet()

        # print(self._bot.get_tome_of("Identify"))

        # self._pickit.pick_up_items()
        # wait(0.5)
        
        # if not data["stash_open"]:
        #     self._a3.open_stash(Location.A3_STASH_WP)
        # self._ui_manager.stash_all_items(self._config.char["num_loot_columns"], self._item_finder, False)

        # self._a3.open_stash(Location.A3_STASH_WP)

        # self._a3.open_wp(Location.A3_STASH_WP)

        # self._char.toggle_run_walk(should_walk=False)

        # m = self._api.find_monster_by_name(Npc.ASHEARA)
        # self._pather.move_mouse_to_monster(m)       
        # x, y = mouse.get_position()
        # print(f"(x, y) = {(x, y)}")
        # wait(2.0)
        # x, y = mouse.get_position()
        # print(f"(x, y) = {(x, y)}")

        # pp.pprint(data["hovered_unit"])
        # pp.pprint(data["hovered_unit_type"])

        # self._pather.walk_to_position((133, 100))

        # self._town_manager.buy_pots(Location.A3_TOWN_START)
        # self._a5.open_trade_and_repair_menu()
        # wait(1)
        
        # data = self._api.wait_for_data()
        # if data["any_menu_open"]:
        #     print("menu open, esc...")
        #     keyboard.send("esc")
        # wait(0.5)
        # self._a3.identify()
        # print(mouse.get_position())
        # print(f"Player location: {point_str(self._api.data['player_pos_area'])}")

        # self._a3.open_stash()
        # ormus = self._api.find_monster_by_name(Npc.ORMUS)
        # if ormus:
        #     print(f"    Ormus distance: {math.dist(ormus['position_area'], self._api.data['player_pos_area'])} (euclidean)")
        # else:
        #     print(f"    No Ormus: {ormus}")

        # self.stop()

        # self._a1.open_wp()


        # get_free_inventory_space(self._api.data["inventory_items"], self._config.char["num_loot_columns"])


        # self._pather.click_object("Bank")
        # self.run_a2_tests()

        # self._a3.resurrect()
        # self._a3.find_vendor_and_open_trade(Npc.ASHEARA, menu_selection="resurrect", confirm_menu=None, y_offset=-55)

        # pickled = self.load_pickle("pickles/_TheWorldstoneChamber_20220530_225113.p")
        # print(f"Loaded pickle data, type: {type(pickled)}")
        # for m in pickled["monsters"]
        #     if "Unique" in m["type"] or "Baal" in m["name"]:
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

        # # pit_lvl2 = self._pather.get_entity_coords_from_str("Pit Level 2", "points_of_interest", False)
        # akara = self._api.find_npc(Npc.AKARA)
        # pf = PathFinder(self._api, 25)
        # path = pf.solve_tsp(akara["position_area"], True)
        # self.start_overlay()
        # nodes = []
        # current = pf.player_node
        # for node in path:
        #     print(f"    distance from current ({current}) to next node ({node}): {math.dist(current, node)}")
        #     bfs_nodes = make_path_bfs(current, node, self._api.data["map"])
        #     for n in bfs_nodes:
        #         nodes.append(n)
        #     self._pather.traverse_walking(node, self._char)
        #     current = node
        # self._api._current_path = nodes
        return True

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
        self._a5 = self._town_manager.a5

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
        restore_d2r_window_visibility()
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

    def dump_data_to_file(self, do_pickle: bool = False) -> str:
        fp = self._api.write_data_to_file()
        if fp is not None:
            try:
                os.system("start " + fp)
            except BaseException as e:
                print(f"Error writing data to a file: {e}")
        self.stop()

    def start_api(self):
        set_d2r_always_on_top()
        self._screen.activate_d2r_window()
        wait(0.2)
        data = None
        print(("-" * 80) + "\n\nStarting API...")
        while data is None:
            wait(0.2)
            data = self._api.get_data()
        return data

    def test_a1_town(self):
        # print("\n\n Testing open_trade_and_repair_menu()...")
        # debug._a1.open_trade_and_repair_menu()
        # wait(3)    

        print("\n\n Testing open_trade_menu()...")  
        debug._a1.open_trade_menu()
        wait(3)

    def test_a2_town(self):
        print("\n\n Testing heal()...")
        self._a2.heal()
        wait(3)
        
        print("\n\n Testing open_stash()...")
        self._a2.open_stash()
        wait(3)
        
        print("\n\n Testing identify()...")
        self._a2.identify()
        wait(3)
        
        print("\n\n Testing open_trade_menu()...")
        self._a2.open_trade_menu()
        wait(3)
        
        print("\n\n Testing open_trade_and_repair_menu()...")
        self._a2.open_trade_and_repair_menu()
        wait(3)
        
        print("\n\n Testing open_wp()...")
        self._a2.open_wp()
        wait(3)

    def test_a3_town(self):
        print("\n\n Testing heal()...")
        self._a3.heal()
        wait(3)
        
        print("\n\n Testing open_wp()...")
        self._a3.resurrect()
        wait(3)
        
        print("\n\n Testing open_stash()...")
        self._a3.open_stash()
        wait(3)
        
        print("\n\n Testing identify()...")
        self._a3.identify()
        wait(3)
        
        print("\n\n Testing open_trade_menu()...")
        self._a3.open_trade_menu()
        wait(3)
        
        print("\n\n Testing open_wp()...")
        self._a3.open_wp()
        wait(3)

    def test_a4_town(self):
        print("\n\nTesting resurrect()...")
        self._a4.resurrect(Location.A4_TOWN_START)
        wait(3)
        self._pather.walk_to_position((46, 41), 6)

        wait(4)
        print("\n\nTesting open_wp()...")
        self._a4.open_wp(Location.A4_TOWN_START)
        wait(3)
        self._pather.walk_to_position((46, 41), 6)

        wait(4)
        print("\n\nTesting identify()...")
        self._a4.identify(Location.A4_TOWN_START)
        wait(3)
        self._pather.walk_to_position((46, 41), 6)

        wait(4)
        print("\n\nTesting gamble()...")
        self._a4.gamble(Location.A4_TOWN_START)
        wait(3)
        self._pather.walk_to_position((46, 41), 6)

        wait(4)
        print("\n\nTesting open_trade_menu()...")
        self._a4.open_trade_menu(Location.A4_TOWN_START)
        wait(3)
        self._pather.walk_to_position((46, 41), 6)

        wait(4)
        print("\n\nTesting open_stash()...")
        self._a4.open_stash(Location.A4_TOWN_START)
        self._pather.walk_to_position((46, 41), 6)

        wait(4)
        print("\n\nTesting heal()...")
        self._a4.heal(Location.A4_TOWN_START)
        self._pather.walk_to_position((46, 41), 6)

        wait(4)
        print("\n\nTesting open_trade_and_repair_menu()...")
        self._a4.open_trade_and_repair_menu(Location.A4_TOWN_START)

    def find_coronet(self):
        start = time.time()
        found = False
        while not found and time.time() - start < 20.0:
            result = self._template_finder.search_and_wait("CORONET", roi=self._config.ui_roi["left_inventory"], time_out=0.4, normalize_monitor=True)
            if result.valid:
                mouse.move(*result.center, delay_factor=[0.1, 0.15])
                found = True
            else:
                mouse.move(*self._screen.convert_abs_to_monitor((-279, 156)), delay_factor=[0.1, 0.15])
                mouse.click(button="left")

if __name__ == "__main__":
    from utils.custom_mouse import mouse
    debug = None

    for proc in psutil.process_iter():
        pname = proc.name().lower()
        if "python" in pname or "d2r" in pname or "bot" in pname or "map" in pname or "cmd" in pname:
            print(proc.name())
            pp.pprint(proc)

    try:
        debug = Debug()
        debug.start_api()
        
        print(f"Player location: {point_str(debug._api.data['player_pos_area'])}")
        last_y = 0
        last_x, last_y = mouse.get_position()
        def do_stuff(debug):
            print(("*" * 80) + "\nDoing stuff...")
            wait(0.5)
            start = time.time()
            try:
                debug.do_stuff()
            except BaseException as e:
                print(e)
                traceback.print_exc()
            # stop_debug(game_controller, overlay)
            elapsed = round(time.time() - start, 2)
            print(f"Done doing stuff in {elapsed} seconds")
    
        # keyboard.add_hotkey(config.advanced_options["resume_key"], lambda: pickit.pick_up_items(char, True))
        keyboard.add_hotkey(debug._config.advanced_options['save_d2r_data_to_file_key'], lambda: debug.dump_data_to_file())
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
