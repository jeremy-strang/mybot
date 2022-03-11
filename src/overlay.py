from obs import obs_recorder
from pathing.path_finder import cluster_nodes
import win32gui
import win32api
import win32con
import win32ui
from win32gui import FindWindow, GetWindowRect, ClientToScreen
import os
from logger import Logger
import numpy as np
from copy import deepcopy

import dearpygui.dearpygui as dpg
from dearpygui.demo import show_demo

class Overlay:

    def __init__(self,bot,stats):
        self._callback = None
        self._pausing = True
        self._do_overlay = True
        self._stats = stats
        self._bot = bot
        self._api = self._bot._api
        self._current_area = None

        self._mini_map_h =100
        self._mini_map_w =100
        
        self._draw_path=None
        self._astar_path = None

        self._texture_data = None

    def update_map(self):
        Logger.info("Updating map overlay...")

        #map_surface.fill((0,0,0))
        nodes = self._api.data['map']
        x = 0
        y = 0 
        self._texture_data=None
        self._texture_data=[]
        for node in nodes:
            for key in node:
                if key:
                    #map_surface.set_at((x,y), (66,66,66))
                    self._texture_data.append(.26)
                    self._texture_data.append(.26)
                    self._texture_data.append(.26)
                    self._texture_data.append(1.0)
                else:
                    #map_surface.set_at((x,y), (55,55,55))
                    self._texture_data.append(0.0)
                    self._texture_data.append(0.0)
                    self._texture_data.append(0.0)
                    self._texture_data.append(0.0)
                x+=1
            x=0
            y+=1
        dpg.delete_item("texture_tag")
        dpg.remove_alias("texture_tag")
        dpg.delete_item("map_node", children_only=True)
        dpg.add_static_texture(self._mini_map_w,self._mini_map_h, self._texture_data,parent="_txt", tag="texture_tag")
        dpg.draw_image("texture_tag",parent="map_node",pmin=[0,0],pmax=[self._mini_map_w,self._mini_map_h])


    def init(self):
        Logger.info("Started overlay...")
        fuchsia = (255,0,255)  # Transparency color

        dpg.create_context()

        self._texture_data = []
        for i in range(0, self._mini_map_w * self._mini_map_h):
            self._texture_data.append(0)
            self._texture_data.append(1.0)
            self._texture_data.append(0)
            self._texture_data.append(255 / 255)

        dpg.add_texture_registry(label="txt_con", tag="_txt",show=False)
        dpg.add_static_texture(self._mini_map_w,self._mini_map_h, self._texture_data,parent="_txt", tag="texture_tag")

        with dpg.window(label="stats",width=220,height=220,pos=(1060,0), tag="main",no_resize=True,no_scrollbar=True,no_title_bar=True,no_move=True,no_collapse=True):
            #dpg.draw_circle((250,250),500,color=(55,55,55,255),fill=[55,55,55],parent="main")

            with dpg.draw_node(tag="root_scale"):
                with dpg.draw_node(tag="root_node"):
                    with dpg.draw_node(tag="map_node"):
                        dpg.draw_image("texture_tag",parent="map_node",pmin=(0,0),pmax=(self._mini_map_w,self._mini_map_h))
                        print("init image")
                    with dpg.draw_node(tag="player"):
                        dpg.draw_circle((2, 2), 4, color=(255, 255, 0, 255),parent="player",tag="ppos")
                    with dpg.draw_node(tag="monsters"):
                        dpg.draw_circle((0, 0), 0, color=(255, 0, 255, 255),parent="monsters",tag="mon_root")
            with dpg.draw_node(tag="no_scale"):
                dpg.draw_text((0, 0), '0', color=(255, 55, 75, 255),size=14,parent="no_scale")


        with dpg.window(label="static entities",width=220,height=220,pos=(1060,220), tag="entities_main",no_resize=True,no_scrollbar=False,no_title_bar=False,no_move=True,no_collapse=False):
            with dpg.table(header_row=False,tag="entity_table"):
                dpg.add_table_column()
                for i in range(0, 2):
                    with dpg.table_row():
                        for j in range(0, 1):
                            dpg.add_text(f"Row{i} Column{j}")


        dpg.create_viewport(title='overlay', width=1280, height=720,decorated=False,clear_color=[255,0,255])
        dpg.setup_dearpygui()
        dpg.show_viewport()


        hwnd = FindWindow(None, "overlay")
        win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) | win32con.WS_EX_LAYERED)
        win32gui.SetLayeredWindowAttributes(hwnd, win32api.RGB(*fuchsia), 0, win32con.LWA_COLORKEY)


        d2 = FindWindow(None, "Diablo II: Resurrected")
        PyCWnd = win32ui.CreateWindowFromHandle(d2)

        mat = dpg.create_translation_matrix([0,0])
    

        while dpg.is_dearpygui_running():

            try:
                data = self._api.get_data() 
            except:
                pass

            if data is None:
                #exit early no data loaded yet
                continue 
            else:

                if str(self._current_area) not in str(data['current_area']):
                    self._current_area = str(data['current_area'])
                    self._mini_map_h = 0
                    for node in data['map']:
                        self._mini_map_h +=1
                    self._mini_map_w = np.size(data['map'][0])
                    self.update_map()

                    dpg.delete_item("entities_main", children_only=True)
                    with dpg.table(header_row=False,tag="entity_table",parent="entities_main"):
                        dpg.add_table_column()
                        dpg.add_table_column()
                        for poi in data['poi']:
                            with dpg.table_row():
                                dpg.add_text(poi['label'])
                                dpg.add_text(poi['position']-data['area_origin'])

                        for npc in data['static_npcs']:
                            with dpg.table_row():
                                dpg.add_text(npc['name'])
                                dpg.add_text(npc['position']-data['area_origin'])



            if self._current_area is not None:
                #draw txt?
                #print("current area")
                offset_w = self._mini_map_w
                offset_h = self._mini_map_h
                center = 110
                px = data['player_pos_area'][0]+data['player_offset'][0]
                py = data['player_pos_area'][1]+data['player_offset'][1]

                dpg.apply_transform("map_node", dpg.create_translation_matrix([0,0]))
                dpg.apply_transform("player", dpg.create_translation_matrix([px,py]))
                dpg.apply_transform("root_node", dpg.create_translation_matrix([-px+center,-py+center]))
                
                #dpg.apply_transform("root_node", dpg.create_scale_matrix([1.2,1.2]))

                dpg.delete_item("monsters", children_only=True)
                dpg.delete_item("no_scale", children_only=True)

                dpg.draw_text((0, 0), data['player_pos_area'], color=(255, 82, 255, 255),size=12,parent="no_scale")
                dpg.draw_text((0, 18), data['player_pos_world'], color=(255, 82, 255, 255),size=12,parent="no_scale")

                self._astar_path = self._api._astar_current_path
                self._draw_path = self._api._current_path

                if self._draw_path is not None:
                    for node in self._draw_path:
                        #these are flipped, unfortunate ha
                        x = node[0]
                        y = node[1]
                        #pygame.draw.rect(map_surface, (0,0,255), pygame.Rect(x,y, 2,2))
                        dpg.draw_circle((1+x, 1+y), 2, color=(0, 0, 255, 255),parent="monsters")

                px = 0 
                py = 0
                if self._astar_path is not None:
                    for node in self._astar_path:
                        #these are flipped, unfortunate ha

                        x = node[1]+1.5
                        y = node[0]+1.5
                        dpg.draw_circle((x, y), 3, color=(255, 0, 0, 255),parent="monsters")
                        #pygame.draw.rect(map_surface, (0,255,0), pygame.Rect(x,y, 9,9))
                        if px>0 and py>0:
                            dpg.draw_line((px, py), (x, y), color=(255, 255, 0, 255), thickness=0.05,parent="monsters")
                        px=x
                        py=y

                for npc in data['static_npcs']:
                    local = npc['position']-data["area_origin"]
                    #print(local)
                    x = local[0]
                    y = local[1]
                    name = str(npc['name'])
                    dpg.draw_circle((1+x, 1+y), 2, color=(0, 255, 255, 255),parent="monsters")
                    dpg.draw_text((1+x, 1+y), name, color=(111, 222, 255, 255),size=12,parent="monsters")

                for poi in data['poi']:
                    local = poi['position']-data["area_origin"]
                    #print(local)
                    x = local[0]
                    y = local[1]
                    name = str(poi['label'])
                    dpg.draw_circle((1+x, 1+y), 2, color=(0, 255, 255, 255),parent="monsters")
                    dpg.draw_text((1+x, 1+y), name, color=(255, 255, 0, 255),size=12,parent="monsters")

                for mob in data['monsters']:
                    #print(mob)
                    local = mob['position']-data["area_origin"]
                    #print(local)
                    x = local[0]
                    y = local[1]
                    #print(mob)
                    if mob['mode'] == 1:
                        #aware of you/activly pathing
                        #pygame.draw.rect(map_surface, (10,90,10), pygame.Rect(x, y, 3,3))
                        dpg.draw_circle((1+x, 1+y), 2, color=(120, 90, 10, 255),parent="monsters")
                    if mob['mode'] == 0:
                        #attacking??
                        #pygame.draw.rect(map_surface, (90,10,10), pygame.Rect(x, y, 3,3))
                        dpg.draw_circle((1+x, 1+y), 2, color=(90, 10, 190, 255),parent="monsters")
                    if mob['mode'] == 2:
                        #?
                        #pygame.draw.rect(map_surface, (0,255,255), pygame.Rect(x, y, 3,3))
                        dpg.draw_circle((1+x, 1+y), 2, color=(25, 70, 255, 255),parent="monsters")
                    if mob['mode'] == 12 and mob['is_targetable_corpse']:
                        #dead
                        #pygame.draw.rect(map_surface, (255,255,255), pygame.Rect(x, y, 3,3))
                        dpg.draw_circle((1+x, 1+y), 2, color=(255, 255, 255, 255),parent="monsters")
                
                for node in cluster_nodes(data["map"]):
                    x = node[0]
                    y = node[1]
                    #pygame.draw.rect(map_surface, (0,0,255), pygame.Rect(x,y, 2,2))
                    dpg.draw_circle((1+x, 1+y), 2, color=(0, 0, 255, 255),parent="monsters")
                
                dpg.apply_transform("root_scale", dpg.create_scale_matrix([2,2])*dpg.create_translation_matrix([-center/2,-center/2]))

                pass

            xx0,yy0,xx1,yy1   = GetWindowRect(d2)
            x0,y0,x1,y1 = win32gui.GetClientRect(d2)
            w = x1-x0
            h = y1-y0
            tl = ClientToScreen(d2,(x0,y0))
            rb = ClientToScreen(d2,(x1,y1))

            left_border = tl[0]-xx0
            right_border = xx1-rb[0]
            bottom_border = yy1-rb[1]
            top_border = tl[1]-yy0

            win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, xx0+left_border,yy0+top_border, int(w), int(h), win32con.SWP_NOSIZE)
            dpg.render_dearpygui_frame()
        dpg.destroy_context()

        
    def stop_overlay(self):
        dpg.stop_dearpygui()
        dpg.destroy_context()
        #os.exit(1)
        self._do_overlay = False

    def set_callback(self, callback):
        self._callback = callback

    def display(self):
        print("display gui")

def stop():
    dpg.stop_dearpygui()
    dpg.destroy_context()
    sys.exit(1)


if __name__ == "__main__":
    import keyboard
    import os
    import sys
    keyboard.add_hotkey('f12', lambda: stop())
    keyboard.wait("f11")
    from bot import Bot
    from config import Config
    from game_stats import GameStats
    from pathing.pather_v2 import PatherV2
    from api import MapAssistApi
    import threading
    from template_finder import TemplateFinder
    from ui import UiManager, char_selector
    from char.sorceress import LightSorc, BlizzSorc, NovaSorc
    from screen import Screen
    from pather import Location, Pather
    from dearpygui.dearpygui import *
    from obs import ObsRecorder

    config = Config()
    obs_recorder = ObsRecorder(config)
    screen = Screen()
    game_stats = GameStats()

    api = MapAssistApi()
    api_thread = threading.Thread(target=api.start)
    api_thread.daemon = False
    api_thread.start()
    #mapassist api + new pather
    game_stats = GameStats() 
    template_finder = TemplateFinder(screen)
    ui_manager = UiManager(screen, template_finder, obs_recorder, game_stats)
    pather = Pather(screen, template_finder)

    bot = Bot(screen, game_stats, template_finder ,api)
    self = bot._andy


    pather_v2 = PatherV2(screen, api)

    char = LightSorc(config.light_sorc, screen, template_finder, ui_manager, pather,pather_v2,api)
    char.discover_capabilities()

    overlay = Overlay(bot,game_stats)
    overlay.init()

    while 1:
        data = self._api.get_data()
        if data is not None:
            print(data["player_pos_area"])
            #for obj in data['static_npcs']:
            #    print(obj)
        print("-----")
        time.sleep(0.5)
