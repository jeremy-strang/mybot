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
from utils.misc import unit_vector, clip_abs_point
from python_tsp.heuristics import solve_tsp_simulated_annealing, solve_tsp_local_search
from python_tsp.exact import solve_tsp_dynamic_programming

def closest_node(node, nodes):
    return nodes[cdist([node], nodes).argmin()]

def cluster_nodes(nodes, max_cluster_ct = None):
    features = np.array([[0, 0]])
    clusters = np.array([[0, 0]])
    x = 0
    y = 0
    for node in nodes:
        for key in node:
            if key:
                features = np.concatenate((features, [np.array([x,y])]))
            x += 1
        x = 0
        y += 1
    features[0, 0:-1, ...] = features[0, 1:, ...]
    cluster_count = int(features.size / 3000)
    if max_cluster_ct is not None:
        cluster_count = min(max_cluster_ct, cluster_count)
    while features.size > 2048:
        features = np.delete(features, list(range(0, features.shape[0], 2)), axis=0)
    clusters_k, distortion = kmeans(features.astype(float), cluster_count,iter=5)
    for c in clusters_k:
        closest = closest_node(c, features)
        clusters = np.concatenate((clusters, [closest]))
    clusters = np.delete(clusters, 0, 0)
    return clusters

def make_path_bfs(start, end, grid):
    wall = 0
    queue = deque([[start]])
    seen = set([start])
    width = len(grid)
    height = len(grid[0])
    while queue:
        path = queue.popleft()
        x, y = path[-1]
        if (x, y) == end:
            if path is None:
                print("NO PATH")
                print(path)
            return path
        for x2, y2 in ((x+1, y), (x-1, y), (x, y+1), (x, y-1), (x-1, y-1), (x+1, y+1), (x+1, y-1), (x-1, y+1)):
            if 0 <= x2 < width and 0 <= y2 < height and grid[y2][x2] != wall and (x2, y2) not in seen:
                queue.append(path + [(x2, y2)])
                seen.add((x2, y2))

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
    def __init__(self, api: MapAssistApi):
        self._api = api
        self._data = None
        self._map = None
        self._current_area = None
        self._clusters = None
        self._weighted_map = None
        self.player_node = None
        self.update_map()
    
    def update_map(self):
        data = self._api.get_data()
        self._data = data
        if data is not None:
            player_x_local = data["player_pos_world"][0] - data["area_origin"][0]
            player_y_local = data["player_pos_world"][1] - data["area_origin"][1]
            self.player_node = (int(player_x_local + 1), int(player_y_local + 1))
            if data["current_area"] != self._current_area:
                self._map = data["map"]
                self._current_area = data["current_area"]
                self._clusters = cluster_nodes(self._map, 10)
                # print(self._clusters)
                float_map = self._map.astype(np.float32)
                float_map[float_map == 0] = 999999.0
                float_map[float_map == 1] = 0.0
                blurred_map = gaussian_filter(float_map, sigma=7)
                self._weighted_map = np.maximum(blurred_map * .001, float_map) + 1

    def make_path_astar(self, start, end, reverse_coords=False):
        if reverse_coords:
            start = (start[1], start[0])
            end = (end[1], end[0])
        weighted = self._weighted_map.astype(np.float32)
        path = pyastar2d.astar_path(weighted, start, end, allow_diagonal=True)
        path = np.flip(path, 1)
        path = path.tolist()
        return path

    def make_path_bfs(self, start, end):
        wall = 0
        queue = deque([[start]])
        seen = set([start])
        width = len(self._map)
        height = len(self._map[0])
        while queue:
            path = queue.popleft()
            x, y = path[-1]
            if (x, y) == end:
                if path is None:
                    print("NO PATH")
                    print(path)
                return path
            for x2, y2 in ((x+1, y), (x-1, y), (x, y+1), (x, y-1), (x-1, y-1), (x+1, y+1), (x+1, y-1), (x-1, y+1)):
                if 0 <= x2 < width and 0 <= y2 < height and self._map[y2][x2] != wall and (x2, y2) not in seen:
                    queue.append(path + [(x2, y2)])
                    seen.add((x2, y2))
        return []
    
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
                    # path_ij = self.make_path_astar(nodes[i], nodes[j], reverse_coords=True)
                    # dist_matrix[i, j] = len(path_ij)
                    dist_matrix[i, j] = cityblock(nodes[i], nodes[j])
        if end_given: dist_matrix[0, N-1] = 0
        elapsed = time.time() - start
        print(f"Calculated distance matrix in {elapsed} seconds")
        print(dist_matrix)
        permutation = None
        if exact:
            permutation, distance = solve_tsp_dynamic_programming(dist_matrix)
        else:
            permutation, distance = solve_tsp_local_search(dist_matrix)
        path = []
        for i in permutation:
            if not end_given or (end_given and i != N-1):
                path.append(nodes[i])
        elapsed = time.time() - start
        print(f"Done solving TSP in {elapsed} seconds")
        print(permutation)
        return path[:-1] if end_given else path


    def _solve_tsp(self, end=None):
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
                if not end_given or (i != 0 and j != N-1):
                    path_ij = self.make_path_astar(nodes[i], nodes[j], reverse_coords=True)
                    dist_matrix[i, j] = len(path_ij)
        if end_given: dist_matrix[0, N-1] = 0
        print(dist_matrix)
        permutation, distance = solve_tsp_dynamic_programming(dist_matrix)
        print(permutation)
        path = []
        for i in permutation:
            if i != N-1: path.append(nodes[i])
        return path

