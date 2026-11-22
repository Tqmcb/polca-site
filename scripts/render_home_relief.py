"""Render the atlas basemap from public Mapzen Terrarium elevation tiles.

Optional cartography build, independent of the static site generator.
Usage: python render_home_relief.py CACHE_DIR OUTPUT.webp [--thumbnail MINI.webp].
Requires NumPy and Pillow.
Coordinates derive from the same Natural Earth geometry as the detailed topic map.
"""

from concurrent.futures import ThreadPoolExecutor
from io import BytesIO
from pathlib import Path
from urllib.request import urlopen
import argparse
import json
from atlas_projection import WIDTH, HEIGHT, CENTRE_X, CENTRE_Y, projection, project
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
PIXELS = 2
ZOOM = 7


def main(cache, output):
    cache.mkdir(parents=True, exist_ok=True)
    geography = json.loads((ROOT / "content/home-map.json").read_text())
    ring = geography["country"]["coordinates"][0]
    params = projection(ring)
    cosine, scale, cx, cy = params

    def image_point(lon, lat):
        x, y = project(lon, lat, params)
        return x * PIXELS, y * PIXELS

    # Reproject a regular geographic output grid into Web Mercator tile pixels.
    x, y = np.meshgrid(
        np.arange(WIDTH * PIXELS) / PIXELS, np.arange(HEIGHT * PIXELS) / PIXELS
    )
    lon = ((x - CENTRE_X) / scale + cx) / cosine
    lat = -((y - CENTRE_Y) / scale + cy)
    world = 256 * 2**ZOOM
    mx = (lon + 180) * world / 360
    my = (1 - np.arcsinh(np.tan(np.radians(lat))) / np.pi) * world / 2
    xmin, xmax = int(mx.min()) // 256, (int(mx.max()) + 1) // 256
    ymin, ymax = int(my.min()) // 256, (int(my.max()) + 1) // 256
    heights = np.empty(
        ((ymax - ymin + 1) * 256, (xmax - xmin + 1) * 256), dtype=np.float32
    )

    def tile(pair):
        tx, ty = pair
        dest = cache / f"{ZOOM}-{tx}-{ty}.png"
        if not dest.is_file():
            url = f"https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{ZOOM}/{tx}/{ty}.png"
            with urlopen(url, timeout=40) as response:
                raw = response.read()
            Image.open(BytesIO(raw)).verify()
            dest.write_bytes(raw)
        rgb = np.array(Image.open(dest).convert("RGB"), dtype=np.float32)
        return tx, ty, rgb[:, :, 0] * 256 + rgb[:, :, 1] + rgb[:, :, 2] / 256 - 32768

    with ThreadPoolExecutor(max_workers=6) as pool:
        pairs = [
            (tx, ty) for tx in range(xmin, xmax + 1) for ty in range(ymin, ymax + 1)
        ]
        for tx, ty, data in pool.map(tile, pairs):
            i, j = (ty - ymin) * 256, (tx - xmin) * 256
            heights[i : i + 256, j : j + 256] = data
    mx -= xmin * 256
    my -= ymin * 256
    ix, iy = mx.astype(int), my.astype(int)
    a, b = mx - ix, my - iy
    z = (
        (1 - a) * (1 - b) * heights[iy, ix]
        + a * (1 - b) * heights[iy, ix + 1]
        + (1 - a) * b * heights[iy + 1, ix]
        + a * b * heights[iy + 1, ix + 1]
    )
    dy, dx = np.gradient(z)
    shade = np.clip((-0.68 * dx - 0.73 * dy) / 12, -1, 1)
    bands = np.clip(np.log1p(np.maximum(z, 0)) / np.log(1500), 0, 1)
    rgb = np.stack(
        [
            230 - 74 * bands + 34 * shade,
            241 - 55 * bands + 26 * shade,
            239 - 31 * bands + 18 * shade,
        ],
        axis=-1,
    )
    surface = Image.fromarray(np.uint8(np.clip(rgb, 0, 255))).convert("RGBA")
    size = surface.size
    mask = Image.new("L", size, 0)
    boundary = [image_point(*coord[:2]) for coord in ring]
    ImageDraw.Draw(mask).polygon(boundary, fill=255)
    ink = ImageDraw.Draw(surface)
    for river in geography["rivers"]:
        geom = river["geometry"]
        streams = (
            geom["coordinates"]
            if geom["type"] == "MultiLineString"
            else [geom["coordinates"]]
        )
        for stream in streams:
            ink.line(
                [image_point(*coord[:2]) for coord in stream], fill="#6594a4", width=2
            )
    ink.line(boundary + [boundary[0]], fill="#eff7f5", width=3, joint="curve")
    surface.putalpha(mask.filter(ImageFilter.GaussianBlur(0.45)))
    surface.save(output, "WEBP", quality=86, method=6)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("cache", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--thumbnail", type=Path)
    opts = parser.parse_args()
    main(opts.cache, opts.output)
    if opts.thumbnail:
        with Image.open(opts.output) as base:
            base.thumbnail((350, 350), Image.Resampling.LANCZOS)
            base.save(opts.thumbnail, quality=84, method=6)
