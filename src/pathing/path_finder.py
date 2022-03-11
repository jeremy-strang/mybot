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
from python_tsp.exact import solve_tsp_dynamic_programming

def closest_node(node, nodes):
    return nodes[cdist([node], nodes).argmin()]

def cluster_nodes(nodes):
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
        self._player_node = None
        self.update_map()
    
    def update_map(self):
        data = self._api.get_data()
        self._data = data
        if data is not None:
            player_x_local = data["player_pos_world"][0] - data["area_origin"][0]
            player_y_local = data["player_pos_world"][1] - data["area_origin"][1]
            self._player_node = (int(player_x_local + 1), int(player_y_local + 1))
            if data["current_area"] != self._current_area:
                self._map = data["map"]
                self._current_area = data["current_area"]
                self._clusters = cluster_nodes(self._map)
                float_map = self._map.astype(np.float32)
                float_map[float_map == 0] = 999999.0
                float_map[float_map == 1] = 0.0
                blurred_map = gaussian_filter(float_map, sigma=7)
                self._weighted_map = np.maximum(blurred_map * .001, float_map) + 1

    def make_path_astar(self, start, end):
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
    
    def solve_tsp(self, end=None):
        self.update_map()
        queue = deque(self._clusters)
        queue.appendleft(self._player_node)
        if end is not None:
            end = (end[0], end[1])
            queue.append(end)
        nodes = np.asarray(queue)
        N = len(nodes)
        dist_matrix = np.zeros((N, N))
        # Find distance in number of nodes between each node i, j
        for i in range(N):
            for j in range(N):
                start = (nodes[i][1], nodes[i][0]) # y x (backwards)
                end = (nodes[j][1], nodes[j][0]) # y x (backwards)
                path_ij = self.make_path_astar(start, end)
                dist_matrix[i, j] = len(path_ij)
        print("Computed distance matrix using astar path node length:")
        print(dist_matrix)
        permutation, distance = solve_tsp_dynamic_programming(dist_matrix)
        print(f"Solved TSP, distance: {distance}, permutation:")
        print(permutation)
        path = []
        for i in permutation:
            path.append(nodes[i])
        return path

    def create_cluster_route(self):
        route = []
        clusters = []
        self.update_map()
        data = self._data
        if data is not None:
            # player_x_local = data["player_pos_world"][0] - data["area_origin"][0]
            # player_y_local = data["player_pos_world"][1] - data["area_origin"][1]
            # start = (int(player_x_local + 1), int(player_y_local + 1))
            start = self._player_node
            clusters = cluster_nodes(self._map)
            for cluster in clusters:
                end = (cluster[0], cluster[1])
                next_route = self.make_path_astar(start, end)
                if next_route is not None:
                    route += next_route
                    start = end
        return (route, clusters)



