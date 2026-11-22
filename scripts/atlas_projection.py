"""Geometry shared by the relief basemap and its geographic labels."""

from math import cos, radians

WIDTH, HEIGHT = 748, 496
CENTRE_X, CENTRE_Y = 372, 242


def projection(ring):
    cosine = cos(radians(52))
    xs, ys = zip(*[(lon * cosine, -lat) for lon, lat in ring])
    scale = min(535 / (max(xs) - min(xs)), 455 / (max(ys) - min(ys)))
    cx, cy = (max(xs) + min(xs)) / 2, (max(ys) + min(ys)) / 2
    return cosine, scale, cx, cy


def project(lon, lat, params):
    cosine, scale, cx, cy = params
    return CENTRE_X + (lon * cosine - cx) * scale, CENTRE_Y + (-lat - cy) * scale
