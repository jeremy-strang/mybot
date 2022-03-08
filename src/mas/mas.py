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
	def __init__(self, callback):
		super(MAS, self).__init__()
		self.daemon = True
		self._pg = None
		self._pg_main = None
		self._pg=None
		self._data=None
		self._player_pos=None
		self._callback = callback

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
		MAS._append_file(config, "./config/custom.ini")
		return config

	def run(self):
		'''overload'''
		ApiHost.Run(self._convert_config(), Action[String](self._callback))


	def cancel(self):
		'''kill thread'''
		ApiHost.Stop()

	def delta_world_to_minimap(self,delta, diag, scale, deltaZ = 0.0):
		camera_angle = -26.0 * 3.14159274 / 180.0

		cos = (diag * math.cos(camera_angle) / scale)
		sin = (diag * math.sin(camera_angle) / scale)

		d = ((delta[0] - delta[1]) * cos, deltaZ - (delta[0] + delta[1]) * sin)

		return d

	def world_to_abs(self, dest):
		'''
		convert world space to ABS screen coords
		'''
		w = 1280
		h = 720 
		player = self._player_pos
		screen_center = (w/2.0, h/2.0)
		delta =  self.delta_world_to_minimap(dest-player,math.sqrt(w*w+h*h),68.5,30)
		screen_coords = ( delta[0],delta[1])
		return screen_coords

	def calc_distance (self, mon):
		if mon["bossID"] != 0:
			return 0
		elif mon["type"] in "SuperUnique":
			return 0.05
		elif any (mobtype in mon["type"] for mobtype in ["Unique", "Champion"]):
			return 0.1
		elif mon["type"] in "Minion":
			return 0.2
		else:
			return mon["dist"]

	def get_data(self, data) -> dict:
		botty_data = {
			"monsters": [],
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
			"menus":None,
		}
		
		# UI, map, and player info
		# ===========================
		botty_data["menus"] = data["wp_menu"]
		botty_data["used_skill"] = data["used_skill"]
		botty_data["left_skill"] = data["left_skill"]
		botty_data["right_skill"] = data["right_skill"]
		botty_data["current_area"] = data["current_area"]
		botty_data["belt_health_pots"] = data["belt_health_pots"]
		botty_data["belt_mana_pots"] = data["belt_mana_pots"]
		botty_data["player_stats"] = data["player_stats"]
		botty_data["player_gold"] = data["player_gold"]
		botty_data["map"] = np.array(data["collision_grid"], dtype=np.uint8)
		botty_data["map"][botty_data["map"] == 1] = 0
		botty_data["map"] += 1

		px_int = int(data["player_pos"]["X"])
		py_int = int(data["player_pos"]["Y"])



		botty_data["area_origin"] = np.array([int(data["area_origin"]["X"]), int(data["area_origin"]["Y"])])
		botty_data["player_pos_world"] = np.array([px_int, py_int])
		self._player_pos = botty_data["player_pos_world"]
		botty_data["player_pos_area"] = botty_data["player_pos_world"] - botty_data["area_origin"]

		#print(botty_data['player_pos_area'])
		#print(botty_data['player_pos_area'])

		px_float = float(data["player_pos"]["X"])-float(px_int)
		py_float = float(data["player_pos"]["Y"])-float(py_int)

		botty_data["player_offset"] = np.array([px_float,py_float])

		#static npcs
		for npc in data["static_npcs"]:
			#print(npc)
			for p in npc['position']:
				p = np.array([int(p["X"]), int(p["Y"])])
				npc['position'] = p
			botty_data["static_npcs"].append(npc)


		# Monsters
		# ===========================
		for monster in data["monsters"]:
			monster["position"] = np.array([int(monster["position"]["X"]), int(monster["position"]["Y"])])
			monster["abs_screen_position"] = np.array(world_to_abs(monster["position"], self._player_pos))
			monster["dist"] = math.dist(botty_data["player_pos_world"], monster["position"])
			botty_data["monsters"].append(monster)
			#if monster['number'] == 479:
			#	print(monster)#shenk
		#botty_data["monsters"] = sorted(botty_data["monsters"], key=lambda r: r["dist"])
		botty_data["monsters"].sort(key=self.calc_distance)
		# Points of Interest
		# ===========================
		for poi in data["points_of_interest"]:
			poi["position"] = np.array([int(poi["position"]["X"]), int(poi["position"]["Y"])])
			poi["abs_screen_position"] = np.array(world_to_abs(poi["position"], self._player_pos))
			botty_data["poi"].append(poi)
			#print(poi)
		# Objects
		# ===========================
		for obj in data["objects"]:
			#print(obj)
			obj["position"] = np.array([int(obj["position"]["X"]), int(obj["position"]["Y"])])
			obj["abs_screen_position"] = np.array(world_to_abs(obj["position"], self._player_pos))
			botty_data["objects"].append(obj)
		# Items
		# ===========================
		for item in data["items"]:
			item["position"] = np.array([int(item["position"]["X"]), int(item["position"]["Y"])])
			item["abs_screen_position"] = np.array(world_to_abs(item["position"], self._player_pos))
			item["dist"] = math.dist(botty_data["player_pos_world"], item["position"])
			botty_data["items"].append(item)
		botty_data["items"] = sorted(botty_data["items"], key=lambda r: r["dist"])
		return botty_data