from d2r import D2rApi, D2rMenu
from logger import Logger
from screen import Screen
import time
import colorama
from colorama import init
from colorama import *
from termcolor import colored
from logger import Logger

import math
import numpy as np

import mouse as _mouse
from utils.custom_mouse import mouse
import keyboard

class ItemManager:
	def __init__(self,screen: Screen, mapi: D2rApi):
		self._health_pots = 0
		self._rejuv_pots = 0
		self._mana_pots = 0
		self._screen = screen
		self._items = None
		self._api = mapi
		self.x_pos = None
		self.y_pos = None
		self._player_y = None
		self._player_x = None
		
	def _pickup_item(self,x,y):
		print("PICK UP!!!")
		odist = 999999
		'''
		keyboard.send('enter')
		wait(0.1, 0.25)
		keyboard.write('/nopickup',delay=.20)
		keyboard.send('enter')
		wait(0.1, 0.25)
		time.sleep(0.10)
		'''


		player_x = self._player_x
		player_y = self._player_y
		target_x = x
		target_y = y
		odist = math.dist([target_x,target_y],[player_x,player_y])


		target_x = x
		target_y = y
		odist = math.dist([target_x,target_y],[player_x,player_y])
		#print("moving....")
		player_x = self._player_x
		player_y = self._player_y
		odist = math.dist([target_x,target_y],[player_x,player_y])
		#print('odist + '+ str(odist))
		player_x = self._player_x
		player_y = self._player_y
		grid_x = (target_x-player_x)-(target_y-player_y)
		grid_y = (target_x-player_x)+(target_y-player_y)
		#why do these work shoudl be 16x8
		o_pos_x = (grid_x)*19.5
		o_pos_y = (grid_y)*9.5
		#pos_m = self._adjust_abs_range_to_screen([o_pos_x,o_pos_y-10])
		pos_m = [o_pos_x,o_pos_y]
		zero = self._screen.convert_abs_to_monitor(pos_m)
		#this works
		#? BUT WHY
		zero = [zero[0]-4.74,zero[1]-9.75]
		zero1 = self._screen.convert_abs_to_monitor([-4.75,-9.75])
		print(_mouse.__file__)
		_mouse.move(*zero1)
		_mouse.move(*zero)
		_mouse.move(*zero1)
		_mouse.move(*zero)
		print("try and clic...")
		time.sleep(1.5)
		_mouse.press("left")
		time.sleep(.25)
		_mouse.release('left')

		odist = math.dist([target_x,target_y],[player_x,player_y])
		print(odist)

	def start(self):
		print("Startup item manager...")
		while 1:
			time.sleep(.1)
			#self._api = mapi

			try:
				self._items = self._api.data['items']
				self._player_x = self._api.data['player_pos_world'][0]
				self._player_y = self._api.data['player_pos_world'][1]
				# item loc 0 = inventory, 1 = equipped, 2 in belt, 3 on ground, 4 cursor, 5 dropping ,6 socketed
				for i in range(0,len(self._items)):
					item = self._items[i]
					if item['mode'] == 0:
						'''in inventory'''
						Logger.info(colored('in inventory ->'+str(item['name']), 'yellow'))
					if item['mode'] == 1:
						''' equipped '''
						Logger.info(colored(item['name'], 'white'))
					if item['mode'] == 2:
						''' on the belt ''' 
						Logger.info(colored(i['name'], 'blue'))
					if item['mode'] == 3:
						''' on the ground ''' 
						Logger.info(colored('dropped ->'+str(item['name'])+' at ->' + str(item['position']), 'red'))
						x = item['position'][0]
						y = item['position'][1]
						mode = item['mode']
						picked = False
						while not picked:
							self._player_x = self._api.data['player_pos_world'][0]
							self._player_y = self._api.data['player_pos_world'][1]
							print("trying...")
							#print(item)
							self._pickup_item(x,y)
							#update again to see if we got it
							item = self._api.data['items'][i]
							
							mode = item['mode']
							print(mode)
							if mode == 0:
								picked = True
								break
					if item['mode'] == 4:
						''' in cursor/picked up '''
						Logger.info(colored('picked up ->'+str(item['name']), 'cyan'))
					if item['mode'] == 5:
						''' dropping '''
						Logger.info(colored('dropping ->'+str(item['name']), 'green'))
					if item['mode'] == 6:
						''' socketed '''
						Logger.info(colored(i['name'], 'green'))				
			except:
				pass

'''
[{'position': {'X': 0.0, 'Y': 2.0}, 'id': 2331641602, 'flags': 8388624, 'quality': 2, 'name': 'Key of Terror', 'base_data': 'MapAssist.Structs.ItemData', 'base_name': 'Key of Terror'}]
[{'position': {'X': 0.0, 'Y': 2.0}, 'id': 2331641602, 'flags': 8388624, 'quality': 2, 'name': 'Key of Terror', 'base_data': 'MapAssist.Structs.ItemData', 'base_name': 'Key of Terror'}]
[{'position': {'X': 0.0, 'Y': 2.0}, 'id': 2331641602, 'flags': 8388624, 'quality': 2, 'name': 'Key of Terror', 'base_data': 'MapAssist.Structs.ItemData', 'base_name': 'Key of Terror'}]
[2022-01-31 18:39:34,079] INFO       Force Exit
[{'position': {'X': 0.0, 'Y': 2.0}, 'id': 2331641602, 'flags': 8388624, 'quality': 2, 'name': 'Key of Terror', 'base_data': 'MapAssist.Structs.ItemData', 'base_name': 'Key of Terror'}]
Restored D2R window visibility
'''