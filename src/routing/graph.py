import collections
import time
import random
import ctypes
import numpy as np
import pyastar2d
from copy import deepcopy
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

def make_route_bfs(start, goal, grid):
    wall = 0
    queue = collections.deque([[start]])
    seen = set([start])
    width = len(grid)
    height = len(grid[0])
    while queue:
        path = queue.popleft()
        x, y = path[-1]
        if (x, y) == goal:
            if path is None:
                print("NO PATH")
                print(path)
            return path
        for x2, y2 in ((x+1, y), (x-1, y), (x, y+1), (x, y-1), (x-1, y-1), (x+1, y+1), (x+1, y-1), (x-1, y+1)):
            if 0 <= x2 < width and 0 <= y2 < height and grid[y2][x2] != wall and (x2, y2) not in seen:
                queue.append(path + [(x2, y2)])
                seen.add((x2, y2))

def make_route_astar(start, end, grid):
    # player_local = (int(player_y_local),
    #                 int(player_x_local))
    # dest = (int(y), int(x))

    float_map = grid.astype(np.float32)

    float_map[float_map == 0] = 999999.0
    float_map[float_map == 1] = 0.0

    # smooth transitions, less local wandering with this
    # we should prob store it somewhere on map load?
    blurred_map = gaussian_filter(float_map, sigma=7)

    comp = np.maximum(blurred_map*.001, float_map)
    out = (comp)*.00001
    comp = comp+1

    path = pyastar2d.astar_path(comp.astype(np.float32), start, end, allow_diagonal=True)
    path = np.flip(path, 1)
    path = path.tolist()
    return path

def create_cluster_route(data):
    route = []
    clusters = []
    if data is not None:
        player_x_local = data["player_pos_world"][0] - data["area_origin"][0]
        player_y_local = data["player_pos_world"][1] - data["area_origin"][1]
        start = (int(player_x_local + 1), int(player_y_local + 1))
        clusters = cluster_nodes(data["map"])
        for cluster in clusters:
            end = (cluster[0], cluster[1])
            next_route = make_route_bfs(start, end, data["map"])
            if next_route is not None:
                route += next_route
                start = end
    return (route, clusters)







