import json
import traceback
from tracemalloc import stop
from char.hammerdin import Hammerdin
import game_controller
from item.pickit import PickIt
import keyboard
import os
import sys
import time
import numpy as np
from mas import world_to_abs
from npc_manager import Npc
from obs import obs_recorder
from run.pit import Pit

from screen import Screen
from bot import Bot
from config import Config
from game_stats import GameStats
from pather import Pather
from pather_v2 import PatherV2
from api import MapAssistApi
import threading
from state_monitor import StateMonitor
from template_finder import TemplateFinder
from town import TownManager
from ui import UiManager, BeltManager
from item import ItemFinder
from game_stats import GameStats
from char.barbarian.zerker_barb import ZerkerBarb

import threading
from overlay import Overlay
from main import on_exit
from utils.misc import round_point, wait
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
        print(("-" * 70) + "\n\nStarting API...\n\n" + ("-" * 70))
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

        bot = Bot(screen, game_stats, template_finder, api, obs_recorder)
        char = Hammerdin(config.hammerdin, screen, template_finder, ui_manager, api, obs_recorder, pather, pather_v2)
        # char = ZerkerBarb(config.zerker_barb, screen, template_finder, ui_manager, api, pather, pather_v2)
        pit = Pit(screen, template_finder, pather, bot._town_manager, ui_manager, char, pickit, api, pather_v2, obs_recorder)
        
        char.discover_capabilities(force=True)
        overlay = start_overlay(bot, game_stats)

        def write_data_to_file(data, data_str):
            current_area = data["current_area"]
            with open(f"../botty_data_{current_area}.json", "w") as f:
                f.write(json.dumps(json.loads(data_str), indent=4, sort_keys=True))
                f.close()

        def find_updated_monster(id: int) -> dict:
            data = api.get_data()
            if data is not None and "monsters" in data and type(data["monsters"]) is list:
                for m in data["monsters"]:
                    if m["id"] == id:
                        return m
            return None
        
        def move_mouse_to_monster(m):
            abs_screen_position = m["abs_screen_position"]
            x = np.clip(abs_screen_position[0], -638, 638)
            y = np.clip(abs_screen_position[1], -350, 225)
            pos_m = screen.convert_abs_to_monitor([x, y])
            x_m = pos_m[0]
            y_m = pos_m[1]
            adjusted_pos_m = [x_m - 5, y_m - 35] if m["dist"] < 25 else [x_m, y_m]
            mouse.move(*adjusted_pos_m, delay_factor=[0.1, 0.2])

        def do_stuff():
            data = api.get_data()
            write_data_to_file(data, api._raw_data_str)
            for m in data["monsters"]:
                name = m["name"]
                if name == "Ormus":
                    menu_open = False
                    start = time.time()
                    while not menu_open and time.time() - start < 10:
                        m = find_updated_monster(m["id"])
                        move_mouse_to_monster(m)
                        if m is not None:
                            mouse.click(button="left")
                            wait(1.3)
                            data = api.get_data()
                            menu_open = data is not None and data["menus"]["NpcInteract"]
                            if menu_open:
                                bot._town_manager.a3._npc_manager.press_npc_btn(Npc.ORMUS, "trade")
                    # position = round_point(m["position"], 2)
                    # abs_screen_position = round_point(m["abs_screen_position"], 2)
                    # mouse_pos_m = screen.convert_abs_to_monitor(abs_screen_position)
                    # move_pos_m = screen.convert_player_target_world_to_monitor(m["position"], data["player_pos_world"])
                    # mouse_pos_m = round_point(world_to_abs(m["position"], data["player_pos_world"]), 2)
                    # mouse_pos_m = round_point(screen.convert_player_target_world_to_monitor(position, data["player_pos_world"]), 2)
                    # dist = m["dist"]
                    # states = ", ".join(m["state_strings"])
                    # is_hovered = m["unit"]["IsHovered"] == True
                    # print(f"\n-------------------- Monster: {name} --------------------")
                    # print(f"  position:             {position}")
                    # print(f"  abs_screen_position:  {abs_screen_position}")
                    # print(f"  mouse_pos_m:          {mouse_pos_m}")
                    # print(f"  move_pos_m:           {move_pos_m}")
                    # print(f"  dist:                 {round(dist, 2)}")
                    # print(f"  states:               {states}")
                    # print(f"  is_hovered:           {is_hovered}")
                    # print(m)
                    # wait(1.0)
                    
        do_stuff()
        
        # keyboard.add_hotkey(config.advanced_options["resume_key"], lambda: pickit.pick_up_items(char, True))
        keyboard.add_hotkey(config.advanced_options["resume_key"], do_stuff) #lambda: pit.battle(True))
        keyboard.add_hotkey(config.advanced_options["exit_key"], lambda: stop_debug(game_controller, overlay))
        print(("-" * 70) + "\n\nReady!\n\n" + ("-" * 70))
        keyboard.wait()

        print("Press Enter to exit ...")
        input()
    except:
        traceback.print_exc()
    finally:
        stop_debug(game_controller, overlay)

# python src/debug.py   
