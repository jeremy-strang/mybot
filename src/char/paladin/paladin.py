from ast import Tuple
from sre_parse import State
from d2r.d2r import TOWNS
import keyboard
from char.skill import Skill
from utils.coordinates import world_to_abs
from utils.custom_mouse import mouse
from char import IChar
from template_finder import TemplateFinder
from ui import UiManager
from pathing import OldPather
from logger import Logger
from screen import Screen
from utils.misc import rotate_vec, unit_vector, wait, is_in_roi, point_str
from monsters import sort_and_filter_monsters, get_unlooted_monsters, CHAMPS_UNIQUES
from constants import Roi
import time
from pathing import OldPather, Location
import math
import threading
import numpy as np
import random

from d2r.d2r_api import D2rApi
from pathing import Pather
from monsters import MonsterRule, MonsterType
from obs import ObsRecorder

class Paladin(IChar):
    def __init__(self, skill_hotkeys: dict, screen: Screen, template_finder: TemplateFinder, ui_manager: UiManager, api: D2rApi, obs_recorder: ObsRecorder, old_pather: OldPather, pather: Pather):
        Logger.info("Setting up Paladin")
        super().__init__(skill_hotkeys, screen, template_finder, ui_manager, api, obs_recorder, pather, old_pather)
        self._old_pather = old_pather
        self._pather = pather
        self._do_pre_move = True
        if not self._skill_hotkeys["teleport"]:
            self._do_pre_move = False

    def get_cast_frames(self):
        fcr = self.get_fcr()
        frames = 15
        if fcr >= 125: frames = 9
        if fcr >= 75: frames = 10
        elif fcr >= 48: frames = 11
        elif fcr >= 30: frames = 12
        elif fcr >= 18: frames = 13
        elif fcr >= 9: frames = 14
        Logger.debug(f"FCR recalculated to be FCR: {fcr} ({frames} frames)")
        return frames

    def pre_buff(self, switch_back=True):
        Logger.info(f'pre_buff.')
        
        if self._char_config["cta_available"]:
            self._pre_buff_cta()
        keyboard.send(self._skill_hotkeys["holy_shield"])
        wait(0.05, 0.1)
        mouse.click(button="right")
        wait(self._cast_duration + 0.04, self._cast_duration + 0.06)
        Logger.info(f'pre_buff end.')

    def pre_move(self):
        # select teleport if available
        super().pre_move()
        # in case teleport hotkey is not set or teleport can not be used, use vigor if set
        should_cast_vigor = self._skill_hotkeys["vigor"] and not self._ui_manager.is_right_skill_selected(Skill.Vigor)
        can_teleport = self.can_tp and self._ui_manager.is_right_skill_active()
        if self._api.data and self._api.data["current_area"] in TOWNS:
            can_teleport = False
        if should_cast_vigor and not can_teleport:
            keyboard.send(self._skill_hotkeys["vigor"])
            wait(0.15)

    def post_attack(self) -> bool:
        mouse.release(button="left")
        wait(0.02, 0.4)
        keyboard.release(self._char_config["stand_still"]) 
        wait(0.02, 0.4)
        return True