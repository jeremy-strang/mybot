import keyboard
from char.sorceress import Sorceress
from utils.custom_mouse import mouse
from logger import Logger
from utils.misc import wait, rotate_vec, unit_vector
import random
from pathing import Location
import numpy as np
from logger import Logger
from config import Config
from screen import Screen
from template_finder import TemplateFinder
from ui import UiManager
from pathing import OldPather, Location

from d2r.d2r_api import D2rApi
from pathing import Pather
from state_monitor import StateMonitor
from obs import ObsRecorder, obs_recorder

class LightSorc(Sorceress):
    def __init__(self, *args, **kwargs):
        Logger.info("Setting up Light Sorc")
        super().__init__(*args, **kwargs)

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

    def _chain_lightning(self, cast_pos_abs: tuple[float, float], delay: tuple[float, float] = (0.1, 0.2), spray: int = 10):
        keyboard.send(self._char_config["stand_still"], do_release=False)
        if self._skill_hotkeys["chain_lightning"]:
            keyboard.send(self._skill_hotkeys["chain_lightning"])
        for _ in range(2):
            x = cast_pos_abs[0] + (random.random() * 2 * spray - spray)
            y = cast_pos_abs[1] + (random.random() * 2 * spray - spray)
            pos_m = self._screen.convert_abs_to_monitor((x, y))
            mouse.move(*pos_m, delay_factor=[0.3*.5, 0.6*.5])
            mouse.press(button="left")
            wait(delay[0], delay[1])
            mouse.release(button="left")
        keyboard.send(self._char_config["stand_still"], do_press=False)

    def _lightning(self, cast_pos_abs: tuple[float, float], delay: tuple[float, float] = (0.1, 0.2), spray: float = 10):
        if not self._skill_hotkeys["lightning"]:
            raise ValueError("You did not set lightning hotkey!")
        keyboard.send(self._skill_hotkeys["lightning"])
        for _ in range(4):
            x = cast_pos_abs[0] + (random.random() * 2 * spray - spray)
            y = cast_pos_abs[1] + (random.random() * 2 * spray - spray)
            cast_pos_monitor = self._screen.convert_abs_to_monitor((x, y))
            mouse.move(*cast_pos_monitor, delay_factor=[0.3*.5, 0.6*.5])
            mouse.press(button="right")
            wait(delay[0], delay[1])
            mouse.release(button="right")

    def _frozen_orb(self, cast_pos_abs: tuple[float, float], delay: tuple[float, float] = (0.1, 0.2), spray: float = 10):
        if self._skill_hotkeys["frozen_orb"]:
            keyboard.send(self._skill_hotkeys["frozen_orb"])
            for _ in range(1):
                x = cast_pos_abs[0] + (random.random() * 2 * spray - spray)
                y = cast_pos_abs[1] + (random.random() * 2 * spray - spray)
                cast_pos_monitor = self._screen.convert_abs_to_monitor((x, y))
                mouse.move(*cast_pos_monitor)
                mouse.press(button="right")
                wait(delay[0], delay[1])
                mouse.release(button="right")

    def kill_pindleskin(self) -> bool:
        pindle_pos_abs = self._screen.convert_screen_to_abs(self._config.path["pindle_end"][0])
        cast_pos_abs = [pindle_pos_abs[0] * 0.9, pindle_pos_abs[1] * 0.9]
        for _ in range(int(self._char_config["atk_len_pindle"])):
            self._chain_lightning(cast_pos_abs, spray=11)
        self._lightning(cast_pos_abs, spray=11)
        wait(self._cast_duration, self._cast_duration + 0.2)
        # Move to items
        self._old_pather.traverse_nodes_fixed("pindle_end", self)
        return True

    def kill_eldritch(self) -> bool:
        eld_pos_abs = self._screen.convert_screen_to_abs(self._config.path["eldritch_end"][0])
        cast_pos_abs = [eld_pos_abs[0] * 0.9, eld_pos_abs[1] * 0.9]
        for _ in range(int(self._char_config["atk_len_eldritch"])):
            self._chain_lightning(cast_pos_abs, spray=90)
        self._lightning(cast_pos_abs, spray=50)
        # Move to items
        wait(self._cast_duration, self._cast_duration + 0.2)
        self._old_pather.traverse_nodes_fixed("eldritch_end", self)
        return True

    def kill_shenk(self) -> bool:
        shenk_pos_abs = self._old_pather.find_abs_node_pos(149, self._screen.grab())
        if shenk_pos_abs is None:
            shenk_pos_abs = self._screen.convert_screen_to_abs(self._config.path["shenk_end"][0])
        cast_pos_abs = [shenk_pos_abs[0] * 0.9, shenk_pos_abs[1] * 0.9]
        for _ in range(int(self._char_config["atk_len_shenk"] * 0.5)):
            self._chain_lightning(cast_pos_abs, spray=90)
        pos_m = self._screen.convert_abs_to_monitor((150, 50))
        self.pre_move()
        self.move(pos_m, force_move=True)
        shenk_pos_abs = self._screen.convert_screen_to_abs(self._config.path["shenk_end"][0])
        cast_pos_abs = [shenk_pos_abs[0] * 0.9, shenk_pos_abs[1] * 0.9]
        for _ in range(int(self._char_config["atk_len_shenk"] * 0.5)):
            self._chain_lightning(cast_pos_abs, spray=90)
        self._lightning(cast_pos_abs, spray=60)
        pos_m = self._screen.convert_abs_to_monitor((150, 50))
        self.pre_move()
        self.move(pos_m, force_move=True)
        shenk_pos_abs = self._screen.convert_screen_to_abs(self._config.path["shenk_end"][0])
        cast_pos_abs = [shenk_pos_abs[0] * 0.9, shenk_pos_abs[1] * 0.9]
        for _ in range(int(self._char_config["atk_len_shenk"])):
            self._chain_lightning(cast_pos_abs, spray=90)
        self._lightning(cast_pos_abs, spray=60)
        self.pre_move()
        self.move(pos_m, force_move=True)
        # Move to items
        wait(self._cast_duration, self._cast_duration + 0.2)
        self._old_pather.traverse_nodes((Location.A5_SHENK_SAFE_DIST, Location.A5_SHENK_END), self, time_out=1.4, force_tp=True)
        return True

    def kill_council(self) -> bool:
        # Move inside to the right
        self._old_pather.traverse_nodes_fixed([(1110, 120)], self)
        self._old_pather.offset_node(300, (80, -110))
        self._old_pather.traverse_nodes([300], self, time_out=1.0, force_tp=True)
        self._old_pather.offset_node(300, (-80, 110))
        wait(0.5)
        self._frozen_orb((-150, -10), spray=10)
        self._lightning((-150, 0), spray=10)
        self._chain_lightning((-150, 15), spray=10)
        wait(0.5)
        pos_m = self._screen.convert_abs_to_monitor((-50, 200))
        self.pre_move()
        self.move(pos_m, force_move=True)
        wait(0.5)
        pos_m = self._screen.convert_abs_to_monitor((-550, 230))
        self.pre_move()
        self.move(pos_m, force_move=True)
        wait(0.5)
        self._old_pather.offset_node(226, (-80, 60))
        self._old_pather.traverse_nodes([226], self, time_out=1.0, force_tp=True)
        self._old_pather.offset_node(226, (80, -60))
        wait(0.5)
        self._frozen_orb((-150, -130), spray=10)
        self._chain_lightning((200, -185), spray=20)
        self._chain_lightning((-170, -150), spray=20)
        wait(0.5)
        self._old_pather.traverse_nodes_fixed([(1110, 15)], self)
        self._old_pather.traverse_nodes([300], self, time_out=1.0, force_tp=True)
        pos_m = self._screen.convert_abs_to_monitor((300, 150))
        self.pre_move()
        self.move(pos_m, force_move=True)
        wait(0.5)
        self._frozen_orb((-170, -100), spray=40)
        self._chain_lightning((-300, -100), spray=10)
        self._chain_lightning((-300, -90), spray=10)
        self._lightning((-300, -110), spray=10)
        wait(0.5)
        # Move back outside and attack
        pos_m = self._screen.convert_abs_to_monitor((-430, 230))
        self.pre_move()
        self.move(pos_m, force_move=True)
        self._old_pather.offset_node(304, (0, -80))
        self._old_pather.traverse_nodes([304], self, time_out=1.0, force_tp=True)
        self._old_pather.offset_node(304, (0, 80))
        wait(0.5)
        self._frozen_orb((175, -170), spray=40)
        self._chain_lightning((-170, -150), spray=20)
        self._chain_lightning((300, -200), spray=20)
        self._chain_lightning((-170, -150), spray=20)
        wait(0.5)
        # Move back inside and attack
        pos_m = self._screen.convert_abs_to_monitor((350, -350))
        self.pre_move()
        self.move(pos_m, force_move=True)
        pos_m = self._screen.convert_abs_to_monitor((100, -30))
        self.pre_move()
        self.move(pos_m, force_move=True)
        wait(0.5)
        # Attack sequence center
        self._frozen_orb((0, 20), spray=40)
        self._lightning((-50, 50), spray=30)
        self._lightning((50, 50), spray=30)
        wait(0.5)
        # Move inside
        pos_m = self._screen.convert_abs_to_monitor((40, -30))
        self.pre_move()
        self.move(pos_m, force_move=True)
        # Attack sequence to center
        wait(0.5)
        self._chain_lightning((-150, 100), spray=20)
        self._chain_lightning((150, 200), spray=40)
        self._chain_lightning((-150, 0), spray=20)
        wait(0.5)
        pos_m = self._screen.convert_abs_to_monitor((-200, 240))
        self.pre_move()
        self.move(pos_m, force_move=True)
        # Move outside since the trav.py expects to start searching for items there if char can teleport
        self._old_pather.traverse_nodes([226], self, time_out=2.5, force_tp=True)
        return True

    def kill_nihlathak(self, end_nodes: list[int]) -> bool:
        # Find nilhlatak position
        delay = [0.2, 0.3]
        atk_len = int(self._char_config["atk_len_nihlathak"])
        nihlathak_pos_abs = None
        for i in range(atk_len):
            nihlathak_pos_abs_next = self._old_pather.find_abs_node_pos(end_nodes[-1], self._screen.grab())

            if nihlathak_pos_abs_next is not None:
                nihlathak_pos_abs = nihlathak_pos_abs_next
            else:
                Logger.warning(f"Can't find Nihlathak next position at node {end_nodes[-1]}")
                if nihlathak_pos_abs is not None:
                    Logger.warning(f"Using previous position for attack sequence")
                    
            if nihlathak_pos_abs is not None:
                cast_pos_abs = np.array([nihlathak_pos_abs[0] * 0.9, nihlathak_pos_abs[1] * 0.9])
                self._chain_lightning(cast_pos_abs, delay, 90)
                # Do some tele "dancing" after each sequence
                if i < atk_len - 1:
                    rot_deg = random.randint(-10, 10) if i % 2 == 0 else random.randint(170, 190)
                    tele_pos_abs = unit_vector(rotate_vec(cast_pos_abs, rot_deg)) * 100
                    pos_m = self._screen.convert_abs_to_monitor(tele_pos_abs)
                    self.pre_move()
                    self.move(pos_m)
                else:
                    self._lightning(cast_pos_abs, spray=60)
            else:               
                Logger.warning(f"Casting static as the last position isn't known. Skipping attack sequence")
                self._cast_static(duration=2)

        # Move to items
        wait(self._cast_duration, self._cast_duration + 0.2)
        self._old_pather.traverse_nodes(end_nodes, self, time_out=0.8)
        return True

    def kill_summoner(self) -> bool:
        # Attack
        cast_pos_abs = np.array([0, 0])
        pos_m = self._screen.convert_abs_to_monitor((-20, 20))
        mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
        for _ in range(int(self._char_config["atk_len_arc"])):
            self._chain_lightning(cast_pos_abs, spray=11)
            self._lightning(cast_pos_abs, spray=11)
        wait(self._cast_duration, self._cast_duration + 0.2)
        return True


    def kill_baal(self, game_state: StateMonitor) -> bool:

        self._kill_mobs(["BaalCrab"], game_state)
        return True


    def kill_mephisto(self, game_state: StateMonitor) -> bool:

        odist = 999999
        while odist > 10:
            if game_state._ready is True:
                target_pos = game_state._target_pos
                tele_pos_abs = self._old_pather._adjust_abs_range_to_screen([target_pos[0],target_pos[1]])
                pos_m = self._screen.convert_abs_to_monitor(tele_pos_abs)
                self.pre_move()
                try:
                    self.move(pos_m)
                except:
                    Logger.error("Something went wrong with movement...")
                    pass
                odist = math.dist([game_state._player_x,game_state._player_y],[game_state._area_pos[0],game_state._area_pos[1]])
        self._kill_mobs(["Mephisto"], game_state,static=0,kite=True,kite_dist=.2)
        return True

    def kill_countess(self, game_state: StateMonitor) -> bool:
        #use unique id for now
        self._kill_mobs(["DarkStalker"], game_state,1,kite=True,kite_dist=.2)
        return True


    def kill_andariel(self, game_state: StateMonitor) -> bool:

        self._kill_mobs(["Andariel"], game_state,kite=True,kite_dist=.67)
        return True


    # Memory reading
    # ===================================
    
    def _kill_mobs(self, names: list[str], game_state:StateMonitor, static: int = 0, kite:bool = True,kite_dist:float = 1.0) -> bool:
        ct = 0
        casted_static = static
        #loop till our boss death
        while game_state._dead == 0:
            if game_state._ready is True:
                target_pos = game_state._target_pos

                if casted_static == 0:
                    tele_pos_abs = unit_vector(rotate_vec(target_pos, 0)) * 150
                    tele_pos_abs = self._old_pather._adjust_abs_range_to_screen([tele_pos_abs[0],tele_pos_abs[1]])
                    pos_m = self._screen.convert_abs_to_monitor(tele_pos_abs)
                    self.pre_move()
                    self.move(pos_m)
                    pos_m = self._screen.convert_abs_to_monitor(target_pos)
                    mouse.move(pos_m[0], pos_m[1], randomize=3, delay_factor=[1*0.1, 1*0.14])
                    self._cast_static(3.0)
                    casted_static=1
                    self._chain_lightning(target_pos, spray=8)

                self._cast_static(.1)
                #not sure we need chain lgt
                #self._chain_lightning(target_pos, spray=8)
                target_pos = game_state._target_pos
                self._lightning(target_pos, spray=8)
                target_pos = game_state._target_pos
                self._frozen_orb(target_pos, spray=8)

                #move around
                if kite:
                    rot_deg = random.randint(-2,2)
                    tele_pos_abs = unit_vector(rotate_vec(target_pos, rot_deg)) * 320*kite_dist
                    tele_pos_abs = self._old_pather._adjust_abs_range_to_screen([tele_pos_abs[0],tele_pos_abs[1]])
                    pos_m = self._screen.convert_abs_to_monitor(tele_pos_abs)
                    self.pre_move()
                    try:
                        self.move(pos_m)
                        self.move(pos_m)
                    except:
                        Logger.error("Something went wrong with movement...")
                        pass
