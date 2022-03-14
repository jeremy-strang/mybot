import keyboard
from char.sorceress import Sorceress
from utils.custom_mouse import mouse
from logger import Logger
from utils.misc import wait, rotate_vec, unit_vector
import random
from old_pather import Location
import numpy as np
from logger import Logger
from config import Config
from screen import Screen
from template_finder import TemplateFinder
from ui import UiManager
from old_pather import OldPather, Location

from api.mapassist import MapAssistApi
from pathing import Pather
from state_monitor import StateMonitor
from obs import ObsRecorder


class NovaSorc(Sorceress):
    def __init__(self, skill_hotkeys: dict, screen: Screen, template_finder: TemplateFinder, ui_manager: UiManager, api: MapAssistApi, obs_recorder: ObsRecorder, old_pather: OldPather, pather: Pather):
        Logger.info("Setting up Nova Sorc")
        super().__init__(skill_hotkeys, screen, template_finder, ui_manager, api, obs_recorder)
        self._old_pather = old_pather
        self._pather = pather
        # we want to change positions a bit of end points
        self._old_pather.offset_node(149, (70, 10))

    def get_cast_frames(self):
        fcr = self.get_fcr()
        frames = 13
        if fcr >= 200: frames = 7
        elif fcr >= 105: frames = 8
        elif fcr >= 63: frames = 9
        elif fcr >= 37: frames = 10
        elif fcr >= 20: frames = 11
        elif fcr >= 9: frames = 12
        return frames

    def _nova(self, time_in_s: float):
        if not self._skill_hotkeys["nova"]:
            raise ValueError("You did not set nova hotkey!")
        keyboard.send(self._skill_hotkeys["nova"])
        wait(0.05, 0.1)
        start = time.time()
        while (time.time() - start) < time_in_s:
            wait(0.03, 0.04)
            mouse.press(button="right")
            wait(0.12, 0.2)
            mouse.release(button="right")

    def _move_and_attack(self, abs_move: tuple[int, int], atk_len: float):
        pos_m = self._screen.convert_abs_to_monitor(abs_move)
        self.pre_move()
        self.move(pos_m, force_move=True)
        self._nova(atk_len)

    def kill_pindle(self) -> bool:
        self._old_pather.traverse_nodes_fixed("pindle_end", self)
        self._cast_static(0.6)
        self._nova(self._char_config["atk_len_pindle"])
        return True

    def kill_eldritch(self) -> bool:
        self._old_pather.traverse_nodes_fixed([(675, 30)], self)
        self._cast_static(0.6)
        self._nova(self._char_config["atk_len_eldritch"])
        return True

    def kill_shenk(self) -> bool:
        self._old_pather.traverse_nodes((Location.A5_SHENK_SAFE_DIST, Location.A5_SHENK_END), self, time_out=1.0)
        self._cast_static(0.6)
        self._nova(self._char_config["atk_len_shenk"])
        return True

    def kill_council(self) -> bool:
        # Check out the node screenshot in assets/templates/trav/nodes to see where each node is at
        atk_len = self._char_config["atk_len_trav"] * 0.21
        # change node to be further to the right
        offset_229 = np.array([200, 100])
        self._old_pather.offset_node(229, offset_229)
        def clear_inside():
            self._old_pather.traverse_nodes_fixed([(1110, 120)], self)
            self._old_pather.traverse_nodes([229], self, time_out=0.8, force_tp=True)
            self._nova(atk_len)
            self._move_and_attack((-40, -20), atk_len)
            self._move_and_attack((40, 20), atk_len)
            self._move_and_attack((40, 20), atk_len)
        def clear_outside():
            self._old_pather.traverse_nodes([226], self, time_out=0.8, force_tp=True)
            self._nova(atk_len)
            self._move_and_attack((45, -20), atk_len)
            self._move_and_attack((-45, 20), atk_len)
        clear_inside()
        clear_outside()
        clear_inside()
        clear_outside()
        # change back node as it is used in trav.py
        self._old_pather.offset_node(229, -offset_229)
        return True

    def kill_nihlathak(self, end_nodes: list[int]) -> bool:
        atk_len = self._char_config["atk_len_nihlathak"] * 0.3
        # Move close to nihlathak
        self._old_pather.traverse_nodes(end_nodes, self, time_out=0.8, do_pre_move=False)
        # move mouse to center
        pos_m = self._screen.convert_abs_to_monitor((0, 0))
        mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
        self._cast_static(0.6)
        self._nova(atk_len)
        self._move_and_attack((50, 25), atk_len)
        self._move_and_attack((-70, -35), atk_len)
        return True

    def kill_summoner(self) -> bool:
        # move mouse to below altar
        pos_m = self._screen.convert_abs_to_monitor((0, 20))
        mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
        # Attack
        self._nova(self._char_config["atk_len_arc"])
        # Move a bit back and another round
        self._move_and_attack((0, 80), self._char_config["atk_len_arc"] * 0.5)
        wait(0.1, 0.15)
        self._nova(self._char_config["atk_len_arc"] * 0.5)
        return True


if __name__ == "__main__":
    import os
    import keyboard
    from screen import Screen
    from template_finder import TemplateFinder
    from old_pather import OldPather
    keyboard.add_hotkey('f12', lambda: Logger.info('Force Exit (f12)') or os._exit(1))
    keyboard.wait("f11")
    from config import Config
    from ui import UiManager
    from obs import ObsRecorder
    config = Config()
    obs_recorder = ObsRecorder(config)
    screen = Screen()
    t_finder = TemplateFinder(screen)
    old_pather = OldPather(screen, t_finder)
    ui_manager = UiManager(screen, t_finder, obs_recorder)
    char = NovaSorc(config.nova_sorc, config.char, screen, t_finder, ui_manager, old_pather)
    char.kill_council()
