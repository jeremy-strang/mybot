import keyboard
from utils.custom_mouse import mouse
from char import IChar
from template_finder import TemplateFinder
from ui import UiManager
from logger import Logger
from screen import Screen
from utils.misc import wait, rotate_vec, unit_vector
import random
from typing import Tuple, Union, List
from pather import Location, Pather
import numpy as np
import time
from utils.misc import cut_roi, is_in_roi
import os
import math

from api.mapassist import MapAssistApi
from pathing.pather_v2 import PatherV2
from state_monitor import StateMonitor
from obs import ObsRecorder

class Necro(IChar):
    def __init__(self, skill_hotkeys: dict, screen: Screen, template_finder: TemplateFinder, ui_manager: UiManager, api: MapAssistApi, obs_recorder: ObsRecorder, pather: Pather, pather_v2: PatherV2):
        os.system('color')
        Logger.info("\033[94m<<Setting up Necro>>\033[0m")
        super().__init__(skill_hotkeys, screen, template_finder, ui_manager, api, obs_recorder)
        self._pather = pather
        self._pather_v2 = pather_v2
        #custom necro pathing for pindle
        self._pather.adapt_path((Location.A5_PINDLE_START, Location.A5_PINDLE_SAFE_DIST), [100,101])
        self._pather.adapt_path((Location.A5_PINDLE_SAFE_DIST, Location.A5_PINDLE_END), [104])
        #minor offsets to pindle fight locations
        self._pather.offset_node(102, [15, 0])
        self._pather.offset_node(103, [15, 0])
        self._pather.offset_node(101, [100,-5])

        self._shenk_dead = 0
        self._skeletons_count=0
        self._mages_count=0
        self._golem_count="none"
        self._revive_count=0

    def get_cast_frames(self):
        fcr = self.get_fcr()
        frames = 15
        if fcr >= 125: frames = 9
        if fcr >= 75: frames = 10
        elif fcr >= 48: frames = 11
        elif fcr >= 30: frames = 12
        elif fcr >= 18: frames = 13
        elif fcr >= 9: frames = 14
        return frames
        

    def _check_shenk_death(self):
        ''' make sure shenk is dead checking for fireballs so we can exit combat sooner '''

        roi = [640,0,640,720]
        img = self._screen.grab()

        template_match = self._template_finder.search(
            ['SHENK_DEATH_1','SHENK_DEATH_2','SHENK_DEATH_3','SHENK_DEATH_4'],
            img,
            threshold=0.6,
            roi=roi,
            use_grayscale = False
        )
        if template_match.valid:
            self._shenk_dead=1
            Logger.info('\33[31m'+"Shenks Dead, looting..."+'\033[0m')
        else:
            return True

    def _count_revives(self):
        roi = [15,14,400,45]
        img = self._screen.grab()
        max_rev = 13

        template_match = self._template_finder.search(
            ['REV_BASE'],
            img,
            threshold=0.6,
            roi=roi
        )
        if template_match.valid:
            self._revive_count=max_rev
        else:
            self._revive_count=0
            return True

        for count in range(1,max_rev):
            rev_num = "REV_"+str(count)
            template_match = self._template_finder.search(
                [rev_num],
                img,
                threshold=0.66,
                roi=roi,
                use_grayscale = False
            )
            if template_match.valid:
                self._revive_count=count

    def _count_skeletons(self):
        roi = [15,14,400,45]
        img = self._screen.grab()
        max_skeles = 13

        template_match = self._template_finder.search(
            ['SKELE_BASE'],
            img,
            threshold=0.6,
            roi=roi
        )
        if template_match.valid:
            self._skeletons_count=max_skeles
        else:
            self._skeletons_count=0
            return True

        for count in range(1,max_skeles):
            skele_num = "SKELE_"+str(count)
            template_match = self._template_finder.search(
                [skele_num],
                img,
                threshold=0.66,
                roi=roi,
                use_grayscale = False
            )
            if template_match.valid:
                self._skeletons_count=count

    def _count_gol(self):
        roi = [15,14,400,45]
        img = self._screen.grab()

        template_match = self._template_finder.search(
            ['CLAY'],
            img,
            threshold=0.6,
            roi=roi
        )
        if template_match.valid:
            self._golem_count="clay gol"
        else:
            self._golem_count="none"
            return True

    def _summon_count(self):
        ''' see how many summons and which golem are out '''

        self._count_skeletons()
        self._count_revives()
        self._count_gol()
    def _summon_stat(self):
        ''' print counts for summons '''
        Logger.info('\33[31m'+"Summon status | "+str(self._skeletons_count)+"skele | "+str(self._revive_count)+" rev | "+self._golem_count+" |"+'\033[0m')

    def _revive(self, cast_pos_abs: Tuple[float, float], spray: int = 10, cast_count: int=12):
        Logger.info('\033[94m'+"raise revive"+'\033[0m')
        keyboard.send(self._char_config["stand_still"], do_release=False)
        for _ in range(cast_count):
            if self._skill_hotkeys["raise_revive"]:
                keyboard.send(self._skill_hotkeys["raise_revive"])
                #Logger.info("revive -> cast")
            x = cast_pos_abs[0] + (random.random() * 2*spray - spray)
            y = cast_pos_abs[1] + (random.random() * 2*spray - spray)
            cast_pos_monitor = self._screen.convert_abs_to_monitor((x, y))

            nx = cast_pos_monitor[0]
            ny = cast_pos_monitor[1]
            if(nx>1280):
                nx=1275
            if(ny>720):
                ny=715
            if(nx<0):
                nx=0
            if(ny<0):
                ny=0
            clamp = [nx,ny]

            mouse.move(*clamp)
            mouse.press(button="right")
            wait(0.075, 0.1)
            mouse.release(button="right")
        keyboard.send(self._char_config["stand_still"], do_press=False)

    def _raise_skeleton(self, cast_pos_abs: Tuple[float, float], spray: int = 10, cast_count: int=16):
        Logger.info('\033[94m'+"raise skeleton"+'\033[0m')
        keyboard.send(self._char_config["stand_still"], do_release=False)
        for _ in range(cast_count):
            if self._skill_hotkeys["raise_skeleton"]:
                keyboard.send(self._skill_hotkeys["raise_skeleton"])
                #Logger.info("raise skeleton -> cast")
            x = cast_pos_abs[0] + (random.random() * 2*spray - spray)
            y = cast_pos_abs[1] + (random.random() * 2*spray - spray)
            cast_pos_monitor = self._screen.convert_abs_to_monitor((x, y))

            nx = cast_pos_monitor[0]
            ny = cast_pos_monitor[1]
            if(nx>1280):
                nx=1279
            if(ny>720):
                ny=719
            if(nx<0):
                nx=0
            if(ny<0):
                ny=0
            clamp = [nx,ny]

            mouse.move(*clamp)
            mouse.press(button="right")
            wait(0.02, 0.05)
            mouse.release(button="right")
        keyboard.send(self._char_config["stand_still"], do_press=False)

    def _raise_mage(self, cast_pos_abs: Tuple[float, float], spray: int = 10, cast_count: int=16):
        Logger.info('\033[94m'+"raise mage"+'\033[0m')
        keyboard.send(self._char_config["stand_still"], do_release=False)
        for _ in range(cast_count):
            if self._skill_hotkeys["raise_mage"]:
                keyboard.send(self._skill_hotkeys["raise_mage"])
                #Logger.info("raise skeleton -> cast")
            x = cast_pos_abs[0] + (random.random() * 2*spray - spray)
            y = cast_pos_abs[1] + (random.random() * 2*spray - spray)
            cast_pos_monitor = self._screen.convert_abs_to_monitor((x, y))

            nx = cast_pos_monitor[0]
            ny = cast_pos_monitor[1]
            if(nx>1280):
                nx=1279
            if(ny>720):
                ny=719
            if(nx<0):
                nx=0
            if(ny<0):
                ny=0
            clamp = [nx,ny]

            mouse.move(*clamp)
            mouse.press(button="right")
            wait(0.02, 0.05)
            mouse.release(button="right")
        keyboard.send(self._char_config["stand_still"], do_press=False)


    def pre_buff(self, switch_back=True):
        #only CTA if pre trav
        if self._char_config["cta_available"]:
            self._pre_buff_cta()
            self._bone_armor()
            wait(.02, .08)
            self._clay_golem()
            wait(.02, .08)
        if self._shenk_dead==1:
            Logger.info("trav buff?")
            #self._heart_of_wolverine()
        Logger.info("prebuff/cta")

    def _clay_golem(self):
        Logger.info('\033[94m'+"cast ~> clay golem"+'\033[0m')
        keyboard.send(self._skill_hotkeys["clay_golem"])
        wait(0.05, 0.2)
        mouse.click(button="right")
        wait(self._cast_duration)


    def bone_armor(self):
        if self._skill_hotkeys["bone_armor"]:
            keyboard.send(self._skill_hotkeys["bone_armor"])
            wait(0.04, 0.1)
            mouse.click(button="right")
            wait(self._cast_duration)
        if self._skill_hotkeys["clay_golem"]:
            keyboard.send(self._skill_hotkeys["clay_golem"])
            wait(0.04, 0.1)
            mouse.click(button="right")
            wait(self._cast_duration)

    def _bone_armor(self):
        if self._skill_hotkeys["bone_armor"]:
            keyboard.send(self._skill_hotkeys["bone_armor"])
            wait(0.04, 0.1)
            mouse.click(button="right")
            wait(self._cast_duration)



    def _left_attack(self, cast_pos_abs: Tuple[float, float], spray: int = 10):
        keyboard.send(self._char_config["stand_still"], do_release=False)
        if self._skill_hotkeys["skill_left"]:
            keyboard.send(self._skill_hotkeys["skill_left"])
        for _ in range(10):
            x = cast_pos_abs[0] + (random.random() * 2*spray - spray)
            y = cast_pos_abs[1] + (random.random() * 2*spray - spray)
            cast_pos_monitor = self._screen.convert_abs_to_monitor((x, y))
            mouse.move(*cast_pos_monitor)
            mouse.press(button="left")
            wait(0.25, 0.3)
            mouse.release(button="left")

        keyboard.send(self._char_config["stand_still"], do_press=False)

    def _left_attack_single(self, cast_pos_abs: Tuple[float, float], spray: int = 10, cast_count: int=6):
        keyboard.send(self._char_config["stand_still"], do_release=False)
        if self._skill_hotkeys["skill_left"]:
            keyboard.send(self._skill_hotkeys["skill_left"])
        for _ in range(cast_count):
            x = cast_pos_abs[0] + (random.random() * 2*spray - spray)
            y = cast_pos_abs[1] + (random.random() * 2*spray - spray)
            cast_pos_monitor = self._screen.convert_abs_to_monitor((x, y))
            mouse.move(*cast_pos_monitor)
            mouse.press(button="left")
            wait(0.25, 0.3)
            mouse.release(button="left")

        keyboard.send(self._char_config["stand_still"], do_press=False)

    def _amp_dmg(self, cast_pos_abs: Tuple[float, float], spray: float = 10):
        if self._skill_hotkeys["amp_dmg"]:
            keyboard.send(self._skill_hotkeys["amp_dmg"])

        x = cast_pos_abs[0] + (random.random() * 2*spray - spray)
        y = cast_pos_abs[1] + (random.random() * 2*spray - spray)
        cast_pos_monitor = self._screen.convert_abs_to_monitor((x, y))
        mouse.move(*cast_pos_monitor)
        mouse.press(button="right")
        wait(0.25, 0.35)
        mouse.release(button="right")

    def _corpse_explosion(self, cast_pos_abs: Tuple[float, float], spray: int = 10,cast_count: int = 8):
        keyboard.send(self._char_config["stand_still"], do_release=False)
        Logger.info('\033[93m'+"corpse explosion~> random cast"+'\033[0m')
        for _ in range(cast_count):
            if self._skill_hotkeys["corpse_explosion"]:
                keyboard.send(self._skill_hotkeys["corpse_explosion"])
                x = cast_pos_abs[0] + (random.random() * 2*spray - spray)
                y = cast_pos_abs[1] + (random.random() * 2*spray - spray)
                cast_pos_monitor = self._screen.convert_abs_to_monitor((x, y))
                mouse.move(*cast_pos_monitor)
                mouse.press(button="right")
                wait(0.075, 0.1)
                mouse.release(button="right")
        keyboard.send(self._char_config["stand_still"], do_press=False)


    def _lerp(self,a: float,b: float, f:float):
        return a + f * (b - a)

    def _cast_circle(self, cast_dir: Tuple[float,float],cast_start_angle: float=0.0, cast_end_angle: float=90.0,cast_div: int = 10,cast_v_div: int=4,cast_spell: str='raise_skeleton',delay: float=1.0,offset: float=1.0):
        Logger.info('\033[93m'+"circle cast ~>"+cast_spell+'\033[0m')
        keyboard.send(self._char_config["stand_still"], do_release=False)
        keyboard.send(self._skill_hotkeys[cast_spell])
        mouse.press(button="right")

        for i in range(cast_div):
            angle = self._lerp(cast_start_angle,cast_end_angle,float(i)/cast_div)
            target = unit_vector(rotate_vec(cast_dir, angle))
            #Logger.info("current angle ~> "+str(angle))
            for j in range(cast_v_div):
                circle_pos_screen = self._pather._adjust_abs_range_to_screen((target*120.0*float(j+1.0))*offset)
                circle_pos_monitor = self._screen.convert_abs_to_monitor(circle_pos_screen)
                mouse.move(*circle_pos_monitor,delay_factor=[0.3*delay, .6*delay])


                #Logger.info("circle move")
        mouse.release(button="right")
        keyboard.send(self._char_config["stand_still"], do_press=False)


    def kill_council(self, game_state: StateMonitor) -> bool:
        odist = 999999
        while odist > 10:
            if game_state._ready is True:
                target_pos = game_state._target_pos
                tele_pos_abs = self._pather._adjust_abs_range_to_screen([target_pos[0],target_pos[1]])
                pos_m = self._screen.convert_abs_to_monitor(tele_pos_abs)
                self.pre_move()
                try:
                    self.move(pos_m,force_move=True)
                except:
                    Logger.error("Something went wrong with movement...")
                    pass
                odist = math.dist([game_state._player_x,game_state._player_y],[game_state._area_pos[0],game_state._area_pos[1]])
        
        self._kill_mobs(["CouncilMember"], game_state,kite=True,kite_dist=.25)
        return True


    def kill_baal(self, game_state: StateMonitor) -> bool:

        self._kill_mobs(["BaalCrab"], game_state)
        return True


    def kill_meph(self, game_state: StateMonitor) -> bool:

        odist = 999999
        while odist > 10:
            if game_state._ready is True:
                target_pos = game_state._target_pos
                tele_pos_abs = self._pather._adjust_abs_range_to_screen([target_pos[0],target_pos[1]])
                pos_m = self._screen.convert_abs_to_monitor(tele_pos_abs)
                self.pre_move()
                try:
                    self.move(pos_m)
                except:
                    Logger.error("Something went wrong with movement...")
                    pass
                odist = math.dist([game_state._player_x,game_state._player_y],[game_state._area_pos[0],game_state._area_pos[1]])
        self._kill_mobs(["Mephisto"], game_state)
        return True

    def kill_tower(self, game_state: StateMonitor) -> bool:
        #use unique id for now
        self._kill_mobs(["DarkStalker"], game_state)
        return True


    def kill_andy(self, game_state: StateMonitor) -> bool:
        odist = 999999
        while odist > 10:
            if game_state._ready is True:
                target_pos = game_state._target_pos
                tele_pos_abs = self._pather._adjust_abs_range_to_screen([target_pos[0],target_pos[1]])
                pos_m = self._screen.convert_abs_to_monitor(tele_pos_abs)
                self.pre_move()
                try:
                    self.move(pos_m)
                except:
                    Logger.error("Something went wrong with movement...")
                    pass
                odist = math.dist([game_state._player_x,game_state._player_y],[game_state._area_pos[0],game_state._area_pos[1]])
        
        self._kill_mobs(["Andariel"], game_state)
        return True


    def kill_pindle_mem(self, game_state: StateMonitor) -> bool:
        #use unique id for now
        self._cast_circle(cast_dir=[-1,1],cast_start_angle=0,cast_end_angle=360,cast_div=32,cast_v_div=2,cast_spell='raise_skeleton',offset=2,delay=1.6)
        
        #self._pather.traverse_nodes([102,103], self)
        #self._pather_v2.traverse()
        self._pather_v2.traverse([58,44], self)

        odist = 999999
        while odist > 30:
            if game_state._ready is True:
                target_pos = game_state._target_pos
                tele_pos_abs = self._pather._adjust_abs_range_to_screen([target_pos[0],target_pos[1]])
                pos_m = self._screen.convert_abs_to_monitor(tele_pos_abs)
                self.pre_move()
                try:
                    self.move(pos_m)
                except:
                    Logger.error("Something went wrong with movement...")
                    pass
                odist = math.dist([game_state._player_x,game_state._player_y],[game_state._area_pos[0],game_state._area_pos[1]])

        self._kill_mobs(["DefiledWarrior"], game_state)
        return True

    def kill_eldrich_mem(self, game_state: StateMonitor) -> bool:
        #use unique id for now
        #self._cast_circle(cast_dir=[-1,1],cast_start_angle=0,cast_end_angle=360,cast_div=32,cast_v_div=2,cast_spell='raise_skeleton',offset=2,delay=1.6)

        odist = 999999
        while odist > 20:
            if game_state._ready is True:
                target_pos = game_state._target_pos
                tele_pos_abs = self._pather._adjust_abs_range_to_screen([target_pos[0],target_pos[1]])
                pos_m = self._screen.convert_abs_to_monitor(tele_pos_abs)
                self.pre_move()
                try:
                    self.move(pos_m)
                except:
                    Logger.error("Something went wrong with movement...")
                    pass
                odist = math.dist([game_state._player_x,game_state._player_y],[game_state._area_pos[0],game_state._area_pos[1]])


        wait(self._cast_duration, self._cast_duration +.2)
        self._kill_mobs(["SiegeBoss"], game_state)

        for _ in range(4):
            self._raise_skeleton([-50,-90],160,cast_count=2)
            #disable revives for now
            self._revive([-50,-90],160,cast_count=4)

        return True


    def kill_shenk_mem(self, game_state: StateMonitor) -> bool:

        #if game_state._ready is True:
            #self._pather_v2.traverse(game_state._area_pos, self)

        wait(self._cast_duration, self._cast_duration +.2)
        self._kill_mobs(["SiegeBoss"], game_state,kite=True)

        for _ in range(4):
            self._raise_skeleton([-50,-90],160,cast_count=2)
            #disable revives for now
            self._revive([-50,-90],160,cast_count=4)
        return True

    # Memory reading
    # ===================================
    
    def _kill_mobs(self, names: list[str], game_state:StateMonitor, kite:bool = False,kite_dist:float = .25) -> bool:
        ct = 0

        #loop till our boss death
        pos_m = self._screen.convert_abs_to_monitor((0, 120))
        mouse.move(*pos_m)
        mouse.click('left')
        wait(.05,.1)
        mouse.click('left')
        pos_m = self._screen.convert_abs_to_monitor((0, 120))
        mouse.move(*pos_m)
        mouse.click('left')
        wait(.05,.1)
        mouse.click('left')



        i = 0 
        amp = 0 
        while game_state._dead == 0:
            i+=1
            if i > 100:
                return False
            if game_state._ready is True:
                target_pos = game_state._target_pos
                target_pos = [target_pos[0]-9.5,target_pos[1]-39.5]                    
                if amp == 0:
                    wait(.05,.1)
                    self._amp_dmg(target_pos, 11)
                    amp = 1
                self._corpse_explosion(target_pos,40,cast_count=2)
                self._left_attack_single(target_pos, 11, cast_count=2)

                #move around
                if kite:
                    #rot_deg = random.randint(-2,2)
                    #tele_pos_abs = unit_vector(rotate_vec(target_pos, rot_deg)) * 320*kite_dist
                    #tele_pos_abs = self._pather._adjust_abs_range_to_screen([tele_pos_abs[0],tele_pos_abs[1]])
                    #pos_m = self._screen.convert_abs_to_monitor(target_pos)
                    #self.pre_move()
                    #try:
                    #self.move(pos_m, force_move=True)
                    try:
                        self._pather_v2.traverse(game_state._area_pos, self)
                        wait(.05,.1)
                        self._amp_dmg(target_pos, 11)
                        pos_m = self._screen.convert_abs_to_monitor((0, 20))
                        mouse.move(*pos_m)
                        mouse.click('left')
                        wait(.05,.1)
                        mouse.click('left')
                        pos_m = self._screen.convert_abs_to_monitor((0, 20))
                        mouse.move(*pos_m)
                        mouse.click('left')
                        wait(.05,.1)
                        mouse.click('left')
                    except:
                        pass
                        #self.move(pos_m)
                    #except:
                        #Logger.error("Something went wrong with movement...")

        self._pather_v2.traverse(game_state._area_pos, self)

if __name__ == "__main__":
    import os
    import keyboard
    keyboard.add_hotkey('f12', lambda: Logger.info('Force Exit (f12)') or os._exit(1))
    keyboard.wait("f11")
    from config import Config
    from char import Necro
    from ui import UiManager
    from obs import ObsRecorder
    config = Config()
    obs_recorder = ObsRecorder(config)
    screen = Screen()
    t_finder = TemplateFinder(screen)
    pather = Pather(screen, t_finder)
    ui_manager = UiManager(screen, t_finder, obs_recorder)
    char = Necro(config.necro, config.char, screen, t_finder, ui_manager, pather)
