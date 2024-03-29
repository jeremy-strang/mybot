from d2r.d2r_api import D2rApi
from template_finder import TemplateFinder
from ui import UiManager
from ui import BeltManager
from pathing import Location
import cv2
import time
import keyboard
from utils.custom_mouse import mouse
from utils.misc import cut_roi, color_filter, wait
from logger import Logger
from screen import Screen
import numpy as np
import time
from config import Config
from obs import ObsRecorder


class HealthManager:
    def __init__(self, screen: Screen, template_finder: TemplateFinder, obs_recorder: ObsRecorder, api: D2rApi):
        self._config = Config()
        self._obs_recorder = obs_recorder
        self._screen = screen
        self._template_finder = template_finder
        self._ui_manager = UiManager(screen, self._template_finder, self._obs_recorder, api)
        self._belt_manager = None # must be set with the belt manager form bot.py
        self._do_monitor = False
        self._did_chicken = False
        self._last_rejuv = time.time()
        self._last_health = time.time()
        self._last_mana = time.time()
        self._last_merc_healh = time.time()
        self._callback = None
        self._pausing = True
        self._last_chicken_screenshot = None
        self._last_location = ""
        self._api = api

    def stop_monitor(self):
        self._do_monitor = False

    def set_belt_manager(self, belt_manager: BeltManager):
        self._belt_manager = belt_manager

    def set_callback(self, callback):
        self._callback = callback

    def did_chicken(self):
        return self._did_chicken

    def reset_chicken_flag(self):
        self._did_chicken = False
        self._pausing = True

    def update_location(self, loc: Location):
        if loc is not None and type(loc) == str:
            bosses = ["shenk", "eldritch", "pindle", "nihlathak", "trav", "arc", "diablo", "andy", "meph", "tower", "baal", "pit", "stony"]
            prev_value = self._pausing
            self._pausing = not any(substring in loc for substring in bosses)
            if self._pausing != prev_value:
                debug_str = "pausing" if self._pausing else "active"
                Logger.info(f"Health Manager is now {debug_str}")
        self._last_location = loc

    @staticmethod
    def get_health(img: np.ndarray) -> float:
        config = Config()
        health_rec = [config.ui_pos["health_left"], config.ui_pos["health_top"], config.ui_pos["health_width"], config.ui_pos["health_height"]]
        health_img = cut_roi(img, health_rec)
        # red mask
        mask1, _ = color_filter(health_img, [np.array([0, 110, 20]), np.array([2, 255, 255])])
        mask2, _ = color_filter(health_img, [np.array([178, 110, 20]), np.array([180, 255, 255])])
        mask = cv2.bitwise_or(mask1, mask2)
        health_percentage = (float(np.sum(mask)) / mask.size) * (1/255.0)
        # green (in case of poison)
        mask, _ = color_filter(health_img, [np.array([47, 90, 20]), np.array([54, 255, 255])])
        health_percentage_green = (float(np.sum(mask)) / mask.size) * (1/255.0)
        return max(health_percentage, health_percentage_green)

    @staticmethod
    def get_mana(img: np.ndarray) -> float:
        config = Config()
        mana_rec = [config.ui_pos["mana_left"], config.ui_pos["mana_top"], config.ui_pos["mana_width"], config.ui_pos["mana_height"]]
        mana_img = cut_roi(img, mana_rec)
        mask, _ = color_filter(mana_img, [np.array([117, 120, 20]), np.array([121, 255, 255])])
        mana_percentage = (float(np.sum(mask)) / mask.size) * (1/255.0)
        return mana_percentage

    @staticmethod
    def get_merc_health(img: np.ndarray) -> float:
        config = Config()
        health_rec = [config.ui_pos["merc_health_left"], config.ui_pos["merc_health_top"], config.ui_pos["merc_health_width"], config.ui_pos["merc_health_height"]]
        merc_health_img = cut_roi(img, health_rec)
        merc_health_img = cv2.cvtColor(merc_health_img, cv2.COLOR_BGR2GRAY)
        _, health_tresh = cv2.threshold(merc_health_img, 5, 255, cv2.THRESH_BINARY)
        merc_health_percentage = (float(np.sum(health_tresh)) / health_tresh.size) * (1/255.0)
        return merc_health_percentage

    def _do_chicken(self, img):
        if self._callback is not None:
            self._callback()
            self._callback = None
        if self._config.general["info_screenshots"]:
            self._last_chicken_screenshot = "./info_screenshots/info_debug_chicken_" + time.strftime("%Y%m%d_%H%M%S") + ".png"
            cv2.imwrite(self._last_chicken_screenshot, img)
    
        # clean up key presses that might be pressed in the run_thread
        keyboard.release(self._config.char["stand_still"])
        wait(0.02, 0.05)
        keyboard.release(self._config.char["show_items"])
        wait(0.02, 0.05)
        mouse.release(button="left")
        wait(0.02, 0.05)
        mouse.release(button="right")
        time.sleep(0.01)
        self._ui_manager.save_and_exit(does_chicken=True)
        self._did_chicken = True
        self._pausing = True

    def start_monitor(self):
        Logger.info("Start health monitoring")
        self._do_monitor = True
        self._did_chicken = False
        start = time.time()
        while self._do_monitor:
            time.sleep(0.1)

            # Wait until the flag is reset by main.py
            if self._did_chicken or self._pausing: continue

            in_game = False
            health_percentage = 1.0
            mana_percentage = 1.0
            merc_alive = True
            merc_health_percentage = 1.0
            should_chicken = False

            if self._api is not None:
                in_game = self._api.in_game
                health_percentage = self._api.player_health_pct
                mana_percentage = self._api.player_mana_pct
                merc_alive = self._api.merc_alive
                merc_health_percentage = self._api.merc_health_pct
                should_chicken= self._api.should_chicken
            else:
                img = self._screen.grab()
                in_game = self._template_finder.search("WINDOW_INGAME_OFFSET_REFERENCE", img, roi=self._config.ui_roi["window_ingame_ref"], threshold=0.9).valid
                health_percentage = self.get_health(img)
                mana_percentage = self.get_mana(img)
                merc_alive = self._template_finder.search(["MERC_A2", "MERC_A1", "MERC_A5", "MERC_A3"], img, roi=self._config.ui_roi["merc_icon"]).valid
                merc_health_percentage = self.get_merc_health(img)

            if in_game:
                # check rejuv
                success_drink_rejuv = False
                last_drink = time.time() - self._last_rejuv
                if (health_percentage < self._config.char["take_rejuv_potion_health"] and last_drink > 1) or \
                (mana_percentage < self._config.char["take_rejuv_potion_mana"] and last_drink > 2):
                    success_drink_rejuv = self._belt_manager.drink_potion("rejuv", stats=[health_percentage, mana_percentage])
                    self._last_rejuv = time.time()

                # in case no rejuv was used, check for chicken, health pot and mana pot usage
                if not success_drink_rejuv:
                    # check health
                    last_drink = time.time() - self._last_health
                    if should_chicken or health_percentage < self._config.char["chicken"] and (time.time() - start) > 6:
                        Logger.warning(f"Trying to chicken, player HP {(health_percentage*100):.1f}%!")
                        img = self._screen.grab()
                        self._do_chicken(img)
                    elif health_percentage < self._config.char["take_health_potion"] and last_drink > 3.5 and not should_chicken:
                        self._belt_manager.drink_potion("health", stats=[health_percentage, mana_percentage])
                        self._last_health = time.time()
                    # check mana
                    last_drink = time.time() - self._last_mana
                    if mana_percentage < self._config.char["take_mana_potion"] and last_drink > 4:
                        self._belt_manager.drink_potion("mana", stats=[health_percentage, mana_percentage])
                        self._last_mana = time.time()
                
                # check merc
                if merc_alive:
                    last_drink = time.time() - self._last_merc_healh
                    if merc_health_percentage < self._config.char["merc_chicken"]:
                        Logger.warning(f"Trying to chicken, merc HP {(merc_health_percentage*100):.1f}%!")
                        self._do_chicken(img)
                    if merc_health_percentage < self._config.char["heal_rejuv_merc"] and last_drink > 4.0:
                        self._belt_manager.drink_potion("rejuv", merc=True, stats=[merc_health_percentage])
                        self._last_merc_healh = time.time()
                    elif merc_health_percentage < self._config.char["heal_merc"] and last_drink > 7.0:
                        self._belt_manager.drink_potion("health", merc=True, stats=[merc_health_percentage])
                        self._last_merc_healh = time.time()
        Logger.debug("Stop health monitoring")
