from dataclasses import dataclass
from lib2to3.pytree import Base
import keyboard
import os
import sys
from beautifultable import BeautifulTable
import logging
import traceback
from git import Repo

from version import __version__
from config import Config
from logger import Logger
from game_controller import GameController
from utils.graphic_debugger import GraphicDebuggerController
from utils.misc import restore_d2r_window_visibility, pad_str_sides
from utils.auto_settings import adjust_settings, backup_settings, restore_settings_from_backup
from utils.restart import kill_game

@dataclass
class Controllers():
    game: GameController
    debugger: GraphicDebuggerController

def check_arg(arg: str) -> bool:
    args = sys.argv
    if len(args) > 1:
        for i in range(1, len(args)):
            print(args[i])
            if args[i] == arg:
                show_options = True
                break

def start_or_pause_bot(controllers: Controllers):
    if controllers.game.is_running:
        controllers.game.toggle_pause_bot()
    else:
        # Kill any other controllers and start mybot
        controllers.debugger.stop()
        controllers.game.start()

def start_or_stop_graphic_debugger(controllers: Controllers):
    if controllers.debugger.is_running:
        controllers.debugger.stop()
    else:
        # Kill any other controller and start debugger
        controllers.game.stop()
        controllers.debugger.start()

def save_d2r_data_to_file(controllers: Controllers, pickle: bool = False):
    if controllers.game.is_running:
        try:
            controllers.game.save_d2r_data_to_file(pickle)
        except BaseException as e:
            print(f"Error saving D2R memory data: {e}")
    else:
        print(f"Error: D2R memory data is not available when the game is not running")

def on_exit(game_controller: GameController,  release_keys="capslock"):
    Logger.info("Exit key pressed, shutting down bot")
    for key in release_keys:
        try: keyboard.release(key)
        except: pass
    try: restore_d2r_window_visibility()
    except: pass

    if game_controller is not None and game_controller.obs_recorder is not None:
        try: game_controller.obs_recorder.stop_recording_if_enabled()
        except: pass
        try: game_controller.obs_recorder.stop_replaybuffer_if_enabled()
        except: pass
    os._exit(1)

def main():
    show_options = False # check_arg("options")

    controllers = Controllers(
        GameController(),
        GraphicDebuggerController()
    )

    config = Config()
    try:
        if not os.path.exists("stats"):
            os.system("mkdir stats")
        if not os.path.exists("info_screenshots") and (config.general["info_screenshots"] or config.general["message_api_type"] == "discord"):
            os.system("mkdir info_screenshots")
        if not os.path.exists("loot_screenshots") and (config.general["loot_screenshots"] or config.general["message_api_type"] == "discord"):
            os.system("mkdir loot_screenshots")
        if not os.path.exists("pickles") and config.advanced_options["dump_data_to_pickle_for_debugging"]:
            os.system("mkdir pickles")
    except BaseException as e:
        print(f"Error creating directories: {e}")

    if config.advanced_options["logg_lvl"] == "info":
        Logger.init(logging.INFO)
    elif config.advanced_options["logg_lvl"] == "debug":
        Logger.init(logging.DEBUG)
    else:
        Logger.error(f"ERROR: Unkown logg_lvl {config.advanced_options['logg_lvl']}. Must be one of [info, debug]")

    print("\n" + pad_str_sides(f"MyBot {__version__} [name: {config.general['name']}]", "="))
    print(f"Active branch:        {config.active_branch}")
    print(f"Latest Commit Sha:    {config.latest_commit_sha}")
    print("Hotkeys:")
    print(f"    Backup settings:          {config.advanced_options['settings_backup_key']} key")
    print(f"    Adjust settings:          {config.advanced_options['auto_settings_key']} key")
    print(f"    Save D2R data to a file:  {config.advanced_options['save_d2r_data_to_file_key']} key")
    print(f"    Toggle Start/Pause Bot:   {config.advanced_options['resume_key']} key")
    print(f"    Stop Bot:                 {config.advanced_options['exit_key']} key")
    print("=" * 80 + "\n")

    dump_pickles = config.advanced_options["dump_data_to_pickle_for_debugging"]
    keyboard.add_hotkey(config.advanced_options['auto_settings_key'], lambda: adjust_settings())
    keyboard.add_hotkey(config.advanced_options['graphic_debugger_key'], lambda: start_or_stop_graphic_debugger(controllers))
    keyboard.add_hotkey(config.advanced_options['restore_settings_from_backup_key'], lambda: restore_settings_from_backup())
    keyboard.add_hotkey(config.advanced_options['settings_backup_key'], lambda: backup_settings())
    keyboard.add_hotkey(config.advanced_options['save_d2r_data_to_file_key'], lambda: save_d2r_data_to_file(controllers, dump_pickles))
    keyboard.add_hotkey(config.advanced_options['resume_key'], lambda: start_or_pause_bot(controllers))
    keyboard.add_hotkey(config.advanced_options["exit_key"], lambda: on_exit(game_controller, [config.char["stand_still"], config.char["force_move"]]))
    keyboard.wait()

if __name__ == "__main__":
    # To avoid cmd just closing down, except any errors and add a input() to the end
    game_controller = None
    debugger_controller = None
    try:
        game_controller = GameController()
        debugger_controller = GraphicDebuggerController()
        main()
    except:
        traceback.print_exc()
        if game_controller is not None:
            if game_controller.config is not None and game_controller.config.general['kill_d2r_on_bot_exception']:
                kill_game()
        on_exit(game_controller)
    print("Press Enter to exit ...")
    input()
