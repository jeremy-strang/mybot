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
        self.in_game = False
        self.inventory_open = False
        self.character_open = False
        self.skill_select_open = False
        self.skill_tree_open = False
        self.chat_open = False
        self.npc_interact_open = False
        self.esc_menu_open = False
        self.map_open = False
        self.npc_shop_open = False
        self.quest_log_open = False
        self.waypoint_open = False
        self.party_open = False
        self.stash_open = False
        self.cube_open = False
        self.potion_belt_open = False
        self.mercenary_inventory_open = False

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
        ApiHost.Run(self._convert_config(), Action[String](self._callback), True)

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
            "player_corpse": None,
            "item_on_cursor": False,
        }

        _data["menus"] = data["menus"]
        
        if self.in_game != data["in_game"]: print(f"in_game changed from {self.in_game} to {data['in_game']}")
        if self.inventory_open != data["inventory_open"]: print(f"inventory_open changed from {self.inventory_open} to {data['inventory_open']}")
        if self.character_open != data["character_open"]: print(f"character_open changed from {self.character_open} to {data['character_open']}")
        if self.skill_select_open != data["skill_select_open"]: print(f"skill_select_open changed from {self.skill_select_open} to {data['skill_select_open']}")
        if self.skill_tree_open != data["skill_tree_open"]: print(f"skill_tree_open changed from {self.skill_tree_open} to {data['skill_tree_open']}")
        if self.chat_open != data["chat_open"]: print(f"chat_open changed from {self.chat_open} to {data['chat_open']}")
        if self.npc_interact_open != data["npc_interact_open"]: print(f"npc_interact_open changed from {self.npc_interact_open} to {data['npc_interact_open']}")
        if self.esc_menu_open != data["esc_menu_open"]: print(f"esc_menu_open changed from {self.esc_menu_open} to {data['esc_menu_open']}")
        if self.map_open != data["map_open"]: print(f"map_open changed from {self.map_open} to {data['map_open']}")
        if self.npc_shop_open != data["npc_shop_open"]: print(f"npc_shop_open changed from {self.npc_shop_open} to {data['npc_shop_open']}")
        if self.quest_log_open != data["quest_log_open"]: print(f"quest_log_open changed from {self.quest_log_open} to {data['quest_log_open']}")
        if self.waypoint_open != data["waypoint_open"]: print(f"waypoint_open changed from {self.waypoint_open} to {data['waypoint_open']}")
        if self.party_open != data["party_open"]: print(f"party_open changed from {self.party_open} to {data['party_open']}")
        if self.stash_open != data["stash_open"]: print(f"stash_open changed from {self.stash_open} to {data['stash_open']}")
        if self.cube_open != data["cube_open"]: print(f"cube_open changed from {self.cube_open} to {data['cube_open']}")
        if self.potion_belt_open != data["potion_belt_open"]: print(f"potion_belt_open changed from {self.potion_belt_open} to {data['potion_belt_open']}")
        if self.mercenary_inventory_open != data["mercenary_inventory_open"]: print(f"mercenary_inventory_open changed from {self.mercenary_inventory_open} to {data['mercenary_inventory_open']}")
        
        self.in_game = _data["in_game"] = data["in_game"]
        self.inventory_open = _data["inventory_open"] = data["inventory_open"]
        self.character_open = _data["character_open"] = data["character_open"]
        self.skill_select_open = _data["skill_select_open"] = data["skill_select_open"]
        self.skill_tree_open = _data["skill_tree_open"] = data["skill_tree_open"]
        self.chat_open = _data["chat_open"] = data["chat_open"]
        self.npc_interact_open = _data["npc_interact_open"] = data["npc_interact_open"]
        self.esc_menu_open = _data["esc_menu_open"] = data["esc_menu_open"]
        self.map_open = _data["map_open"] = data["map_open"]
        self.npc_shop_open = _data["npc_shop_open"] = data["npc_shop_open"]
        self.quest_log_open = _data["quest_log_open"] = data["quest_log_open"]
        self.waypoint_open = _data["waypoint_open"] = data["waypoint_open"]
        self.party_open = _data["party_open"] = data["party_open"]
        self.stash_open = _data["stash_open"] = data["stash_open"]
        self.cube_open = _data["cube_open"] = data["cube_open"]
        self.potion_belt_open = _data["potion_belt_open"] = data["potion_belt_open"]
        self.mercenary_inventory_open = _data["mercenary_inventory_open"] = data["mercenary_inventory_open"]

        _data["used_skill"] = data["used_skill"]
        _data["left_skill"] = data["left_skill"]
        _data["right_skill"] = data["right_skill"]
        _data["current_area"] = data["current_area"]
        _data["belt_health_pots"] = data["belt_health_pots"]
        _data["belt_mana_pots"] = data["belt_mana_pots"]
        _data["belt_rejuv_pots"] = data["belt_rejuv_pots"]
        _data["flattened_belt"] = data["flattened_belt"]
        _data["player_stats"] = data["player_stats"]
        _data["player_gold"] = data["player_gold"]
        _data["player_id"] = data["player_id"]
        _data["player_merc"] = data["player_merc"]
        _data["player_corpse"] = data["player_corpse"]
        _data["item_on_cursor"] = data["item_on_cursor"]

        if data["map_changed"]:
            print(f"Map changed: {len(data['collision_grid'])}")
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
            x = item["position"][0]
            y = item["position"][1]
            item["position"] = np.array([x, y])
            item["abs_screen_position"] = np.array(world_to_abs(item["position"], self._player_pos))
            item["dist"] = math.dist(_data["player_pos_world"], item["position"])
        _data["items"] = data["items"]

        return _data
