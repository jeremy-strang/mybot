import json
import math
import time
import traceback
from tracemalloc import stop
from turtle import pos
from char.hammerdin import Hammerdin
import game_controller
from pickit.pixel_pickit import PixelPickit
from pickit.pickit import Pickit
import keyboard
import os
import sys
from monsters.monster_rule import MonsterRule
from npc_manager import Npc
from obs import obs_recorder
from pathing import PathFinder
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
from api import MapAssistApi
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

if __name__ == "__main__":
    from utils.coordinates import world_to_abs
    from utils.custom_mouse import mouse
        
    def stop_debug(game_controller, overlay):
        ui_manager.abort = True
        if overlay is not None: overlay.stop_overlay()
        on_exit(game_controller, ["capslock", "space"])

    def start_overlay(bot, game_stats):
        print("Overlay thread starting...")
        overlay = Overlay(bot, game_stats)
        overlay_thread = threading.Thread(target=overlay.init)
        overlay_thread.daemon = True
        overlay_thread.start()
        return overlay

    overlay = None
    game_stats = None
    game_controller = None
    try:
        config = Config()
        screen = Screen()
        game_stats = GameStats()
        obs_recorder = ObsRecorder(config)

        api = MapAssistApi(config.custom_files)
        api_thread = threading.Thread(target=api.start)
        api_thread.daemon = False
        api_thread.start()

        game_stats = GameStats() 
        template_finder = TemplateFinder(screen)
        old_pather = OldPather(screen, template_finder)
        pather = Pather(screen, api)
        item_finder = ItemFinder(config)
        ui_manager = UiManager(screen, template_finder, obs_recorder, api, game_stats)
        belt_manager = BeltManager(screen, template_finder, api)

        char = Hammerdin(config.hammerdin, screen, template_finder, ui_manager, api, obs_recorder, old_pather, pather)
        pixel_pickit = PixelPickit(screen, item_finder, ui_manager, belt_manager, api, char, pather, game_stats)
        pickit = Pickit(screen, ui_manager, belt_manager, char, pather, api, game_stats)
        # char = ZerkerBarb(config.zerker_barb, screen, template_finder, ui_manager, api, obs_recorder, old_pather, pather)
        char.discover_capabilities(force=True)
        bot = Bot(screen, game_stats, template_finder, api, obs_recorder)
        pit = Pit(screen, template_finder, old_pather, bot._town_manager, ui_manager, char, pixel_pickit, api, pather, obs_recorder)
        travincal = Travincal(template_finder, old_pather, bot._town_manager, ui_manager, char, pixel_pickit, api, pather, obs_recorder)
        countess = Countess(template_finder, old_pather, bot._town_manager, ui_manager, char, pixel_pickit, api, pather, obs_recorder)
        andariel = Andariel(screen, old_pather, bot._town_manager, ui_manager, char, pixel_pickit, api, pather, obs_recorder)
        summoner = Summoner(screen, template_finder, old_pather, bot._town_manager, ui_manager, char, pixel_pickit, api, pather, obs_recorder)

        data = None
        print(("-" * 80) + "\n\nStarting API...")
        while data is None:
            wait(0.2)
            data = api.get_data()
        
        # overlay = start_overlay(bot, game_stats)
        # pp.pprint(config.items)

        def do_stuff():
            print("Doing stuff...")
            wait(0.5)
            start = time.time()
            try:
                data = api.get_data()
                
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

                # pixel_pickit.pick_up_items(char)

                # if not data["stash_open"]:
                #     bot._town_manager.a3.open_stash(Location.A3_STASH_WP)
                # ui_manager.stash_all_items(config.char["num_loot_columns"], item_finder, False)

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
                # akara = find_npc(Npc.AKARA, api)
                # pf = PathFinder(api)
                # start = pf.player_node

                # if akara is not None:
                #     path = pf.solve_tsp(end=akara["position"] - data["area_origin"])
                # else:
                #     path = pf.solve_tsp()
                # api._current_path = []
                # for node in path:
                #     api._current_path += pf.make_path_astar(start, node, True)
                #     start = node

                # api._current_path = path
                # bot._town_manager.a1.open_trade_menu(Location.A1_TOWN_START)

            except BaseException as e:
                print(e)
                traceback.print_exc()
            # stop_debug(game_controller, overlay)
            print("Done doing stuff")

        # keyboard.add_hotkey(config.advanced_options["resume_key"], lambda: pickit.pick_up_items(char, True))
        keyboard.add_hotkey(config.advanced_options['save_d2r_data_to_file_key'], lambda: api.write_data_to_file())
        keyboard.add_hotkey(config.advanced_options["resume_key"], lambda: do_stuff()) #lambda: pit.battle(True))
        keyboard.add_hotkey(config.advanced_options["exit_key"], lambda: stop_debug(game_controller, overlay))
        keyboard.add_hotkey("ctrl+=", lambda: start_overlay(bot, game_stats))
        print("Ready!\n\n" + ("-" * 80))
        keyboard.wait()

        print("Press Enter to exit ...")
        input()
    except:
        traceback.print_exc()
    finally:
        stop_debug(game_controller, overlay)

# python src/debug.py   
