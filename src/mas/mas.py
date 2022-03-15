'''
this runs map assist from compiled dlls
'''
import configparser
import os
import clr
import numpy as np
from requests.exceptions import ConnectionError
import math
from .world_to_abs import world_to_abs

from threading import Thread

clr.AddReference(os.path.abspath(r'MapAssistApi/bin/x64/Release/MapAssist.dll'))

from MapAssist.Botty import ApiHost
from System import Action
from System import String
from System import Object
from System.Collections.Generic import Dictionary


class MAS(Thread):
    def __init__(self, callback, custom_files=[]):
        super(MAS, self).__init__()
        self.daemon = True
        self._pg = None
        self._pg_main = None
        self._pg=None
        self._data=None
        self._player_pos=None
        self._callback = callback
        self._custom_files = custom_files

    def update(self):
        pass

    @staticmethod
    def _append_file(config, fileName: str):
        p = configparser.ConfigParser()
        p.read(fileName)
        for section in p.sections():
            for key in p[section]:
                if(not config.ContainsKey(section)):
                    config[section] = Dictionary[String, Object]()
                config[section][key] = p[section][key]

    def _convert_config(self):
        config = Dictionary[String, Dictionary[String, Object]]()
        MAS._append_file(config, "./config/params.ini")
        MAS._append_file(config, "./config/pickit.ini")
        if self._custom_files is not None and type(self._custom_files) is list:
            for f in self._custom_files:
                MAS._append_file(config, f)
        return config

    def run(self):
        ApiHost.Run(self._convert_config(), Action[String](self._callback))


    def cancel(self):
        ApiHost.Stop()

    def delta_world_to_minimap(self,delta, diag, scale, deltaZ = 0.0):
        camera_angle = -26.0 * 3.14159274 / 180.0
        cos = (diag * math.cos(camera_angle) / scale)
        sin = (diag * math.sin(camera_angle) / scale)
        d = ((delta[0] - delta[1]) * cos, deltaZ - (delta[0] + delta[1]) * sin)
        return d

    def world_to_abs(self, dest):
        w = 1280
        h = 720 
        player = self._player_pos
        screen_center = (w / 2.0, h / 2.0)
        delta =  self.delta_world_to_minimap(dest-player,math.sqrt(w*w + h*h), 68.5, 30)
        screen_coords = (delta[0], delta[1])
        return screen_coords

    def get_data(self, data) -> dict:
        _data = {
            "monsters": [],
            "mercs": [],
            "poi": [],
            "objects": [],
            "items": [],
            "static_npcs": [],
            "map": None,
            "player_pos_world": None,
            "player_pos_area": None,
            "area_origin": None,
            "current_area": None,
            "used_skill": None,
            "right_skill": None,
            "left_skill": None,
            "menus": None,
            "player_health": 0.0,
            "player_mana": 0.0,
            "player_health_pct": 1.0,
            "player_mana_pct": 1.0,
            "player_id": 0,
            "player_merc": None,
        }

        _data["menus"] = data["wp_menu"]
        _data["used_skill"] = data["used_skill"]
        _data["left_skill"] = data["left_skill"]
        _data["right_skill"] = data["right_skill"]
        _data["current_area"] = data["current_area"]
        _data["belt_health_pots"] = data["belt_health_pots"]
        _data["belt_mana_pots"] = data["belt_mana_pots"]
        _data["belt_rejuv_pots"] = data["belt_rejuv_pots"]
        _data["player_stats"] = data["player_stats"]
        _data["player_gold"] = data["player_gold"]
        _data["player_id"] = data["player_id"]
        _data["player_merc"] = data["player_merc"]
        _data["map"] = np.array(data["collision_grid"], dtype=np.uint8)
        _data["map"][_data["map"] == 1] = 0
        _data["map"] += 1


        px_int = int(data["player_pos"]["X"])
        py_int = int(data["player_pos"]["Y"])

        _data["area_origin"] = np.array([int(data["area_origin"]["X"]), int(data["area_origin"]["Y"])])
        _data["player_pos_world"] = np.array([px_int, py_int])
        self._player_pos = _data["player_pos_world"]
        _data["player_pos_area"] = _data["player_pos_world"] - _data["area_origin"]
        
        health = data["player_life"]
        max_health = data["player_max_life"]
        mana = data["player_mana"]
        max_mana = data["player_max_mana"]
        _data["player_health"] = health
        _data["player_max_health"] = max_health
        _data["player_mana"] = mana
        _data["player_max_mana"] = max_mana
        _data["player_health_pct"] = float(health) / max_health if max_health > 0 else 0.0
        _data["player_mana_pct"] = float(mana) / max_mana if max_mana > 0 else 0.0

        px_float = float(data["player_pos"]["X"])-float(px_int)
        py_float = float(data["player_pos"]["Y"])-float(py_int)

        _data["player_offset"] = np.array([px_float,py_float])

        for npc in data["static_npcs"]:
            for p in npc["position"]:
                p = np.array([int(p["X"]), int(p["Y"])])
                npc["position"] = p
            _data["static_npcs"].append(npc)

        for monster in data["monsters"]:
            monster["position"] = np.array([int(monster["position"]["X"]), int(monster["position"]["Y"])])
            monster["abs_screen_position"] = np.array(world_to_abs(monster["position"], self._player_pos))
            monster["dist"] = math.dist(_data["player_pos_world"], monster["position"])
            _data["monsters"].append(monster)

        for poi in data["points_of_interest"]:
            poi["position"] = np.array([int(poi["position"]["X"]), int(poi["position"]["Y"])])
            poi["abs_screen_position"] = np.array(world_to_abs(poi["position"], self._player_pos))
            _data["poi"].append(poi)

        for obj in data["objects"]:
            obj["position"] = np.array([int(obj["position"]["X"]), int(obj["position"]["Y"])])
            obj["abs_screen_position"] = np.array(world_to_abs(obj["position"], self._player_pos))
            _data["objects"].append(obj)

        for item in data["items"]:
            item["position"] = np.array([int(item["position"]["X"]), int(item["position"]["Y"])])
            item["abs_screen_position"] = np.array(world_to_abs(item["position"], self._player_pos))
            item["dist"] = math.dist(_data["player_pos_world"], item["position"])
            _data["items"].append(item)
        _data["items"] = sorted(_data["items"], key=lambda r: r["dist"])
        return _data
