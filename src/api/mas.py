'''
This runs map assist from compiled dlls
'''
import configparser
import os
import clr
import numpy as np
from requests.exceptions import ConnectionError
import math
from threading import Thread
from utils.coordinates import world_to_abs

clr.AddReference(os.path.abspath(r'MapAssistApi/bin/x64/Release/MapAssist.dll'))

from MapAssist.MyBot import ApiHost
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
        self._player_pos_world=None
        self._callback = callback
        self._custom_files = custom_files
        self.in_game = False
        self.should_chicken = False
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
        self.player_summary = None
        self.player_name = None

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

    def get_data(self, data) -> dict:
        _data = {
            "monsters": [],
            "mercs": [],
            "points_of_interest": [],
            "objects": [],
            "items": [],
            "items_logged": [],
            "static_npcs": [],
            "map": None,
            "player_pos_world": None,
            "player_pos_area": None,
            "area_origin": None,
            "current_area": None,
            "used_skill": None,
            "right_skill": None,
            "left_skill": None,
            "item_on_cursor": False,
            "menus": None,
            "player_health": 0.0,
            "player_mana": 0.0,
            "player_health_pct": 1.0,
            "player_mana_pct": 1.0,
            "player_id": 0,
            "player_merc": None,
            "player_corpse": None,
        }

        _data["menus"] = data["menus"]
        
        # if self.in_game != data["in_game"]: print(f"in_game changed from {self.in_game} to {data['in_game']}")
        # if self.should_chicken != data["should_chicken"]: print(f"should_chicken changed from {self.should_chicken} to {data['should_chicken']}")
        # if self.inventory_open != data["inventory_open"]: print(f"inventory_open changed from {self.inventory_open} to {data['inventory_open']}")
        # if self.character_open != data["character_open"]: print(f"character_open changed from {self.character_open} to {data['character_open']}")
        # if self.skill_select_open != data["skill_select_open"]: print(f"skill_select_open changed from {self.skill_select_open} to {data['skill_select_open']}")
        # if self.skill_tree_open != data["skill_tree_open"]: print(f"skill_tree_open changed from {self.skill_tree_open} to {data['skill_tree_open']}")
        # if self.chat_open != data["chat_open"]: print(f"chat_open changed from {self.chat_open} to {data['chat_open']}")
        # if self.npc_interact_open != data["npc_interact_open"]: print(f"npc_interact_open changed from {self.npc_interact_open} to {data['npc_interact_open']}")
        # if self.esc_menu_open != data["esc_menu_open"]: print(f"esc_menu_open changed from {self.esc_menu_open} to {data['esc_menu_open']}")
        # if self.map_open != data["map_open"]: print(f"map_open changed from {self.map_open} to {data['map_open']}")
        # if self.npc_shop_open != data["npc_shop_open"]: print(f"npc_shop_open changed from {self.npc_shop_open} to {data['npc_shop_open']}")
        # if self.quest_log_open != data["quest_log_open"]: print(f"quest_log_open changed from {self.quest_log_open} to {data['quest_log_open']}")
        # if self.waypoint_open != data["waypoint_open"]: print(f"waypoint_open changed from {self.waypoint_open} to {data['waypoint_open']}")
        # if self.party_open != data["party_open"]: print(f"party_open changed from {self.party_open} to {data['party_open']}")
        # if self.stash_open != data["stash_open"]: print(f"stash_open changed from {self.stash_open} to {data['stash_open']}")
        # if self.cube_open != data["cube_open"]: print(f"cube_open changed from {self.cube_open} to {data['cube_open']}")
        # if self.potion_belt_open != data["potion_belt_open"]: print(f"potion_belt_open changed from {self.potion_belt_open} to {data['potion_belt_open']}")
        # if self.mercenary_inventory_open != data["mercenary_inventory_open"]: print(f"mercenary_inventory_open changed from {self.mercenary_inventory_open} to {data['mercenary_inventory_open']}")
        
        self.in_game = _data["in_game"] = data["in_game"]
        self.should_chicken = _data["should_chicken"] = data["should_chicken"]
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

        _data["map_changed"] = data["map_changed"]
        if data["map_changed"]:
            _data["map"] = np.array(data["collision_grid"], dtype=np.uint8)
            _data["map"][_data["map"] == 1] = 0
            _data["map"] += 1
        
        if self.player_summary is None and self.in_game:
            self.player_summary = f"Level {data['player_level']} {data['player_class']}"
            self.player_name = data['player_name']

        player_x_world = int(data["player_pos_world"]["X"])
        player_y_world = int(data["player_pos_world"]["Y"])
        area_origin_x = int(data["area_origin"]["X"])
        area_origin_y = int(data["area_origin"]["Y"])
        _data["area_origin"] = np.array([area_origin_x, area_origin_y])
        _data["player_pos_world"] = np.array([player_x_world, player_y_world])
        self._player_pos_world = _data["player_pos_world"]
        _data["player_pos_area"] = np.array([player_x_world - area_origin_x,
                                             player_y_world - area_origin_y])
        
        _data["player_health"] = data["player_health"]
        _data["player_max_health"] = data["player_max_health"]
        _data["player_mana"] = data["player_mana"]
        _data["player_max_mana"] = data["player_max_mana"]
        _data["player_health_pct"] = data["player_health_pct"]
        _data["player_mana_pct"] = data["player_mana_pct"]
        _data["merc_alive"] = "player_merc" in data and data["player_merc"] is not None and data["player_merc"]["mode"] != 12
        _data["merc_health_pct"] = data["player_merc"]["heath_percentage"] if _data["merc_alive"] else 0.0

        px_float = float(data["player_pos_world"]["X"]) - float(player_x_world)
        py_float = float(data["player_pos_world"]["Y"]) - float(player_y_world)
        _data["player_offset"] = np.array([px_float,
                                           py_float])

        for npc in data["static_npcs"]:
            for p in npc["position"]:
                p = np.array([int(p["X"]), int(p["Y"])])
                npc["position"] = p
            _data["static_npcs"].append(npc)

        for monster in data["monsters"]:
            monster_world_x = int(monster["position"]["X"])
            monster_world_y = int(monster["position"]["Y"])
            monster["position"] = np.array([monster_world_x, monster_world_y])
            monster["position_abs"] = np.array(world_to_abs(monster["position"], self._player_pos_world))
            monster["position_area"] = np.array([monster_world_x - area_origin_x, monster_world_y - area_origin_y])
            monster["dist"] = math.dist(_data["player_pos_world"], monster["position"])
            _data["monsters"].append(monster)

        for poi in data["points_of_interest"]:
            poi_world_x = int(poi["position"]["X"])
            poi_world_y = int(poi["position"]["Y"])
            poi["position"] = np.array([poi_world_x, poi_world_y])
            poi["position_abs"] = np.array(world_to_abs(poi["position"], self._player_pos_world))
            poi["position_area"] = np.array([poi_world_x - area_origin_x, poi_world_y - area_origin_y])
            _data["points_of_interest"].append(poi)

        for obj in data["objects"]:
            obj_world_x = int(obj["position"]["X"])
            obj_world_y = int(obj["position"]["Y"])
            obj["position"] = np.array([obj_world_x, obj_world_y])
            obj["position_abs"] = np.array(world_to_abs(obj["position"], self._player_pos_world))
            obj["position_area"] = np.array([obj_world_x - area_origin_x, obj_world_y - area_origin_y])
            _data["objects"].append(obj)

        for item in data["items"]:
            item_world_x = int(item["position"][0])
            item_world_y = int(item["position"][1])
            item["position"] = np.array([item_world_x, item_world_y])
            item["position_abs"] = np.array(world_to_abs(item["position"], self._player_pos_world))
            item["position_area"] = np.array([item_world_x - area_origin_x, item_world_y - area_origin_y])
            item["dist"] = math.dist(_data["player_pos_world"], item["position"])
        _data["items"] = data["items"]

        for item in data["items_logged"]:
            item_world_x = int(item["position"][0])
            item_world_y = int(item["position"][1])
            item["position"] = np.array([item_world_x, item_world_y])
            item["position_abs"] = np.array(world_to_abs(item["position"], self._player_pos_world))
            item["position_area"] = np.array([item_world_x - area_origin_x, item_world_y - area_origin_y])
            item["dist"] = math.dist(_data["player_pos_world"], item["position"])
        _data["items_logged"] = data["items_logged"]

        return _data