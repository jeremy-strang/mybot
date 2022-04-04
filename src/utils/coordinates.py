import math

def delta_in_world_to_minimap_delta(delta, diag, scale, deltaZ=0.0):
    camera_angle = -26.0 * 3.14159274 / 180.0
    cos = (diag * math.cos(camera_angle) / scale)
    sin = (diag * math.sin(camera_angle) / scale)
    d = ((delta[0] - delta[1]) * cos, deltaZ - (delta[0] + delta[1]) * sin)
    return d

def world_to_abs(dest, player):
    w = 1280
    h = 720
    delta = delta_in_world_to_minimap_delta(dest-player, math.sqrt(w * w + h * h), 68.5, 30)
    screen_coords = (delta[0], delta[1])
    return screen_coords
