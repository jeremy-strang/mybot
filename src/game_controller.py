import os
import threading
import time
import cv2
import traceback
from obs import obs_recorder

from template_finder import TemplateFinder
from utils.auto_settings import check_settings
from bot import Bot
from config import Config
from death_manager import DeathManager
from game_recovery import GameRecovery
from game_stats import GameStats
from health_manager import HealthManager
from logger import Logger
from messages import Messenger
from screen import Screen
from ui.char_selector import CharSelector
from utils.restart import restart_game, kill_game
from utils.misc import kill_thread, set_d2r_always_on_top, restore_d2r_window_visibility
from api import MapAssistApi
from obs import ObsRecorder

from item_manager import ItemManager



class GameController:
    def __init__(self):
        self.config = Config()
        self.obs_recorder = ObsRecorder(self.config)
        self.is_running = False
        self.screen = None
        self.template_finder = None
        self.health_monitor_thread = None
        self.health_manager = None
        self.death_manager = None
        self.death_monitor_thread = None
        self.game_recovery = None
        self.game_stats = None
        self.game_controller_thread = None
        self.bot_thread = None
        self.bot = None
        self.api = None
        self.api_thread = None
        self.item_manager = None
        self.item_manater_thread = None
        self.overlay_thread = None
        self.overlay = None

    def run_bot(self, pick_corpse: bool = False):
        try:
            if self.config.general['restart_d2r_when_stuck']:
                # Make sure the correct char is selected
                if self.char_selector.has_char_template_saved():
                    Logger.info("Selecting original char")
                    self.char_selector.select_char()
                else:
                    Logger.info("Saving top-most char as template")
                    self.char_selector.save_char_template()
            # Start bot thread + API thread
            self.start_api_thread()
            #self.start_item_manager()
            self.bot = Bot(self.screen, self.game_stats, self.template_finder, self.api, self.obs_recorder, pick_corpse)
            self.bot_thread = threading.Thread(target=self.bot.start)
            self.bot_thread.daemon = True
            self.bot_thread.start()
            if self.config.advanced_options['debug_overlay']:
                self.start_overlay_thread(self.bot)
            # Register that thread to the death and health manager so they can stop the bot thread if needed
            self.death_manager.set_callback(lambda: self.bot.stop() or kill_thread(self.bot_thread))
            self.health_manager.set_callback(lambda: self.bot.stop() or kill_thread(self.bot_thread))
            self.health_manager.set_belt_manager(self.bot.get_belt_manager())
            do_restart = False
            messenger = Messenger()
            while 1:
                self.health_manager.update_location(self.bot.get_curr_location())
                max_game_length_reached = self.game_stats.get_current_game_length() > self.config.general["max_game_length_s"]
                max_consecutive_fails_reached = False if not self.config.general["max_consecutive_fails"] else self.game_stats.get_consecutive_runs_failed() >= self.config.general["max_consecutive_fails"]
                if max_game_length_reached or max_consecutive_fails_reached or self.death_manager.died() or self.health_manager.did_chicken():
                    # Some debug and logging
                    if max_game_length_reached:
                        Logger.info(f"Max game length reached. Attempting to restart {self.config.general['name']}!")
                        if self.config.general["info_screenshots"]:
                            cv2.imwrite("./info_screenshots/info_max_game_length_reached_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self.screen.grab())
                    elif self.death_manager.died():
                        self.game_stats.log_death(self.death_manager._last_death_screenshot)
                    elif self.health_manager.did_chicken():
                        self.game_stats.log_chicken(self.health_manager._last_chicken_screenshot)
                    self.bot.stop()
                    kill_thread(self.bot_thread)
                    # Try to recover from whatever situation we are and go back to hero selection
                    if max_consecutive_fails_reached: 
                        msg = f"Consecutive fails {self.game_stats.get_consecutive_runs_failed()} >= Max {self.config.general['max_consecutive_fails']}. Quitting botty."
                        Logger.error(msg)
                        if self.config.general["custom_message_hook"]:
                            messenger.send_message(msg)
                        self.safe_exit(1)
                        return False
                    else:
                        do_restart = self.game_recovery.go_to_hero_selection()
                    break
                time.sleep(0.5)
            self.bot_thread.join()
            if do_restart:
                # Reset flags before running a new bot
                self.death_manager.reset_death_flag()
                self.health_manager.reset_chicken_flag()
                self.game_stats.log_end_game(failed=max_game_length_reached)
                return self.run_bot(True)
            else:
                if self.config.general["info_screenshots"]:
                    cv2.imwrite("./info_screenshots/info_could_not_recover_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self.screen.grab())
                if self.config.general['restart_d2r_when_stuck']:
                    Logger.error("Could not recover from a max game length violation. Restarting the Game.")
                    if self.config.general["custom_message_hook"]:
                        messenger.send_message("Got stuck and will now restart D2R")
                    if restart_game(self.config.general["d2r_path"]):
                        self.game_stats.log_end_game(failed=max_game_length_reached)
                        if self.setup_screen():
                            self.template_finder = TemplateFinder(self.screen)
                            self.start_health_manager_thread()
                            self.start_death_manager_thread()
                            self.game_recovery = GameRecovery(self.screen, self.death_manager, self.template_finder)
                            return self.run_bot(True)
                    Logger.error("Could not restart the game. Quitting.")
                    messenger.send_message("Got stuck and could not restart the game. Quitting.")
                else:
                    Logger.error("Could not recover from a max game length violation. Quitting botty.")
                    if self.config.general["custom_message_hook"]:
                        messenger.send_message("Got stuck and will now quit botty")
                self.safe_exit(1)
        except BaseException as err:
            if self.config.general['kill_d2r_on_botty_error']:
                kill_game()
            traceback.print_exc()

    def start(self):
        # Check if we user should update the d2r settings
        diff = check_settings()
        if len(diff) > 0:
            Logger.warning("Your D2R settings differ from the requiered ones. Please use Auto Settings to adjust them. The differences are:")
            Logger.warning(f"{diff}")
        set_d2r_always_on_top()
        self.setup_screen()
        self.template_finder = TemplateFinder(self.screen)
        self.start_health_manager_thread()
        self.start_death_manager_thread()
        self.game_recovery = GameRecovery(self.screen, self.death_manager, self.template_finder, self.obs_recorder, self.api)
        self.game_stats = GameStats()        
        self.start_game_controller_thread()
        self.is_running = True

    def stop(self):
        restore_d2r_window_visibility()
        if self.overlay_thread: kill_thread(self.overlay_thread)
        if self.death_monitor_thread: kill_thread(self.death_monitor_thread)
        if self.health_monitor_thread: kill_thread(self.health_monitor_thread)
        if self.bot_thread: kill_thread(self.bot_thread)
        if self.game_controller_thread: kill_thread(self.game_controller_thread)
        if self.item_manager_thread: kill_thread(self.item_manager_thread)
        if self.api_thread: kill_thread(self.api_thread)
        self.api.stop()
        self.is_running = False
       
    def setup_screen(self):
        self.screen = Screen()
        if self.screen.found_offsets:
            return True
        return False

    def start_overlay_thread(self,bot):
        # Run game debug overlay
        from overlay import Overlay
        Logger.debug("Overlay thread starting...")
        self.overlay = Overlay(bot,self.game_stats)
        self.overlay_thread = threading.Thread(target=self.overlay.init)
        self.overlay_thread.daemon = True
        self.overlay_thread.start()

    def start_health_manager_thread(self):
        # Run health monitor thread
        self.health_manager = HealthManager(self.screen, self.template_finder, self.obs_recorder, self.api)
        self.health_monitor_thread = threading.Thread(target=self.health_manager.start_monitor)
        self.health_monitor_thread.daemon = True
        self.health_monitor_thread.start()

    def start_death_manager_thread(self):
        # Run death monitor thread
        self.death_manager = DeathManager(self.screen, self.template_finder)
        self.death_monitor_thread = threading.Thread(target=self.death_manager.start_monitor)
        self.death_monitor_thread.daemon = True
        self.death_monitor_thread.start()

    def start_item_manager(self):
        self.item_manager = ItemManager(self.screen,self.api)
        self.item_manager_thread = threading.Thread(target=self.item_manager.start)
        self.item_manager_thread.daemon = False
        self.item_manager_thread.start()

    def start_api_thread(self):
        # run map assist
        self.api = MapAssistApi(self.config.custom_files)
        self.api.start()

    def start_game_controller_thread(self):
        # Run game controller thread
        self.game_controller_thread = threading.Thread(target=self.run_bot)
        self.game_controller_thread.daemon = False
        self.game_controller_thread.start()

    def toggle_pause_bot(self):
        if self.bot:
            self.bot.toggle_pause()

    def safe_exit(self, error_code=0):
        kill_game()
        os._exit(error_code)

    def save_d2r_data_to_file(self):
        if self.api is not None:
            self.api.write_data_to_file()