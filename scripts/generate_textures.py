from __future__ import annotations

import math
import random
import struct
import zlib
from pathlib import Path
from typing import Callable

PROJECT_ROOT = Path(__file__).resolve().parents[1]
TEXTURE_DIR = PROJECT_ROOT / "assets" / "textures" / "thap_rua_ho_guom"
SIZE = 256

RGBA = tuple[int, int, int, int]
HeightMap = list[list[float]]
Texture = tuple[list[list[RGBA]], HeightMap]


def _chunk(kind: bytes, data: bytes) -> bytes:
    return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)


def write_png(path: Path, pixels: list[list[RGBA]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    h = len(pixels)
    w = len(pixels[0])
    raw = bytearray()
    for row in pixels:
        raw.append(0)
        for r, g, b, a in row:
            raw.extend((r & 255, g & 255, b & 255, a & 255))
    out = bytearray(b"\x89PNG\r\n\x1a\n")
    out.extend(_chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 6, 0, 0, 0)))
    out.extend(_chunk(b"IDAT", zlib.compress(bytes(raw), 9)))
    out.extend(_chunk(b"IEND", b""))
    path.write_bytes(bytes(out))


def clamp(v: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, v))


def smooth(t: float) -> float:
    return t * t * (3 - 2 * t)


def mix(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def color_mix(a: tuple[int, int, int], b: tuple[int, int, int], t: float) -> tuple[int, int, int]:
    t = clamp(t)
    return (int(mix(a[0], b[0], t)), int(mix(a[1], b[1], t)), int(mix(a[2], b[2], t)))


def color_towards(a: tuple[int, int, int], b: tuple[int, int, int], t: float) -> tuple[int, int, int]:
    return color_mix(a, b, t)


def color_scale(a: tuple[int, int, int], s: float) -> tuple[int, int, int]:
    return tuple(max(0, min(255, int(c * s))) for c in a)  # type: ignore[return-value]


def make_noise(size: int, cell: int, seed: int) -> list[list[float]]:
    rng = random.Random(seed)
    gw = size // cell + 3
    gh = size // cell + 3
    grid = [[rng.random() for _ in range(gw)] for _ in range(gh)]
    out: list[list[float]] = []
    for y in range(size):
        gy = y / cell
        y0 = int(gy)
        fy = smooth(gy - y0)
        row: list[float] = []
        for x in range(size):
            gx = x / cell
            x0 = int(gx)
            fx = smooth(gx - x0)
            a = mix(grid[y0][x0], grid[y0][x0 + 1], fx)
            b = mix(grid[y0 + 1][x0], grid[y0 + 1][x0 + 1], fx)
            row.append(mix(a, b, fy))
        out.append(row)
    return out


def combine_noise(size: int, seed: int, cells: tuple[int, int, int] = (64, 24, 8)) -> list[list[float]]:
    n1 = make_noise(size, cells[0], seed)
    n2 = make_noise(size, cells[1], seed + 17)
    n3 = make_noise(size, cells[2], seed + 31)
    return [[clamp(n1[y][x] * 0.52 + n2[y][x] * 0.33 + n3[y][x] * 0.15) for x in range(size)] for y in range(size)]


def hash01(x: int, y: int, seed: int = 0) -> float:
    """Hash nhỏ cho texture procedural, tránh gọi Random trong từng pixel."""
    v = math.sin(x * 127.1 + y * 311.7 + seed * 74.7) * 43758.5453123
    return v - math.floor(v)


def blank(size: int) -> HeightMap:
    return [[0.0 for _ in range(size)] for _ in range(size)]


def crack_mask(size: int, seed: int, count: int) -> HeightMap:
    rng = random.Random(seed)
    mask = blank(size)
    for _ in range(count):
        x = rng.uniform(0, size - 1)
        y = rng.uniform(0, size - 1)
        angle = rng.uniform(-math.pi, math.pi)
        length = rng.randint(size // 8, size // 2)
        for _ in range(length):
            angle += rng.uniform(-0.22, 0.22)
            x += math.cos(angle) * rng.uniform(0.6, 1.8)
            y += math.sin(angle) * rng.uniform(0.6, 1.8)
            ix, iy = int(x), int(y)
            if ix < 1 or iy < 1 or ix >= size - 1 or iy >= size - 1:
                break
            for yy in range(iy - 1, iy + 2):
                for xx in range(ix - 1, ix + 2):
                    d = abs(xx - x) + abs(yy - y)
                    mask[yy][xx] = max(mask[yy][xx], clamp(1.0 - d * 0.45))
            if rng.random() < 0.035:
                bx, by = x, y
                ba = angle + rng.choice([-1, 1]) * rng.uniform(0.8, 1.35)
                for _ in range(rng.randint(8, 35)):
                    bx += math.cos(ba) * rng.uniform(0.7, 1.4)
                    by += math.sin(ba) * rng.uniform(0.7, 1.4)
                    ba += rng.uniform(-0.18, 0.18)
                    bix, biy = int(bx), int(by)
                    if 1 <= bix < size - 1 and 1 <= biy < size - 1:
                        mask[biy][bix] = max(mask[biy][bix], 0.7)
                    else:
                        break
    return mask


def normal_map(height: HeightMap, strength: float) -> list[list[RGBA]]:
    size = len(height)
    pixels: list[list[RGBA]] = []
    for y in range(size):
        row: list[RGBA] = []
        for x in range(size):
            l = height[y][(x - 1) % size]
            r = height[y][(x + 1) % size]
            u = height[(y - 1) % size][x]
            d = height[(y + 1) % size][x]
            nx = (l - r) * strength
            ny = (u - d) * strength
            nz = 1.0
            m = math.sqrt(nx * nx + ny * ny + nz * nz)
            nx, ny, nz = nx / m, ny / m, nz / m
            row.append((int((nx * 0.5 + 0.5) * 255), int((ny * 0.5 + 0.5) * 255), int((nz * 0.5 + 0.5) * 255), 255))
        pixels.append(row)
    return pixels


def tex_wall(size: int = SIZE) -> Texture:
    n = combine_noise(size, 100, (80, 32, 10))
    fine = combine_noise(size, 120, (28, 12, 5))
    cracks = crack_mask(size, 121, 14)
    rain = make_noise(size, 42, 122)
    pixels: list[list[RGBA]] = []
    h = blank(size)
    for y in range(size):
        row: list[RGBA] = []
        for x in range(size):
            stain = clamp((rain[0][x] - 0.55) * 2.3) * (0.3 + y / size * 0.7)
            moss = clamp((n[y][x] - 0.62) * 2.5) * clamp((y / size - 0.50) * 2.4)
            c = color_mix((188, 180, 146), (125, 126, 116), n[y][x] * 0.75)
            c = color_towards(c, (75, 68, 54), stain * 0.5)
            c = color_towards(c, (36, 94, 42), moss * 0.55)
            c = color_scale(c, 0.94 + fine[y][x] * 0.16)
            if cracks[y][x] > 0:
                c = color_towards(c, (30, 27, 22), cracks[y][x] * 0.85)
            h[y][x] = n[y][x] * 0.34 + fine[y][x] * 0.12 - cracks[y][x] * 0.5 + moss * 0.15 - stain * 0.12
            row.append((*c, 255))
        pixels.append(row)
    return pixels, h


def tex_roof(size: int = SIZE) -> Texture:
    n = combine_noise(size, 200, (64, 24, 8))
    pixels: list[list[RGBA]] = []
    h = blank(size)
    row_h, col_w = 28, 44
    for y in range(size):
        row: list[RGBA] = []
        for x in range(size):
            yy = y % row_h
            xx = (x + (y // row_h) * 19) % col_w
            seam = (1.0 if yy < 2 or yy > row_h - 3 else 0.0) + (1.0 if xx < 2 or xx > col_w - 3 else 0.0)
            curve = 0.5 + 0.5 * math.sin((xx / col_w) * math.tau)
            lichen = clamp((n[(y + 23) % size][(x + 31) % size] - 0.63) * 2.8)
            c = color_mix((65, 39, 24), (139, 86, 46), n[y][x] * 0.9)
            c = color_towards(c, (183, 127, 66), curve * 0.16)
            c = color_towards(c, (31, 27, 22), seam * 0.35)
            c = color_towards(c, (86, 100, 62), lichen * 0.42)
            h[y][x] = n[y][x] * 0.22 + curve * 0.13 - seam * 0.18 + lichen * 0.07
            row.append((*c, 255))
        pixels.append(row)
    return pixels, h


def tex_moss(size: int = SIZE) -> Texture:
    n = combine_noise(size, 300, (44, 16, 6))
    pixels: list[list[RGBA]] = []
    h = blank(size)
    for y in range(size):
        row: list[RGBA] = []
        for x in range(size):
            dry = n[(y + 39) % size][(x + 11) % size]
            c = color_mix((17, 66, 27), (94, 148, 54), n[y][x])
            c = color_towards(c, (25, 34, 19), clamp(0.45 - dry) * 0.7)
            c = color_towards(c, (132, 120, 68), clamp(dry - 0.76) * 0.45)
            h[y][x] = n[y][x] * 0.62 + dry * 0.16
            row.append((*c, 255))
        pixels.append(row)
    return pixels, h


def tex_stone(size: int = SIZE) -> Texture:
    n = combine_noise(size, 400, (72, 24, 8))
    cracks = crack_mask(size, 401, 20)
    pixels: list[list[RGBA]] = []
    h = blank(size)
    for y in range(size):
        row: list[RGBA] = []
        for x in range(size):
            mortar = 1.0 if x % 92 < 2 or y % 72 < 2 else 0.0
            c = color_mix((103, 103, 90), (168, 159, 129), n[y][x])
            c = color_towards(c, (43, 40, 34), mortar * 0.58)
            c = color_towards(c, (32, 29, 25), cracks[y][x] * 0.9)
            h[y][x] = n[y][x] * 0.35 - mortar * 0.28 - cracks[y][x] * 0.48
            row.append((*c, 255))
        pixels.append(row)
    return pixels, h


def tex_natural_pebble(size: int = SIZE) -> Texture:
    """Đá cuội tự nhiên cho các viên nhỏ trên cỏ: không có lưới gạch vuông."""
    n = combine_noise(size, 460, (76, 28, 9))
    fine = combine_noise(size, 472, (18, 7, 3))
    cracks = crack_mask(size, 461, 9)
    pixels: list[list[RGBA]] = []
    h = blank(size)
    for y in range(size):
        row: list[RGBA] = []
        for x in range(size):
            speckle = hash01(x, y, 462)
            c = color_mix((112, 108, 91), (178, 166, 130), n[y][x] * 0.78 + fine[y][x] * 0.22)
            c = color_towards(c, (77, 72, 60), clamp(0.28 - n[(y + 17) % size][(x + 29) % size]) * 0.42)
            c = color_towards(c, (218, 204, 160), clamp(speckle - 0.82) * 0.28)
            c = color_towards(c, (38, 35, 30), cracks[y][x] * 0.62)
            h[y][x] = n[y][x] * 0.28 + fine[y][x] * 0.22 - cracks[y][x] * 0.34 + speckle * 0.04
            row.append((*c, 255))
        pixels.append(row)
    return pixels, h


def tex_water(size: int = SIZE) -> Texture:
    n = combine_noise(size, 500, (96, 48, 18))
    pixels: list[list[RGBA]] = []
    h = blank(size)
    for y in range(size):
        row: list[RGBA] = []
        for x in range(size):
            r1 = math.sin(x * 0.13 + y * 0.04)
            r2 = math.sin(-x * 0.045 + y * 0.16 + 1.8)
            bright = clamp(r1 * 0.38 + r2 * 0.24 - 0.28)
            c = color_mix((19, 75, 72), (83, 137, 113), n[y][x] * 0.65 + 0.18)
            c = color_towards(c, (151, 189, 166), bright * 0.55)
            c = color_towards(c, (8, 40, 39), clamp(0.28 - n[y][x]) * 0.5)
            h[y][x] = 0.18 * r1 + 0.12 * r2 + n[y][x] * 0.12
            row.append((*c, 255))
        pixels.append(row)
    return pixels, h


def tex_water_underside_soft(size: int = SIZE) -> list[list[RGBA]]:
    """Đáy nước RGBA: tâm sâu nhẹ, rìa mờ dần để không lộ footprint vuông."""
    broad = combine_noise(size, 552, (128, 54, 20))
    mist = combine_noise(size, 566, (80, 32, 12))
    pixels: list[list[RGBA]] = []
    for y in range(size):
        row: list[RGBA] = []
        yf = (y + 0.5) / size * 2.0 - 1.0
        for x in range(size):
            xf = (x + 0.5) / size * 2.0 - 1.0
            d = math.sqrt(xf * xf + yf * yf)
            # Center mờ sâu, biên fade rộng nên mép hình học gần như tan vào mặt nước.
            fade = clamp(1.0 - smooth(clamp((d - 0.42) / 0.54)))
            wave = 0.5 + 0.5 * math.sin((x * 0.040 + y * 0.026) + broad[y][x] * 4.0)
            c = color_mix((14, 70, 67), (77, 132, 116), broad[y][x] * 0.56 + mist[y][x] * 0.22)
            c = color_towards(c, (167, 206, 190), clamp(wave - 0.68) * 0.24)
            c = color_towards(c, (10, 48, 48), clamp(0.30 - broad[y][x]) * 0.25)
            alpha = int(170 * fade)
            row.append((*c, alpha))
        pixels.append(row)
    return pixels





def generate_soft_water_underlay_texture(size: int = 512) -> None:
    """Texture nước dưới đáy có alpha mềm ở rìa, tránh hiện mảng vuông cứng."""
    n = combine_noise(size, 530, (160, 72, 30))
    mist = combine_noise(size, 548, (96, 42, 18))
    pixels: list[list[RGBA]] = []
    for y in range(size):
        row: list[RGBA] = []
        for x in range(size):
            u = x / (size - 1)
            v = y / (size - 1)
            dx = abs(u - 0.5) / 0.5
            dy = abs(v - 0.5) / 0.5
            # Superellipse fade: giữa rõ hơn, rìa tan mềm vào mặt nước trên.
            edge = 1.0 - (dx ** 4.0 + dy ** 4.0) ** 0.25
            edge = smooth(clamp(edge * 2.55 - 0.34))
            wave = 0.5 + 0.5 * math.sin((u * 6.2 + v * 1.4) * math.tau + n[y][x] * 1.5)
            wave2 = 0.5 + 0.5 * math.sin((u * -2.2 + v * 5.3) * math.tau + mist[y][x] * 2.1)
            c = color_mix((24, 100, 96), (116, 178, 156), n[y][x] * 0.48 + mist[y][x] * 0.28 + wave * 0.10)
            c = color_towards(c, (188, 221, 203), clamp(wave + wave2 - 1.28) * 0.18)
            # Alpha ở rìa gần 0 nên không còn đường biên vuông/sắc.
            alpha = int(210 * edge * (0.80 + 0.16 * wave + 0.08 * mist[y][x]))
            row.append((*c, max(0, min(255, alpha))))
        pixels.append(row)
    write_png(TEXTURE_DIR / "water_underlay_soft_basecolor.png", pixels)
    print("wrote water_underlay_soft_basecolor.png")


def tex_grass(size: int = SIZE) -> Texture:
    n = combine_noise(size, 600, (40, 14, 5))
    pixels: list[list[RGBA]] = []
    h = blank(size)
    for y in range(size):
        row: list[RGBA] = []
        for x in range(size):
            blade = 0.5 + 0.5 * math.sin(x * 0.56 + n[y][x] * 7.0)
            c = color_mix((39, 94, 27), (139, 177, 66), n[y][x] * 0.82 + blade * 0.18)
            c = color_towards(c, (18, 61, 23), clamp(0.34 - n[(y + 19) % size][x]) * 0.7)
            c = color_towards(c, (177, 199, 87), clamp(blade - 0.82) * 0.45)
            h[y][x] = n[y][x] * 0.42 + blade * 0.14
            row.append((*c, 255))
        pixels.append(row)
    return pixels, h


def tex_mud(size: int = SIZE) -> Texture:
    n = combine_noise(size, 700, (62, 22, 8))
    pixels: list[list[RGBA]] = []
    h = blank(size)
    for y in range(size):
        row: list[RGBA] = []
        for x in range(size):
            wet = n[(y + 41) % size][(x + 9) % size]
            c = color_mix((69, 51, 31), (137, 98, 52), n[y][x])
            c = color_towards(c, (28, 24, 20), clamp(0.45 - wet) * 0.55)
            c = color_towards(c, (108, 128, 63), clamp(wet - 0.70) * 0.28)
            h[y][x] = n[y][x] * 0.32 + wet * 0.18
            row.append((*c, 255))
        pixels.append(row)
    return pixels, h


def _hash01(a: int, b: int, seed: int) -> float:
    n = (a * 374761393 + b * 668265263 + seed * 1442695041) & 0xFFFFFFFF
    n = (n ^ (n >> 13)) * 1274126177 & 0xFFFFFFFF
    return ((n ^ (n >> 16)) & 0xFFFFFFFF) / 0xFFFFFFFF


def _leaf_field(x: int, y: int, *, size: int, seed: int, warm: bool = False) -> tuple[float, float, float]:
    """Trường lá nhỏ dạng ellipse chồng lớp: trả về leaf, vein, gap.

    Cách này giúp texture lá dày hơn: nhìn gần thấy nhiều mảng lá nhỏ, nhìn xa
    vẫn thành tán xanh liền mạch, hợp các cụm cây ven hồ.
    """
    # Lá nhỏ hơn và dày hơn so với bản trước để cụm cây không còn cảm giác
    # mảng xanh phẳng/vuông khi nhìn gần.
    cell_w = 10 if not warm else 9
    cell_h = 7 if not warm else 7
    gx = x // cell_w
    gy = y // cell_h
    leaf = 0.0
    vein = 0.0
    for yy in range(gy - 1, gy + 2):
        for xx in range(gx - 1, gx + 2):
            jx = _hash01(xx, yy, seed) - 0.5
            jy = _hash01(xx, yy, seed + 7) - 0.5
            cx = (xx + 0.52 + jx * 0.40) * cell_w
            cy = (yy + 0.52 + jy * 0.42) * cell_h
            angle = _hash01(xx, yy, seed + 13) * math.tau
            ca, sa = math.cos(angle), math.sin(angle)
            dx = x - cx
            dy = y - cy
            rx = ca * dx + sa * dy
            ry = -sa * dx + ca * dy
            ax = cell_w * (0.46 + _hash01(xx, yy, seed + 23) * 0.18)
            ay = cell_h * (0.36 + _hash01(xx, yy, seed + 31) * 0.16)
            shape = 1.0 - (rx / ax) ** 2 - (ry / ay) ** 2
            if shape > 0.0:
                val = smooth(clamp(shape))
                leaf = max(leaf, val)
                center_line = clamp(1.0 - abs(ry) / max(0.001, ay * 0.14)) * clamp(1.0 - abs(rx) / max(0.001, ax * 0.92))
                vein = max(vein, center_line * val)
    # Tối khe giữa lá để tán cây có độ sâu, không phẳng như mảng màu xanh.
    gap = clamp((1.0 - leaf) * 0.52)
    return leaf, vein, gap


def tex_leaf(size: int = SIZE) -> Texture:
    n = combine_noise(size, 800, (34, 13, 5))
    micro = combine_noise(size, 812, (12, 6, 3))
    pixels: list[list[RGBA]] = []
    h = blank(size)
    for y in range(size):
        row: list[RGBA] = []
        for x in range(size):
            leaf, vein, gap = _leaf_field(x, y, size=size, seed=801)
            dapple = 0.5 + 0.5 * math.sin(x * 0.19 + y * 0.11 + n[y][x] * 5.5)
            c = color_mix((13, 55, 22), (72, 137, 48), n[y][x] * 0.55 + leaf * 0.45)
            c = color_towards(c, (119, 173, 68), vein * 0.48 + clamp(dapple - 0.72) * 0.24)
            c = color_towards(c, (8, 38, 18), gap * 0.24)
            c = color_towards(c, (35, 92, 30), micro[y][x] * 0.20)
            h[y][x] = leaf * 0.60 + vein * 0.24 + n[y][x] * 0.12 - gap * 0.045
            row.append((*c, 255))
        pixels.append(row)
    return pixels, h


def tex_leaf_warm(size: int = SIZE) -> Texture:
    """Lá lộc vừng vàng/cam/đỏ nhẹ, dày hơn bằng nhiều lá nhỏ chồng lớp."""
    n = combine_noise(size, 840, (36, 13, 5))
    pixels: list[list[RGBA]] = []
    h = blank(size)
    for y in range(size):
        row: list[RGBA] = []
        for x in range(size):
            leaf, vein, gap = _leaf_field(x, y, size=size, seed=841, warm=True)
            band = 0.5 + 0.5 * math.sin((x + y * 0.35) * 0.18 + n[y][x] * 5.0)
            c = color_mix((128, 87, 32), (216, 158, 58), n[y][x] * 0.55 + leaf * 0.34 + band * 0.11)
            c = color_towards(c, (155, 55, 38), clamp(vein + band - 1.05) * 0.45)
            c = color_towards(c, (72, 104, 36), clamp(0.26 - n[(y + 21) % size][(x + 9) % size]) * 0.32)
            c = color_towards(c, (244, 202, 84), vein * 0.34)
            c = color_towards(c, (56, 40, 24), gap * 0.30)
            h[y][x] = leaf * 0.54 + vein * 0.24 + n[y][x] * 0.13 - gap * 0.07
            row.append((*c, 255))
        pixels.append(row)
    return pixels, h


def tex_bark(size: int = SIZE) -> Texture:
    n = combine_noise(size, 900, (46, 18, 6))
    pixels: list[list[RGBA]] = []
    h = blank(size)
    for y in range(size):
        row: list[RGBA] = []
        for x in range(size):
            groove = 0.5 + 0.5 * math.sin(x * 0.17 + n[y][x] * 5.0)
            c = color_mix((60, 39, 22), (132, 82, 42), n[y][x])
            c = color_towards(c, (24, 18, 13), clamp(0.42 - groove) * 0.85)
            c = color_towards(c, (155, 112, 62), clamp(groove - 0.82) * 0.35)
            h[y][x] = groove * 0.55 + n[y][x] * 0.18
            row.append((*c, 255))
        pixels.append(row)
    return pixels, h


def tex_label(size: int = SIZE) -> Texture:
    pixels, h = tex_wall(size)
    for y in range(size):
        for x in range(size):
            if size * 0.38 < y < size * 0.62:
                r, g, b, a = pixels[y][x]
                pixels[y][x] = (int(r * 0.88), int(g * 0.82), int(b * 0.62), a)
                h[y][x] += 0.07
    return pixels, h




def generate_vietnamese_label_texture() -> None:
    """Tạo bảng chữ kiểu cũ: THÁP RÙA - HỒ GƯƠM, có dấu tiếng Việt.

    Tỉ lệ ảnh ngang/dẹt hơn để map lên bảng cũ không bị kéo giãn quá mức.
    """
    try:
        from PIL import Image, ImageDraw, ImageFilter, ImageFont
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError(
            "scripts/generate_textures.py cần Pillow để render chữ tiếng Việt có dấu. "
            "Cài bằng: python3 -m pip install Pillow"
        ) from exc

    width, height = 2048, 128
    rng = random.Random(1976)
    img = Image.new("RGBA", (width, height), (52, 45, 34, 255))
    px = img.load()

    for y in range(height):
        for x in range(width):
            n = 0.5 + 0.5 * math.sin(x * 0.010 + y * 0.052 + 0.4)
            n = n * 0.50 + (0.5 + 0.5 * math.sin(x * 0.026 - y * 0.021)) * 0.25 + rng.random() * 0.25
            vignette = max(abs(x - width * 0.5) / (width * 0.5), abs(y - height * 0.5) / (height * 0.5))
            r, g, b = color_mix((38, 33, 27), (92, 78, 55), n * 0.78)
            r, g, b = color_towards((r, g, b), (18, 16, 14), clamp((vignette - 0.66) * 2.1))
            px[x, y] = (r, g, b, 255)

    draw = ImageDraw.Draw(img)
    for _ in range(120):
        y = rng.randint(12, height - 12)
        x0 = rng.randint(18, width - 100)
        x1 = min(width - 18, x0 + rng.randint(60, 320))
        a = rng.randint(14, 36)
        draw.line([(x0, y), (x1, y + rng.randint(-1, 1))], fill=(185, 162, 112, a), width=1)

    draw.rounded_rectangle((12, 10, width - 12, height - 10), radius=16, outline=(39, 31, 22, 255), width=7)
    draw.rounded_rectangle((22, 18, width - 22, height - 18), radius=12, outline=(171, 144, 88, 255), width=5)
    draw.rounded_rectangle((40, 33, width - 40, height - 33), radius=7, outline=(216, 191, 130, 150), width=2)

    title = "THÁP RÙA - HỒ GƯƠM"
    font_path = _find_vietnamese_font()
    if font_path is None:
        font = ImageFont.load_default()
    else:
        font = ImageFont.truetype(font_path, size=70)
        for size in range(82, 34, -2):
            candidate = ImageFont.truetype(font_path, size=size)
            bbox = draw.textbbox((0, 0), title, font=candidate, stroke_width=2)
            tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
            if tw <= int(width * 0.90) and th <= int(height * 0.64):
                font = candidate
                break

    bbox = draw.textbbox((0, 0), title, font=font, stroke_width=2)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    x = (width - tw) / 2 - bbox[0]
    y = (height - th) / 2 - bbox[1] - 1

    draw.text((x + 4, y + 5), title, font=font, fill=(12, 10, 8, 210), stroke_width=3, stroke_fill=(12, 10, 8, 180))
    draw.text((x, y), title, font=font, fill=(238, 218, 154, 255), stroke_width=2, stroke_fill=(74, 58, 32, 240))
    draw.text((x, y - 1), title, font=font, fill=(255, 242, 188, 96))
    img = img.filter(ImageFilter.UnsharpMask(radius=1.0, percent=90, threshold=2))
    TEXTURE_DIR.mkdir(parents=True, exist_ok=True)
    img.save(TEXTURE_DIR / "museum_label_vi_basecolor.png")
    print("wrote museum_label_vi_basecolor.png")


def generate_blank_label_back_texture() -> None:
    """Tạo mặt sau bảng tên: cùng style bảng cũ nhưng không có chữ."""
    try:
        from PIL import Image, ImageDraw, ImageFilter
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError(
            "scripts/generate_textures.py cần Pillow để render nền bảng sau. "
            "Cài bằng: python3 -m pip install Pillow"
        ) from exc

    width, height = 2048, 128
    rng = random.Random(1977)
    img = Image.new("RGBA", (width, height), (52, 45, 34, 255))
    px = img.load()

    for y in range(height):
        for x in range(width):
            n = 0.5 + 0.5 * math.sin(x * 0.011 + y * 0.047 + 0.8)
            n = n * 0.55 + (0.5 + 0.5 * math.sin(x * 0.028 - y * 0.018)) * 0.25 + rng.random() * 0.20
            vignette = max(abs(x - width * 0.5) / (width * 0.5), abs(y - height * 0.5) / (height * 0.5))
            r, g, b = color_mix((38, 33, 27), (88, 76, 54), n * 0.72)
            r, g, b = color_towards((r, g, b), (18, 16, 14), clamp((vignette - 0.66) * 2.1))
            px[x, y] = (r, g, b, 255)

    draw = ImageDraw.Draw(img)
    for _ in range(150):
        y = rng.randint(12, height - 12)
        x0 = rng.randint(16, width - 100)
        x1 = min(width - 16, x0 + rng.randint(50, 360))
        a = rng.randint(12, 34)
        draw.line([(x0, y), (x1, y + rng.randint(-1, 1))], fill=(178, 154, 105, a), width=1)

    draw.rounded_rectangle((12, 10, width - 12, height - 10), radius=16, outline=(39, 31, 22, 255), width=7)
    draw.rounded_rectangle((22, 18, width - 22, height - 18), radius=12, outline=(151, 124, 76, 220), width=5)
    draw.rounded_rectangle((40, 33, width - 40, height - 33), radius=7, outline=(196, 171, 112, 110), width=2)
    img = img.filter(ImageFilter.UnsharpMask(radius=1.0, percent=70, threshold=2))
    TEXTURE_DIR.mkdir(parents=True, exist_ok=True)
    img.save(TEXTURE_DIR / "museum_label_blank_basecolor.png")
    print("wrote museum_label_blank_basecolor.png")


def _title_normal_from_height(height: list[list[float]], strength: float = 5.0) -> list[list[RGBA]]:
    """Normal map cho ảnh chữ tỉ lệ chữ nhật."""
    hgt = len(height)
    wid = len(height[0])
    pixels: list[list[RGBA]] = []
    for y in range(hgt):
        row: list[RGBA] = []
        for x in range(wid):
            l = height[y][max(0, x - 1)]
            r = height[y][min(wid - 1, x + 1)]
            u = height[max(0, y - 1)][x]
            d = height[min(hgt - 1, y + 1)][x]
            nx = (l - r) * strength
            ny = (u - d) * strength
            nz = 1.0
            m = math.sqrt(nx * nx + ny * ny + nz * nz)
            nx, ny, nz = nx / m, ny / m, nz / m
            row.append((int((nx * 0.5 + 0.5) * 255), int((ny * 0.5 + 0.5) * 255), int((nz * 0.5 + 0.5) * 255), 255))
        pixels.append(row)
    return pixels


def _find_vietnamese_font() -> str | None:
    """Tìm font có hỗ trợ tiếng Việt. Không đóng gói font vào project."""
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf",
        "/Library/Fonts/Arial Unicode.ttf",
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
        "C:/Windows/Fonts/arialbd.ttf",
        "C:/Windows/Fonts/arial.ttf",
    ]
    for candidate in candidates:
        if Path(candidate).exists():
            return candidate
    return None


def save_title_plaque() -> None:
    """Tạo bảng tên tiếng Việt có dấu theo tỉ lệ bảng cũ: THÁP RÙA - HỒ GƯƠM.

    Texture dùng tỉ lệ ngang/dẹt hơn bản trước để khi map lên bảng cũ không bị
    kéo quá đà. Chữ được render bằng font hệ thống có hỗ trợ Unicode tiếng Việt.
    """
    try:
        from PIL import Image, ImageDraw, ImageFilter, ImageFont
    except ImportError as exc:  # pragma: no cover - chỉ xảy ra khi máy chưa cài Pillow
        raise RuntimeError(
            "scripts/generate_textures.py cần Pillow để render chữ tiếng Việt có dấu. "
            "Cài bằng: python3 -m pip install Pillow"
        ) from exc

    width, height = 2048, 144
    rng = random.Random(20260526)
    title = "THÁP RÙA - HỒ GƯƠM"

    img = Image.new("RGBA", (width, height), (34, 30, 24, 255))
    # Nền bảng cũ: đen nâu, có grain nhẹ, không dùng texture đá.
    for y in range(height):
        for x in range(width):
            n = int(9 * math.sin(x * 0.013 + y * 0.046) + 6 * math.sin(x * 0.031 - y * 0.029))
            grain = rng.randint(-5, 5)
            edge = min(x, width - 1 - x, y, height - 1 - y)
            vignette = -18 if edge < 10 else (-8 if edge < 22 else 0)
            r = max(0, min(255, 37 + n + grain + vignette))
            g = max(0, min(255, 33 + n + grain + vignette))
            b = max(0, min(255, 26 + int(n * 0.6) + grain + vignette))
            img.putpixel((x, y), (r, g, b, 255))

    draw = ImageDraw.Draw(img)
    border_outer = (177, 143, 76, 255)
    border_inner = (226, 201, 132, 255)
    shadow_line = (16, 14, 11, 255)
    draw.rounded_rectangle((14, 10, width - 15, height - 11), radius=16, outline=shadow_line, width=8)
    draw.rounded_rectangle((24, 18, width - 25, height - 19), radius=13, outline=border_outer, width=5)
    draw.rounded_rectangle((43, 34, width - 44, height - 35), radius=8, outline=border_inner, width=2)

    font_path = _find_vietnamese_font()
    if font_path is None:
        font = ImageFont.load_default()
    else:
        font_size = 80
        while font_size > 32:
            font = ImageFont.truetype(font_path, font_size)
            bbox = draw.textbbox((0, 0), title, font=font, stroke_width=2)
            tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
            if tw <= width - 170 and th <= height - 32:
                break
            font_size -= 2

    bbox = draw.textbbox((0, 0), title, font=font, stroke_width=2)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    x = (width - tw) / 2 - bbox[0]
    y = (height - th) / 2 - bbox[1] - 1

    shadow = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.text((x + 5, y + 5), title, font=font, fill=(0, 0, 0, 170), stroke_width=2, stroke_fill=(0, 0, 0, 150))
    shadow = shadow.filter(ImageFilter.GaussianBlur(2.0))
    img.alpha_composite(shadow)
    draw = ImageDraw.Draw(img)
    draw.text((x, y), title, font=font, fill=(248, 232, 178, 255), stroke_width=2, stroke_fill=(69, 49, 26, 255))
    draw.text((x, y - 1), title, font=font, fill=(255, 246, 205, 230), stroke_width=1, stroke_fill=(120, 90, 45, 170))

    img.save(TEXTURE_DIR / "title_plaque_basecolor.png")

    height_map = [[0.06 for _ in range(width)] for _ in range(height)]
    for yy in range(height):
        for xx in range(width):
            if xx < 24 or xx > width - 25 or yy < 18 or yy > height - 19:
                height_map[yy][xx] = 0.13
            if 43 <= xx <= width - 44 and (34 <= yy <= 37 or height - 38 <= yy <= height - 35):
                height_map[yy][xx] = 0.26
            if 34 <= yy <= height - 35 and (43 <= xx <= 46 or width - 47 <= xx <= width - 44):
                height_map[yy][xx] = 0.26

    text_mask = Image.new("L", (width, height), 0)
    md = ImageDraw.Draw(text_mask)
    md.text((x, y), title, font=font, fill=255, stroke_width=2, stroke_fill=200)
    mask_pixels = text_mask.load()
    for yy in range(height):
        for xx in range(width):
            if mask_pixels[xx, yy] > 0:
                height_map[yy][xx] = max(height_map[yy][xx], 0.42 * (mask_pixels[xx, yy] / 255.0))
    write_png(TEXTURE_DIR / "title_plaque_normal.png", _title_normal_from_height(height_map, strength=4.0))
    print("wrote title_plaque_basecolor.png + title_plaque_normal.png")


def save_pair(name: str, maker: Callable[[int], Texture], strength: float) -> None:
    pixels, h = maker(SIZE)
    write_png(TEXTURE_DIR / f"{name}_basecolor.png", pixels)
    write_png(TEXTURE_DIR / f"{name}_normal.png", normal_map(h, strength))
    print(f"wrote {name}_basecolor.png + {name}_normal.png")


def main() -> None:
    TEXTURE_DIR.mkdir(parents=True, exist_ok=True)
    save_pair("wall_old_plaster", tex_wall, 4.6)
    save_pair("roof_old_tile", tex_roof, 5.2)
    save_pair("moss", tex_moss, 4.0)
    save_pair("stone_crack", tex_stone, 4.8)
    save_pair("natural_pebble", tex_natural_pebble, 4.0)
    save_pair("water", tex_water, 2.3)
    generate_soft_water_underlay_texture()
    write_png(TEXTURE_DIR / "water_underside_soft_basecolor.png", tex_water_underside_soft(SIZE))
    print("wrote water_underside_soft_basecolor.png")
    save_pair("grass_island", tex_grass, 4.1)
    save_pair("mud_bank", tex_mud, 4.0)
    save_pair("tree_leaf", tex_leaf, 3.2)
    save_pair("tree_leaf_warm", tex_leaf_warm, 3.2)
    save_pair("tree_bark", tex_bark, 5.4)
    save_pair("old_label", tex_label, 4.4)
    generate_vietnamese_label_texture()
    generate_blank_label_back_texture()
    save_title_plaque()


if __name__ == "__main__":
    main()
