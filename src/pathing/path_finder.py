from collections import deque
import queue
import time
import random
import ctypes
import numpy as np
import pyastar2d
from copy import deepcopy
from api.mapassist import MapAssistApi
from logger import Logger
from typing import List, Tuple
from math import ceil, cos, floor, sin, dist
from win32con import HWND_TOPMOST, SWP_NOMOVE, SWP_NOSIZE, HWND_NOTOPMOST
from win32gui import GetWindowText, SetWindowPos, EnumWindows, GetClientRect, ClientToScreen
from win32api import GetMonitorInfo, MonitorFromWindow
from win32process import GetWindowThreadProcessId
from scipy.spatial.distance import cdist
from scipy.spatial.distance import cityblock
from scipy.cluster.vq import kmeans
from scipy.ndimage.filters import gaussian_filter
from utils.misc import cluster_nodes, unit_vector, clip_abs_point
from python_tsp.heuristics import solve_tsp_simulated_annealing, solve_tsp_local_search
from python_tsp.exact import solve_tsp_dynamic_programming

def make_path_astar(start, end, grid):
    float_map = grid.astype(np.float32)
    float_map[float_map == 0] = 999999.0
    float_map[float_map == 1] = 0.0
    blurred_map = gaussian_filter(float_map, sigma=7)
    comp = np.maximum(blurred_map*.001, float_map)
    # out = (comp)*.00001
    comp = comp+1
    path = pyastar2d.astar_path(comp.astype(
        np.float32), start, end, allow_diagonal=True)
    path = np.flip(path, 1)
    path = path.tolist()
    return path

class PathFinder:
    def __init__(self, api: MapAssistApi, max_cluster_ct=25):
        self._api = api
        self._data = None
        self._map = None
        self._current_area = None
        self._clusters = None
        self._weighted_map = None
        self._max_cluster_ct = max_cluster_ct
        self.player_node = None
        self.update_map()
    
    def update_map(self):
        data = self._data = self._api.data
        if data:
            player_x_local = data['player_pos_world'][0] - data['area_origin'][0]
            player_y_local = data['player_pos_world'][1] - data['area_origin'][1]
            self.player_node = (int(player_x_local + 1), int(player_y_local + 1))
            if data['current_area'] != self._current_area or data['map_changed']:
                self._map = data["map"]
                self._current_area = data["current_area"]
                self._clusters = cluster_nodes(self._map, self._max_cluster_ct)
                float_map = self._map.astype(np.float32)
                float_map[float_map == 0] = 999999.0
                float_map[float_map == 1] = 0.0
                blurred_map = gaussian_filter(float_map, sigma=7)
                self._weighted_map = np.maximum(blurred_map * .001, float_map) + 1

    def make_path_astar(self, start, end, reverse_coords=False):
        self.update_map()
        if reverse_coords:
            start = (start[1], start[0])
            end = (end[1], end[0])
        weighted = self._weighted_map.astype(np.float32)
        path = pyastar2d.astar_path(weighted, start, end, allow_diagonal=True)
        path = np.flip(path, 1)
        path = path.tolist()
        return path
    
    def solve_tsp(self, end=None, exact=False):
        start = time.time()
        self.update_map()
        queue = deque(self._clusters)
        queue.appendleft(self.player_node)

        end_given = end is not None
        if end_given:
            end = (end[0], end[1])
            queue.append(end)
        nodes = np.asarray(queue)
        N = len(nodes)
        if end_given: N += 1

        # Find distance in number of nodes between each node i, j
        dist_matrix = np.zeros((N, N))
        for i in range(N):
            for j in range(N):
                if not end_given or (i != N-1 and j != N-1):
                    dist_matrix[i, j] = cityblock(nodes[i], nodes[j])
        if end_given: dist_matrix[0, N-1] = 0
        elapsed = time.time() - start
        permutation = None
        distance = 0
        if exact:
            permutation, distance = solve_tsp_dynamic_programming(dist_matrix)
        else:
            permutation, distance = solve_tsp_local_search(dist_matrix)
        path = []
        for i in permutation:
            if not end_given or (end_given and i != N-1):
                path.append(nodes[i])
        elapsed = time.time() - start
        print(f"Done solving TSP in {round(elapsed, 2)} seconds, distance: {round(distance, 2)}")
        return path[:-1] if end_given else path
    
    