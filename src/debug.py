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
from run.andy import Andy
from run.pit import Pit
from run.trav import Trav

from screen import Screen
from bot import Bot
from config import Config
from game_stats import GameStats
from pather import Location, Pather
from pathing import PatherV2
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

if __name__ == "__main__":
    from mas import world_to_abs
    from utils.custom_mouse import mouse
        
    def stop_debug(game_controller, overlay):
        ui_manager.abort = True
        if overlay is not None: overlay.stop_overlay()
        on_exit(game_controller)

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

        api = MapAssistApi()
        api_thread = threading.Thread(target=api.start)
        api_thread.daemon = False
        api_thread.start()

        data = None
        print(("-" * 80) + "\n\nStarting API...\n\n" + ("-" * 80))
        while data is None:
            wait(0.2)
            data = api.get_data()

        game_stats = GameStats() 
        template_finder = TemplateFinder(screen)
        pather = Pather(screen, template_finder)
        pather_v2 = PatherV2(screen, api)
        item_finder = ItemFinder()
        ui_manager = UiManager(screen, template_finder, game_stats)
        belt_manager = BeltManager(screen, template_finder)
        
        pickit = PickIt(screen, item_finder, ui_manager, belt_manager)

        # char = Hammerdin(config.hammerdin, screen, template_finder, ui_manager, api, obs_recorder, pather, pather_v2)
        char = ZerkerBarb(config.zerker_barb, screen, template_finder, ui_manager, api, obs_recorder, pather, pather_v2)
        char.discover_capabilities(force=True)
        bot = Bot(screen, game_stats, template_finder, api, obs_recorder)
        pit = Pit(screen, template_finder, pather, bot._town_manager, ui_manager, char, pickit, api, pather_v2, obs_recorder)
        trav = Trav(template_finder, pather, bot._town_manager, ui_manager, char, pickit, api, pather_v2, obs_recorder)
        andy = Andy(screen, pather, bot._town_manager, ui_manager, char, pickit, api, pather_v2, obs_recorder)
        
        def write_data_to_file(data, data_str):
            current_area = data["current_area"]
            with open(f"../botty_data_{current_area}.json", "w") as f:
                f.write(json.dumps(json.loads(data_str), indent=4, sort_keys=True))
                f.close()

        def do_stuff():
            route, clusters = pather_v2.create_cluster_route()
            api._current_path = route
            # for c in clusters:
            #     pather_v2.traverse_walking(c, char, obj=False, threshold=10)
            # bot._town_manager.a3.open_trade_menu(Location.A3_TOWN_START)

        # keyboard.add_hotkey(config.advanced_options["resume_key"], lambda: pickit.pick_up_items(char, True))
        keyboard.add_hotkey(config.advanced_options["resume_key"], lambda: do_stuff()) #lambda: pit.battle(True))
        keyboard.add_hotkey(config.advanced_options["exit_key"], lambda: stop_debug(game_controller, overlay))
        print(("-" * 80) + "\n\nReady!\n\n" + ("-" * 80))
        
        overlay = start_overlay(bot, game_stats)

        keyboard.wait()

        print("Press Enter to exit ...")
        input()
    except:
        traceback.print_exc()
    finally:
        stop_debug(game_controller, overlay)

# python src/debug.py   
