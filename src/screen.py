from pydoc import cli
from utils.coordinates import world_to_abs
import numpy as np
from mss import mss
import cv2
import time
from logger import Logger
from typing import Tuple
from config import Config
from utils.misc import find_d2r_window, clip_abs_point
import os

class Screen:
    """Grabs images from screen and converts different coordinate systems to each other"""

    def __init__(self):
        self._sct = mss()
        if len(self._sct.monitors) == 1:
            Logger.error("How do you not have a monitor connected?!")
            os._exit(1)
        self._config = Config()
        self._monitor_roi = self._sct.monitors[0]
        # Find d2r screen offsets and monitor idx
        self.found_offsets = False
        position = None
        Logger.debug("Using WinAPI to search for window under D2R.exe process")
        position = find_d2r_window()
        if position is not None:
            self._set_window_position(*position)
        else:
            if self._config.general["info_screenshots"]:
                cv2.imwrite("./info_screenshots/error_d2r_window_not_found_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self.grab())
            Logger.error("Could not determine window offset. Please make sure you have the D2R window open.")

    def _set_window_position(self, offset_x: int, offset_y: int):
        Logger.debug(f"Set offsets: left {offset_x}px, top {offset_y}px")
        self._monitor_roi["top"] = offset_y
        self._monitor_roi["left"] = offset_x
        self._monitor_roi["width"] = self._config.ui_pos["screen_width"]
        self._monitor_roi["height"] = self._config.ui_pos["screen_height"]
        self._monitor_x_range = (self._monitor_roi["left"] + 10, self._monitor_roi["left"] + self._monitor_roi["width"] - 10)
        self._monitor_y_range = (self._monitor_roi["top"] + 10, self._monitor_roi["top"] + self._monitor_roi["height"] - 10)
        self.found_offsets = True

    def convert_monitor_to_screen(self, screen_coord: Tuple[float, float]) -> Tuple[float, float]:
        return (screen_coord[0] - self._monitor_roi["left"], screen_coord[1] - self._monitor_roi["top"])

    def convert_screen_to_monitor(self, screen_coord: Tuple[float, float]) -> Tuple[float, float]:
        x = screen_coord[0] + self._monitor_roi["left"]
        y = screen_coord[1] + self._monitor_roi["top"]
        return (np.clip(x, *self._monitor_x_range), np.clip(y, *self._monitor_y_range))

    def convert_abs_to_screen(self, abs_coord: Tuple[float, float]) -> Tuple[float, float]:
        # abs has it's center on char which is the center of the screen
        return ((self._monitor_roi["width"] // 2) + abs_coord[0], (self._monitor_roi["height"] // 2) + abs_coord[1])

    def convert_screen_to_abs(self, screen_coord: Tuple[float, float]) -> Tuple[float, float]:
        return (screen_coord[0] - (self._monitor_roi["width"] // 2), screen_coord[1] - (self._monitor_roi["height"] // 2))

    def convert_area_to_monitor(self, pos_world: Tuple[float, float], player_pos_world: Tuple[float, float], clip_input: bool = False) -> Tuple[float, float]:
        pos_abs = world_to_abs(pos_world, player_pos_world)
        return self.convert_abs_to_monitor(pos_abs, clip_input)

    def convert_abs_to_monitor(self, abs_coord: Tuple[float, float], clip_input: bool = False) -> Tuple[float, float]:
        if clip_input:
            abs_coord = clip_abs_point(abs_coord)
        screen_coord = self.convert_abs_to_screen(abs_coord)
        monitor_coord = self.convert_screen_to_monitor(screen_coord)
        return monitor_coord

    def convert_player_target_world_to_monitor(self, target_pos_world: Tuple[float, float], player_pos_world: Tuple[float, float]) -> Tuple[float, float]:
        target_pos = world_to_abs(target_pos_world, player_pos_world)
        target_pos = [target_pos[0] - 9.5,target_pos[1] - 39.5]
        x = np.clip(target_pos[0], -638, 638)
        y = np.clip(target_pos[1], -350, 235)
        pos_m = self.convert_abs_to_monitor([x, y])
        return pos_m

    def grab(self) -> np.ndarray:
        img = np.array(self._sct.grab(self._monitor_roi))
        return img[:, :, :3]
