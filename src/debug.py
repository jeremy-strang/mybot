import json
import time
import traceback
from tracemalloc import stop
from char.hammerdin import Hammerdin
import game_controller
from item.pickit import PickIt
import keyboard
import os
import sys
from npc_manager import Npc
from obs import obs_recorder
from pathing import PathFinder
from run.andy import Andy
from run.pit import Pit
from run.trav import Trav

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
from item import ItemFinder
from game_stats import GameStats
from char.barbarian.zerker_barb import ZerkerBarb

import threading
from overlay import Overlay
from main import on_exit
from utils.custom_mouse import mouse
from utils.misc import wait
from obs import ObsRecorder
from utils.monsters import find_npc

if __name__ == "__main__":
    from mas import world_to_abs
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
        item_finder = ItemFinder()
        ui_manager = UiManager(screen, template_finder, obs_recorder, api, game_stats)
        belt_manager = BeltManager(screen, template_finder, api)
        pickit = PickIt(screen, item_finder, ui_manager, belt_manager, api)

        char = Hammerdin(config.hammerdin, screen, template_finder, ui_manager, api, obs_recorder, old_pather, pather)
        # char = ZerkerBarb(config.zerker_barb, screen, template_finder, ui_manager, api, obs_recorder, old_pather, pather)
        char.discover_capabilities(force=True)
        bot = Bot(screen, game_stats, template_finder, api, obs_recorder)
        pit = Pit(screen, template_finder, old_pather, bot._town_manager, ui_manager, char, pickit, api, pather, obs_recorder)
        trav = Trav(template_finder, old_pather, bot._town_manager, ui_manager, char, pickit, api, pather, obs_recorder)
        andy = Andy(screen, old_pather, bot._town_manager, ui_manager, char, pickit, api, pather, obs_recorder)

        data = None
        print(("-" * 80) + "\n\nStarting API...")
        while data is None:
            wait(0.2)
            data = api.get_data()
        
        def write_data_to_file(data, data_str):
            current_area = data["current_area"]
            with open(f"../botty_data_{current_area}.json", "w") as f:
                f.write(json.dumps(json.loads(data_str), indent=4, sort_keys=True))
                f.close()

        def do_stuff():
            print("Doing stuff...")
            data = api.get_data()
            # potion_type = "rejuv"
            # if "flattened_belt" in data and data["flattened_belt"] is not None:
            #     belt = data["flattened_belt"]
            #     if belt is not None and len(belt) > 0:
            #         for i in range(min(len(belt), 4)):
            #             print(f"belt[{i}]['ItemBaseName'] = {belt[i]['ItemBaseName']} type(belt[i]) = {type(belt[i])}")
            #             if len(belt) > i and "ItemBaseName" in belt[i] and potion_type.lower() in belt[i]["ItemBaseName"].lower():
            #                 print (f"potion{i+1}")
            

            # belt_manager.update_pot_needs(True)
            # print(belt_manager.get_pot_needs())

            print(belt_manager._get_potion_key("mana"))
            print(belt_manager._get_potion_key("health"))
            print(belt_manager._get_potion_key("rejuv"))

            # write_data_to_file(data, api._raw_data_str)
            
            
            # print(data["belt_items"])

            # bank = None
            # for obj in data["objects"]:w
            #     if obj["name"].startswith("Bank"):
            #         bank = obj
            #         print(f"object id: {obj['id']}, name: {obj['name']}, position: {obj['position']}")
            #         print(bank)
            
            # bot._town_manager.a3.open_stash(Location.A3_TOWN_START)
            # curr_loc = bot._town_manager.open_stash(bot.get_curr_location())

            # ui_manager.throw_out_junk(item_finder)

            stop_debug(game_controller, overlay)


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
        
            # overlay = start_overlay(bot, game_stats)
            print("Done doing stuff")

        # keyboard.add_hotkey(config.advanced_options["resume_key"], lambda: pickit.pick_up_items(char, True))
        keyboard.add_hotkey(config.advanced_options["resume_key"], lambda: do_stuff()) #lambda: pit.battle(True))
        keyboard.add_hotkey(config.advanced_options["exit_key"], lambda: stop_debug(game_controller, overlay))
        print("Ready!\n\n" + ("-" * 80))
        keyboard.wait()

        print("Press Enter to exit ...")
        input()
    except:
        traceback.print_exc()
    finally:
        stop_debug(game_controller, overlay)

# python src/debug.py   
