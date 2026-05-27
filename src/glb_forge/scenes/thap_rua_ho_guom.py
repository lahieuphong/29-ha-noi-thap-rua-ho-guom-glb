from __future__ import annotations

import base64
import gzip
import json
import math
import random
import struct

from pathlib import Path

from glb_forge.scene import SceneMesh, Vec2, Vec3, v_norm
from glb_forge.trees import TreeMaterials, add_hoan_kiem_lakeside_trees

from .thap_rua_ho_guom_data import EMBEDDED_GLB_GZIP_B64


# File GLB chỉ chứa dữ liệu mesh/material, không chứa lại mã nguồn procedural gốc.
# Vì vậy file này dựng lại SceneMesh bằng cách đọc trực tiếp geometry/material đã trích
# từ GLB, rồi đưa qua cùng writer Python như project mẫu.

_GLTF_MAGIC = 0x46546C67
_CHUNK_JSON = 0x4E4F534A
_CHUNK_BIN = 0x004E4942
_FLOAT = 5126
_UNSIGNED_SHORT = 5123
_UNSIGNED_INT = 5125
_TYPE_COMPONENTS = {
    "SCALAR": 1,
    "VEC2": 2,
    "VEC3": 3,
    "VEC4": 4,
}
_COMPONENT_FORMAT = {
    _FLOAT: "f",
    _UNSIGNED_SHORT: "H",
    _UNSIGNED_INT: "I",
}
_COMPONENT_SIZE = {
    _FLOAT: 4,
    _UNSIGNED_SHORT: 2,
    _UNSIGNED_INT: 4,
}



TexturePair = tuple[str | None, str | None]

TEXTURE_ROOT = Path(__file__).resolve().parents[3] / "assets" / "textures" / "thap_rua_ho_guom"

MATERIAL_TEXTURES: dict[str, TexturePair] = {
    "ho guom deep green water": ("water_basecolor.png", "water_normal.png"),
    "shallow jade water": ("water_basecolor.png", "water_normal.png"),
    "soft pale water ripples": ("water_basecolor.png", "water_normal.png"),
    "dark tower reflection on water": ("water_basecolor.png", "water_normal.png"),

    "wet dark island mud edge": ("mud_bank_basecolor.png", "mud_bank_normal.png"),
    "warm island earth bank": ("mud_bank_basecolor.png", "mud_bank_normal.png"),
    "go rua old grass": ("grass_island_basecolor.png", "grass_island_normal.png"),
    "shadowed lake island grass": ("grass_island_basecolor.png", "grass_island_normal.png"),
    "fresh grass tips": ("grass_island_basecolor.png", "grass_island_normal.png"),

    "aged grey yellow plaster": ("wall_old_plaster_basecolor.png", "wall_old_plaster_normal.png"),
    "worn light plaster edge": ("wall_old_plaster_basecolor.png", "wall_old_plaster_normal.png"),
    "old warm plaster patches": ("wall_old_plaster_basecolor.png", "wall_old_plaster_normal.png"),
    "cool grey old plaster patches": ("wall_old_plaster_basecolor.png", "wall_old_plaster_normal.png"),
    "slightly brighter arch rim": ("wall_old_plaster_basecolor.png", "wall_old_plaster_normal.png"),
    "black grey rain stains": ("wall_old_plaster_basecolor.png", "wall_old_plaster_normal.png"),

    "dark stone gaps and cracks": ("stone_crack_basecolor.png", "stone_crack_normal.png"),
    "old light grey stone": ("stone_crack_basecolor.png", "stone_crack_normal.png"),
    "distant shore stone": ("stone_crack_basecolor.png", "stone_crack_normal.png"),
    "soft natural island pebbles": ("natural_pebble_basecolor.png", "natural_pebble_normal.png"),

    "green moss on old tower": ("moss_basecolor.png", "moss_normal.png"),
    "dark damp moss": ("moss_basecolor.png", "moss_normal.png"),

    "old dark brown grey roof": ("roof_old_tile_basecolor.png", "roof_old_tile_normal.png"),
    "very dark roof ridge": ("roof_old_tile_basecolor.png", "roof_old_tile_normal.png"),
    "worn roof edge highlight": ("roof_old_tile_basecolor.png", "roof_old_tile_normal.png"),
    "aged roof tile strip 1": ("roof_old_tile_basecolor.png", "roof_old_tile_normal.png"),
    "aged roof tile strip 2": ("roof_old_tile_basecolor.png", "roof_old_tile_normal.png"),
    "aged roof tile strip 3": ("roof_old_tile_basecolor.png", "roof_old_tile_normal.png"),
    "aged roof tile strip 4": ("roof_old_tile_basecolor.png", "roof_old_tile_normal.png"),
    "aged roof tile strip 5": ("roof_old_tile_basecolor.png", "roof_old_tile_normal.png"),
    "dark aged roof finial": ("roof_old_tile_basecolor.png", "roof_old_tile_normal.png"),

    "faded Quy Son Thap plaque": ("old_label_basecolor.png", "old_label_normal.png"),
    # Giữ bảng đen cũ theo màu gốc; bỏ texture đá loang ở label thấp phía trước.
    "light label lettering": ("old_label_basecolor.png", "old_label_normal.png"),
    "front vietnamese old style plaque": ("museum_label_vi_basecolor.png", None),
    "thin old title board backing": (None, None),
    "old title brass trim": (None, None),
    "thicker lake display base underside": ("water_basecolor.png", "water_normal.png"),
    "thicker lake display water underside": ("water_basecolor.png", "water_normal.png"),
    # Giữ lại mặt nước/bệ nước bản cũ theo yêu cầu cuối.
    "soft transparent lake water underside": ("water_underside_soft_basecolor.png", "water_normal.png"),
    "soft transparent lake water side skirt": ("water_underside_soft_basecolor.png", "water_normal.png"),
    "vietnamese front label texture": ("museum_label_vi_basecolor.png", None),
    "blank rear title board texture": ("museum_label_blank_basecolor.png", None),
    "label water foot block": ("water_basecolor.png", "water_normal.png"),

    "distant lakeside tree trunks": ("tree_bark_basecolor.png", "tree_bark_normal.png"),
    "deep Hoan Kiem tree green": ("tree_leaf_basecolor.png", "tree_leaf_normal.png"),
    "sunlit leaves": ("tree_leaf_basecolor.png", "tree_leaf_normal.png"),
    "dark lakeside foliage": ("tree_leaf_basecolor.png", "tree_leaf_normal.png"),
    "faint Hanoi lakeside silhouettes": ("tree_leaf_basecolor.png", "tree_leaf_normal.png"),

    "mature loc vung trunk bark": ("tree_bark_basecolor.png", "tree_bark_normal.png"),
    "dark loc vung branch bark": ("tree_bark_basecolor.png", "tree_bark_normal.png"),
    "deep loc vung foliage clusters": ("tree_leaf_basecolor.png", "tree_leaf_normal.png"),
    "shadowed loc vung inner foliage": ("tree_leaf_basecolor.png", "tree_leaf_normal.png"),
    "sunlit loc vung leaf highlights": ("tree_leaf_basecolor.png", "tree_leaf_normal.png"),
    "warm yellow red loc vung seasonal leaves": ("tree_leaf_warm_basecolor.png", "tree_leaf_warm_normal.png"),
    "soft distant tree haze foliage": ("tree_leaf_basecolor.png", "tree_leaf_normal.png"),
}

LEGACY_TREE_MATERIALS = {
    "distant lakeside tree trunks",
    "deep Hoan Kiem tree green",
    "sunlit leaves",
    "dark lakeside foliage",
    "faint Hanoi lakeside silhouettes",
}

LEGACY_FRONT_LABEL_MATERIALS = {
    # Chỉ bỏ chữ cũ không dấu; giữ lại bệ/bảng thấp cũ để đúng form ban đầu.
    "light label lettering",
}

LEGACY_TOWER_GREEN_MOSS_MATERIALS = {
    # Các mảng xanh lá cũ trên thân tháp đang giống miếng chữ nhật dán lên tường.
    # Theo yêu cầu mới, bỏ hẳn các mảng này để mặt tường sạch và tự nhiên hơn.
    "green moss on old tower",
    "dark damp moss",
}

LOW_ISLAND_STONE_MATERIALS = {
    # Những viên đá/đất thấp trên thảm cỏ trong GLB gốc là các hộp vuông.
    # Ta bỏ phần hộp thấp đó và thay bằng boulder procedural bo tròn ở dưới.
    "old light grey stone",
}

TRANSPARENT_LAKE_WATER_MATERIALS = {
    "ho guom deep green water",
    "shallow jade water",
    "soft pale water ripples",
    "dark tower reflection on water",
}

LEGACY_SQUARE_WATER_UNDERLAY_MATERIALS = {
    # Lớp nước xanh lục phía dưới đảo trong GLB gốc là một mảng chữ nhật.
    # Giữ màu/texture nước cũ đã duyệt, nhưng bỏ hình chữ nhật này và vẽ lại
    # bằng footprint méo cong như viền cỏ để không còn cảm giác một ô vuông nằm dưới nước.
    "shallow jade water",
}


NATURAL_ISLAND_STONES: tuple[tuple[float, float, float, float, float], ...] = (
    (-10.72, 0.19, 2.13, 0.29, 0.22), (-10.62, 0.16, -0.33, 0.34, 0.30),
    (-10.17, 0.15, -2.51, 0.24, 0.27), (-9.96, 0.19, -1.31, 0.25, 0.18),
    (-9.94, 0.19, 1.33, 0.41, 0.33), (-9.88, 0.15, 3.85, 0.40, 0.20),
    (-9.14, 0.17, -4.83, 0.26, 0.34), (-8.85, 0.15, -3.92, 0.25, 0.34),
    (-8.60, 0.16, 4.64, 0.33, 0.26), (-8.51, 0.13, -6.13, 0.22, 0.20),
    (-7.65, 0.19, 5.86, 0.29, 0.28), (-7.26, 0.24, -7.01, 0.36, 0.24),
    (-6.58, 0.17, 7.12, 0.39, 0.38), (-5.65, 0.14, 7.14, 0.39, 0.29),
    (-5.43, 0.14, -7.77, 0.26, 0.23), (-4.24, 0.23, -7.54, 0.35, 0.30),
    (-3.88, 0.20, 8.78, 0.37, 0.18), (-2.90, 0.18, 9.29, 0.36, 0.23),
    (-2.48, 0.16, -8.41, 0.23, 0.37), (-1.85, 0.18, -8.58, 0.34, 0.31),
    (-1.28, 0.19, 9.58, 0.40, 0.29), (-0.45, 0.16, -8.98, 0.22, 0.18),
    (0.48, 0.20, 9.47, 0.39, 0.19), (1.42, 0.18, -9.05, 0.39, 0.21),
    (1.74, 0.19, 8.23, 0.29, 0.22), (2.59, 0.20, -8.70, 0.34, 0.18),
    (2.59, 0.23, 9.28, 0.41, 0.20), (3.96, 0.20, -8.78, 0.40, 0.29),
    (4.68, 0.20, 8.09, 0.23, 0.36), (5.02, 0.17, -7.12, 0.23, 0.29),
    (5.64, 0.20, 7.71, 0.20, 0.19), (7.05, 0.20, -6.29, 0.35, 0.32),
    (7.18, 0.17, -6.09, 0.39, 0.30), (7.42, 0.23, 6.24, 0.37, 0.25),
    (8.27, 0.16, 5.47, 0.27, 0.18), (8.91, 0.18, -4.32, 0.21, 0.25),
    (9.28, 0.24, 3.46, 0.39, 0.28), (9.44, 0.17, 4.77, 0.23, 0.31),
    (10.20, 0.20, -3.47, 0.28, 0.20), (10.70, 0.17, -2.75, 0.34, 0.38),
    (10.89, 0.17, 2.36, 0.32, 0.19), (10.89, 0.17, -1.05, 0.35, 0.24),
    (11.12, 0.13, 1.54, 0.28, 0.25), (11.22, 0.20, -0.10, 0.25, 0.19),
)

DARK_MATERIAL_WORDS = ("dark", "black", "shadowed", "damp", "stains", "gaps", "reflection")


def _texture_path(filename: str | None) -> str | None:
    if filename is None:
        return None
    return str(TEXTURE_ROOT / filename)


def _texture_pair_for_material(name: str) -> TexturePair:
    return MATERIAL_TEXTURES.get(name, (None, None))


def _add_tree_materials(scene: SceneMesh) -> TreeMaterials:
    """Material riêng cho hàng cây ven Hồ Gươm phiên bản chi tiết.

    Các material này dùng lại texture bark/leaf procedural, nhưng tint khác nhau để
    cây có lớp trong tối, lớp ngoài sáng và vài lá lộc vừng vàng-đỏ theo mùa.
    """

    return TreeMaterials(
        bark=scene.add_material(
            "mature loc vung trunk bark",
            (0.52, 0.32, 0.17, 1.0),
            roughness=0.90,
            base_color_texture=_texture_path("tree_bark_basecolor.png"),
            normal_texture=_texture_path("tree_bark_normal.png"),
            normal_scale=0.58,
        ),
        branch=scene.add_material(
            "dark loc vung branch bark",
            (0.34, 0.20, 0.11, 1.0),
            roughness=0.92,
            base_color_texture=_texture_path("tree_bark_basecolor.png"),
            normal_texture=_texture_path("tree_bark_normal.png"),
            normal_scale=0.55,
        ),
        foliage_deep=scene.add_material(
            "deep loc vung foliage clusters",
            (0.38, 0.68, 0.30, 1.0),
            roughness=0.86,
            base_color_texture=_texture_path("tree_leaf_basecolor.png"),
            normal_texture=_texture_path("tree_leaf_normal.png"),
            normal_scale=0.38,
        ),
        foliage_dark=scene.add_material(
            "shadowed loc vung inner foliage",
            (0.18, 0.39, 0.19, 1.0),
            roughness=0.91,
            base_color_texture=_texture_path("tree_leaf_basecolor.png"),
            normal_texture=_texture_path("tree_leaf_normal.png"),
            normal_scale=0.36,
        ),
        foliage_sunlit=scene.add_material(
            "sunlit loc vung leaf highlights",
            (0.55, 0.82, 0.34, 1.0),
            roughness=0.82,
            base_color_texture=_texture_path("tree_leaf_basecolor.png"),
            normal_texture=_texture_path("tree_leaf_normal.png"),
            normal_scale=0.34,
        ),
        foliage_warm=scene.add_material(
            "warm yellow red loc vung seasonal leaves",
            (0.94, 0.72, 0.32, 1.0),
            roughness=0.86,
            base_color_texture=_texture_path("tree_leaf_warm_basecolor.png"),
            normal_texture=_texture_path("tree_leaf_warm_normal.png"),
            normal_scale=0.34,
        ),
        foliage_haze=scene.add_material(
            "soft distant tree haze foliage",
            (0.20, 0.36, 0.24, 1.0),
            roughness=0.94,
            base_color_texture=_texture_path("tree_leaf_basecolor.png"),
            normal_texture=_texture_path("tree_leaf_normal.png"),
            normal_scale=0.25,
        ),
    )




def _add_quad_custom_uv(
    scene: SceneMesh,
    points: tuple[Vec3, Vec3, Vec3, Vec3],
    uvs: tuple[Vec2, Vec2, Vec2, Vec2],
    material: int,
    normal: Vec3,
) -> None:
    """Thêm quad với UV tự đặt, dùng cho bảng chữ để tránh bị lật/mirror."""
    base = len(scene.positions)
    scene.positions.extend(points)
    scene.normals.extend([normal, normal, normal, normal])
    scene.texcoords.extend(uvs)
    scene.indices_by_material[material].extend([base, base + 1, base + 2, base, base + 2, base + 3])


def _add_triangle_custom_uv(
    scene: SceneMesh,
    p0: Vec3,
    p1: Vec3,
    p2: Vec3,
    uv0: Vec2,
    uv1: Vec2,
    uv2: Vec2,
    material: int,
    normal: Vec3,
) -> None:
    base = len(scene.positions)
    n = v_norm(normal)
    scene.positions.extend([p0, p1, p2])
    scene.normals.extend([n, n, n])
    scene.texcoords.extend([uv0, uv1, uv2])
    scene.indices_by_material[material].extend([base, base + 1, base + 2])


def _organic_water_outline(
    *,
    center_x: float,
    center_z: float,
    half_x: float,
    half_z: float,
    segments: int,
    power: float,
    wobble: float,
) -> list[tuple[float, float]]:
    """Tạo outline nước cong/méo, không còn cạnh thẳng kiểu hình vuông.

    ``power`` gần 2 cho dáng oval; cao hơn một chút giữ được cảm giác mặt nước
    rộng như bản cũ nhưng các góc/cạnh mềm như đường viền đảo cỏ.
    """
    pts: list[tuple[float, float]] = []
    for i in range(segments):
        a = math.tau * i / segments
        c, s = math.cos(a), math.sin(a)
        sx = math.copysign(abs(c) ** (2.0 / power), c)
        sz = math.copysign(abs(s) ** (2.0 / power), s)
        ripple = (
            1.0
            + wobble * math.sin(a * 3.0 + 0.55)
            + wobble * 0.62 * math.sin(a * 7.0 - 1.20)
            + wobble * 0.34 * math.sin(a * 13.0 + 2.10)
        )
        pts.append((center_x + sx * half_x * ripple, center_z + sz * half_z * ripple))
    return pts


def _water_uv_for_outline(x: float, z: float, *, center_x: float, center_z: float, half_x: float, half_z: float) -> Vec2:
    # Dùng UV rộng như nước cũ, chỉ đổi footprint geometry nên texture không bị thay phong cách.
    return (0.5 + (x - center_x) / (half_x * 2.18), 0.5 + (z - center_z) / (half_z * 2.18))


def _add_curved_shallow_water_underlay(scene: SceneMesh) -> None:
    """Vẽ lại mảng nước xanh lục phía dưới đảo bằng mép cong như mặt cỏ.

    Đây là phần thay cho mảng ``shallow jade water`` chữ nhật của GLB gốc. Màu,
    alpha và texture vẫn là nước bản cũ; chỉ đổi outline để khi nhìn từ trên không
    còn thấy một hình vuông thô bên dưới mặt hồ.
    """
    material = scene.add_material(
        "shallow jade water",
        (0.105, 0.35, 0.30, 0.54),
        roughness=0.82,
        double_sided=True,
        base_color_texture=_texture_path("water_basecolor.png"),
        normal_texture=_texture_path("water_normal.png"),
        normal_scale=0.45,
    )
    center_x, center_z = 0.43, 1.38
    half_x, half_z = 19.45, 14.65
    segments = 168
    rings = 14
    outline = _organic_water_outline(
        center_x=center_x,
        center_z=center_z,
        half_x=half_x,
        half_z=half_z,
        segments=segments,
        power=2.72,
        wobble=0.030,
    )

    def point(r: float, seg: int) -> Vec3:
        ox, oz = outline[seg]
        x = center_x + (ox - center_x) * r
        z = center_z + (oz - center_z) * r
        # Rất nhẹ thôi để không làm thay đổi mặt nước cũ, chỉ tránh mặt phẳng cứng hoàn toàn.
        y = -0.038 + 0.010 * math.sin(x * 0.18 + z * 0.11) * (0.30 + 0.70 * r)
        return (x, y, z)

    center = (center_x, -0.038, center_z)
    first_ring: list[Vec3] = [point(1.0 / rings, s) for s in range(segments)]
    for s in range(segments):
        n = (s + 1) % segments
        p1 = first_ring[s]
        p2 = first_ring[n]
        _add_triangle_custom_uv(
            scene,
            center,
            p1,
            p2,
            (0.5, 0.5),
            _water_uv_for_outline(p1[0], p1[2], center_x=center_x, center_z=center_z, half_x=half_x, half_z=half_z),
            _water_uv_for_outline(p2[0], p2[2], center_x=center_x, center_z=center_z, half_x=half_x, half_z=half_z),
            material,
            (0.0, 1.0, 0.0),
        )

    previous = first_ring
    for ring in range(2, rings + 1):
        r = ring / rings
        current = [point(r, s) for s in range(segments)]
        for s in range(segments):
            n = (s + 1) % segments
            p0, p1 = previous[s], previous[n]
            p2, p3 = current[n], current[s]
            _add_quad_custom_uv(
                scene,
                (p0, p1, p2, p3),
                (
                    _water_uv_for_outline(p0[0], p0[2], center_x=center_x, center_z=center_z, half_x=half_x, half_z=half_z),
                    _water_uv_for_outline(p1[0], p1[2], center_x=center_x, center_z=center_z, half_x=half_x, half_z=half_z),
                    _water_uv_for_outline(p2[0], p2[2], center_x=center_x, center_z=center_z, half_x=half_x, half_z=half_z),
                    _water_uv_for_outline(p3[0], p3[2], center_x=center_x, center_z=center_z, half_x=half_x, half_z=half_z),
                ),
                material,
                (0.0, 1.0, 0.0),
            )
        previous = current


def _add_subtle_lake_display_base(scene: SceneMesh) -> None:
    """Giữ đáy/bệ nước dày, nhưng trả footprint đáy trong về hình vuông.

    Bản trước bo cong cả phần đáy trong suốt nên khi nhìn từ dưới xuất hiện một
    mảng trắng trong kiểu mặt nước bị tròn/oval. Theo yêu cầu mới, chỉ phần đáy
    trong suốt này được đưa về hình chữ nhật đúng theo mặt nước xanh bên dưới;
    các lớp nước/đảo/cây/bảng chữ khác giữ nguyên.
    """

    base = scene.add_material(
        "thicker lake display water underside",
        # Giữ alpha và texture nước như bản đã duyệt; chỉ đổi footprint geometry.
        (0.22, 0.54, 0.50, 0.38),
        roughness=0.52,
        double_sided=True,
        base_color_texture=_texture_path("water_basecolor.png"),
        normal_texture=_texture_path("water_normal.png"),
        normal_scale=0.24,
    )

    # Khớp với mặt nước xanh vuông gốc: material ``ho guom deep green water``
    # có bounds x [-25, 25], z [-19, 19]. Không đụng đến mảng nước cong dưới đảo.
    half_x, half_z = 25.0, 19.0
    y_top, y_bottom = -0.105, -0.70
    x0, x1 = -half_x, half_x
    z0, z1 = -half_z, half_z

    # Mặt đáy vuông/chữ nhật nhìn từ dưới.
    _add_quad_custom_uv(
        scene,
        ((x0, y_bottom, z0), (x1, y_bottom, z0), (x1, y_bottom, z1), (x0, y_bottom, z1)),
        ((0.0, 0.0), (8.0, 0.0), (8.0, 6.0), (0.0, 6.0)),
        base,
        (0.0, -1.0, 0.0),
    )

    # Bốn thành nước cũng theo cạnh vuông để không còn outline trắng bo cong.
    _add_quad_custom_uv(
        scene,
        ((x0, y_top, z0), (x1, y_top, z0), (x1, y_bottom, z0), (x0, y_bottom, z0)),
        ((0.0, 0.0), (8.0, 0.0), (8.0, 1.0), (0.0, 1.0)),
        base,
        (0.0, 0.0, -1.0),
    )
    _add_quad_custom_uv(
        scene,
        ((x1, y_top, z1), (x0, y_top, z1), (x0, y_bottom, z1), (x1, y_bottom, z1)),
        ((0.0, 0.0), (8.0, 0.0), (8.0, 1.0), (0.0, 1.0)),
        base,
        (0.0, 0.0, 1.0),
    )
    _add_quad_custom_uv(
        scene,
        ((x1, y_top, z0), (x1, y_top, z1), (x1, y_bottom, z1), (x1, y_bottom, z0)),
        ((0.0, 0.0), (6.0, 0.0), (6.0, 1.0), (0.0, 1.0)),
        base,
        (1.0, 0.0, 0.0),
    )
    _add_quad_custom_uv(
        scene,
        ((x0, y_top, z1), (x0, y_top, z0), (x0, y_bottom, z0), (x0, y_bottom, z1)),
        ((0.0, 0.0), (6.0, 0.0), (6.0, 1.0), (0.0, 1.0)),
        base,
        (-1.0, 0.0, 0.0),
    )

def _push_smooth_vertex(scene: SceneMesh, position: Vec3, normal: Vec3, uv: Vec2) -> int:
    index = len(scene.positions)
    scene.positions.append(position)
    scene.normals.append(v_norm(normal))
    scene.texcoords.append(uv)
    return index


def _add_rounded_natural_stone(
    scene: SceneMesh,
    *,
    x: float,
    z: float,
    ground_y: float,
    size_x: float,
    size_z: float,
    material: int,
    rng: random.Random,
) -> None:
    """Thay viên hộp vuông bằng boulder dẹt, méo tự nhiên.

    Đá chỉ là nửa elip nổi nhẹ khỏi cỏ, có mép không đều và normal mượt nên khi
    nhìn gần không còn cảm giác khối lập phương.
    """

    rx = size_x * rng.uniform(0.56, 0.78)
    rz = size_z * rng.uniform(0.56, 0.78)
    height = max(0.055, min(0.16, rng.uniform(0.065, 0.13) * (0.78 + (size_x + size_z))))
    center_y = ground_y + height * 0.18
    angle = rng.uniform(0.0, math.tau)
    ca, sa = math.cos(angle), math.sin(angle)
    segments = 18
    rings = 6
    phase = rng.uniform(0.0, math.tau)

    def rotate(px: float, pz: float) -> tuple[float, float]:
        return (px * ca - pz * sa, px * sa + pz * ca)

    def point(ring: int, seg: int) -> Vec3:
        # ring 0 nằm sát mặt đất, ring cuối là đỉnh bo tròn.
        t = ring / rings
        lat = t * (math.pi / 2.0)
        radial = math.cos(lat)
        y = ground_y + math.sin(lat) * height
        a = math.tau * seg / segments
        wobble = 1.0 + 0.18 * math.sin(a * 3.0 + phase) + 0.08 * math.sin(a * 7.0 + phase * 0.7 + ring)
        lx = math.cos(a) * rx * radial * wobble
        lz = math.sin(a) * rz * radial * wobble
        ox, oz = rotate(lx, lz)
        return (x + ox, y, z + oz)

    rings_pts: list[list[Vec3]] = []
    for r in range(rings + 1):
        rings_pts.append([point(r, s) for s in range(segments)])

    # Mặt bên bo tròn.
    for r in range(rings):
        for s in range(segments):
            j = (s + 1) % segments
            pts = (rings_pts[r][s], rings_pts[r][j], rings_pts[r + 1][j], rings_pts[r + 1][s])
            base = len(scene.positions)
            for p, uv in zip(pts, ((0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0))):
                # Normal x/z theo tâm, y hơi mạnh để đá sáng mềm như đá tự nhiên.
                nx = (p[0] - x) / max(rx, 1e-4)
                ny = 0.65 + (p[1] - ground_y) / max(height, 1e-4)
                nz = (p[2] - z) / max(rz, 1e-4)
                _push_smooth_vertex(scene, p, (nx, ny, nz), uv)
            scene.indices_by_material[material].extend([base, base + 1, base + 2, base, base + 2, base + 3])

    # Đỉnh nhỏ đóng lại, tránh mặt trên phẳng vuông.
    top = (x, ground_y + height * 1.02, z)
    top_ring = rings_pts[-1]
    for s in range(segments):
        j = (s + 1) % segments
        base = len(scene.positions)
        _push_smooth_vertex(scene, top, (0.0, 1.0, 0.0), (0.5, 0.5))
        _push_smooth_vertex(scene, top_ring[s], (0.0, 1.0, 0.0), (0.0, 0.0))
        _push_smooth_vertex(scene, top_ring[j], (0.0, 1.0, 0.0), (1.0, 0.0))
        scene.indices_by_material[material].extend([base, base + 1, base + 2])


def _add_natural_island_stones(scene: SceneMesh, seed: int) -> None:
    stone = scene.add_material(
        "soft natural island pebbles",
        (0.72, 0.68, 0.55, 1.0),
        roughness=0.91,
        base_color_texture=_texture_path("natural_pebble_basecolor.png"),
        normal_texture=_texture_path("natural_pebble_normal.png"),
        normal_scale=0.42,
    )
    rng = random.Random(seed + 9124)
    for x, top_y, z, size_x, size_z in NATURAL_ISLAND_STONES:
        # Đặt đá hơi thấp hơn mặt hộp cũ một chút để bám vào cỏ/bờ đất, không nổi như đồ chơi.
        ground_y = top_y - rng.uniform(0.035, 0.065)
        _add_rounded_natural_stone(
            scene,
            x=x + rng.uniform(-0.025, 0.025),
            z=z + rng.uniform(-0.025, 0.025),
            ground_y=ground_y,
            size_x=size_x,
            size_z=size_z,
            material=stone,
            rng=rng,
        )


def _without_low_island_stone_boxes(indices: list[int], positions: list[Vec3]) -> list[int]:
    """Bỏ các tam giác thuộc viên đá hộp thấp trên cỏ, giữ lại bệ/lan can tháp."""
    filtered: list[int] = []
    for i in range(0, len(indices), 3):
        tri = indices[i : i + 3]
        pts = [positions[index] for index in tri]
        if all(p[1] < 0.32 for p in pts):
            continue
        filtered.extend(tri)
    return filtered


def _add_textured_label_quad(
    scene: SceneMesh,
    *,
    x0: float,
    x1: float,
    y0: float,
    y1: float,
    z: float,
    material: int,
    normal_z: float,
) -> None:
    """Thêm mặt bảng chữ với UV không lật.

    Tạo riêng mặt trước và mặt sau thay vì dùng double-sided một mặt. Cách này
    tránh lỗi chữ bị soi gương khi người xem xoay model sang phía còn lại.
    """
    base = len(scene.positions)
    if normal_z < 0:
        scene.positions.extend([(x0, y0, z), (x0, y1, z), (x1, y1, z), (x1, y0, z)])
        scene.normals.extend([(0.0, 0.0, -1.0)] * 4)
        scene.texcoords.extend([(1.0, 1.0), (1.0, 0.0), (0.0, 0.0), (0.0, 1.0)])
    else:
        scene.positions.extend([(x0, y0, z), (x1, y0, z), (x1, y1, z), (x0, y1, z)])
        scene.normals.extend([(0.0, 0.0, 1.0)] * 4)
        scene.texcoords.extend([(1.0, 1.0), (0.0, 1.0), (0.0, 0.0), (1.0, 0.0)])
    scene.indices_by_material[material].extend([base, base + 1, base + 2, base, base + 2, base + 3])


def _add_front_vietnamese_label(scene: SceneMesh) -> None:
    """Lấy lại kiểu bảng chữ cũ, nhưng đổi thành tiếng Việt có dấu.

    Bảng dùng texture ``museum_label_vi_basecolor.png`` kiểu cũ: nền nâu đen,
    viền vàng, chữ vàng ngà. Mặt trước có chữ, mặt sau dùng nền bảng trống để
    không còn chữ soi gương khi xoay model.
    """

    plaque = scene.add_material(
        "thick dark stone label plaque",
        (0.35, 0.30, 0.23, 1.0),
        roughness=0.94,
        base_color_texture=_texture_path("old_label_basecolor.png"),
        normal_texture=_texture_path("old_label_normal.png"),
        normal_scale=0.30,
    )
    foot = scene.add_material(
        "label water foot block",
        (0.22, 0.50, 0.46, 1.0),
        roughness=0.82,
        base_color_texture=_texture_path("water_basecolor.png"),
        normal_texture=_texture_path("water_normal.png"),
        normal_scale=0.28,
    )
    text = scene.add_material(
        "vietnamese front label texture",
        (1.0, 1.0, 1.0, 1.0),
        roughness=0.78,
        double_sided=False,
        base_color_texture=_texture_path("museum_label_vi_basecolor.png"),
        normal_texture=None,
        normal_scale=0.0,
    )
    blank_back = scene.add_material(
        "blank rear title board texture",
        (1.0, 1.0, 1.0, 1.0),
        roughness=0.82,
        double_sided=False,
        base_color_texture=_texture_path("museum_label_blank_basecolor.png"),
        normal_texture=None,
        normal_scale=0.0,
    )

    # Khung bảng cũ, giữ dáng gọn hơn bản title-plaque lớn.
    scene.add_box((0.0, 0.39, -17.47), (9.70, 0.78, 0.22), plaque)
    # Chân bảng dày hơn và đổi sang texture nước theo yêu cầu.
    scene.add_box((0.0, 0.035, -17.34), (10.35, 0.22, 0.78), foot)
    scene.add_box((0.0, -0.105, -17.34), (10.65, 0.12, 0.92), foot)

    # Mặt trước có chữ; mặt sau chỉ dùng nền bảng trống để không còn chữ bị lật gương khi xoay model.
    _add_textured_label_quad(scene, x0=-4.55, x1=4.55, y0=0.14, y1=0.68, z=-17.595, material=text, normal_z=-1.0)
    _add_textured_label_quad(scene, x0=-4.55, x1=4.55, y0=0.14, y1=0.68, z=-17.345, material=blank_back, normal_z=1.0)

def _texture_color_factor(name: str, color: tuple[float, float, float, float], has_texture: bool) -> tuple[float, float, float, float]:
    """Nâng nhẹ tint để texture không bị nhân màu quá tối trong PBR."""
    if not has_texture:
        return color

    rgb = color[:3]
    max_channel = max(rgb)
    if max_channel <= 1e-6:
        return color

    lower_name = name.lower()
    target_max = 0.82
    if any(word in lower_name for word in DARK_MATERIAL_WORDS):
        target_max = 0.55
    if "water" in lower_name:
        target_max = 0.92
    if "light" in lower_name or "highlight" in lower_name or "sunlit" in lower_name:
        target_max = 0.95

    factor = target_max / max_channel
    alpha = color[3]
    if name in TRANSPARENT_LAKE_WATER_MATERIALS:
        # Quay lại độ trong/đậm của mặt nước bản cũ theo yêu cầu: giữ bề mặt nước
        # giống bản tham chiếu, không thay các phần khác của mô hình.
        alpha = min(alpha, 0.54)
        if "ripples" in lower_name or "reflection" in lower_name:
            alpha = min(alpha, 0.38)
    return (
        min(1.0, rgb[0] * factor),
        min(1.0, rgb[1] * factor),
        min(1.0, rgb[2] * factor),
        alpha,
    )


def _generate_planar_texcoords(positions: list[Vec3], normals: list[Vec3]) -> list[Vec2]:
    """Tạo UV tự động theo hướng mặt để dán texture lặp.

    GLB gốc không có UV. Cách này không thay thế UV thủ công, nhưng đủ để texture
    tường, mái, rêu, nước và cỏ có hạt/vân thay vì chỉ là màu phẳng.
    """
    if len(positions) != len(normals):
        raise ValueError("positions và normals phải có cùng độ dài để tạo UV.")

    min_x = min(p[0] for p in positions)
    min_y = min(p[1] for p in positions)
    min_z = min(p[2] for p in positions)

    # 0.34 tạo khoảng 3 UV units cho chiều cao tháp và nhiều vòng lặp cho mặt nước.
    scale = 0.34
    uvs: list[Vec2] = []
    for (x, y, z), (nx, ny, nz) in zip(positions, normals):
        ax, ay, az = abs(nx), abs(ny), abs(nz)
        if ay >= ax and ay >= az:
            u = (x - min_x) * scale
            v = (z - min_z) * scale
        elif ax >= az:
            u = (z - min_z) * scale
            v = (y - min_y) * scale
        else:
            u = (x - min_x) * scale
            v = (y - min_y) * scale
        uvs.append((u, v))
    return uvs


def _embedded_glb_bytes() -> bytes:
    compact = "".join(EMBEDDED_GLB_GZIP_B64.split())
    return gzip.decompress(base64.b64decode(compact))


def _parse_glb(glb: bytes) -> tuple[dict, bytes]:
    magic, version, length = struct.unpack_from("<III", glb, 0)
    if magic != _GLTF_MAGIC or version != 2 or length != len(glb):
        raise ValueError("Dữ liệu nhúng không phải GLB 2.0 hợp lệ.")

    offset = 12
    gltf_json: dict | None = None
    bin_blob: bytes | None = None

    while offset < len(glb):
        chunk_length, chunk_type = struct.unpack_from("<II", glb, offset)
        offset += 8
        chunk = glb[offset : offset + chunk_length]
        offset += chunk_length

        if chunk_type == _CHUNK_JSON:
            gltf_json = json.loads(chunk.decode("utf-8"))
        elif chunk_type == _CHUNK_BIN:
            bin_blob = chunk

    if gltf_json is None or bin_blob is None:
        raise ValueError("GLB thiếu JSON chunk hoặc BIN chunk.")
    return gltf_json, bin_blob


def _accessor_bytes(gltf: dict, bin_blob: bytes, accessor_index: int) -> tuple[bytes, dict]:
    accessor = gltf["accessors"][accessor_index]
    view = gltf["bufferViews"][accessor["bufferView"]]

    component_type = accessor["componentType"]
    component_size = _COMPONENT_SIZE[component_type]
    component_count = _TYPE_COMPONENTS[accessor["type"]]
    count = accessor["count"]

    byte_offset = view.get("byteOffset", 0) + accessor.get("byteOffset", 0)
    byte_length = component_size * component_count * count
    byte_stride = view.get("byteStride")

    if byte_stride is None or byte_stride == component_size * component_count:
        return bin_blob[byte_offset : byte_offset + byte_length], accessor

    # GLB hiện tại không dùng stride, nhưng giữ nhánh này để loader chắc hơn.
    packed = bytearray()
    item_size = component_size * component_count
    for i in range(count):
        start = byte_offset + i * byte_stride
        packed.extend(bin_blob[start : start + item_size])
    return bytes(packed), accessor


def _read_vec3_accessor(gltf: dict, bin_blob: bytes, accessor_index: int) -> list[Vec3]:
    raw, accessor = _accessor_bytes(gltf, bin_blob, accessor_index)
    if accessor["componentType"] != _FLOAT or accessor["type"] != "VEC3":
        raise TypeError("Accessor không phải FLOAT/VEC3.")
    return [tuple(values) for values in struct.iter_unpack("<3f", raw)]


def _read_scalar_accessor(gltf: dict, bin_blob: bytes, accessor_index: int) -> list[int]:
    raw, accessor = _accessor_bytes(gltf, bin_blob, accessor_index)
    if accessor["type"] != "SCALAR":
        raise TypeError("Accessor index không phải SCALAR.")
    fmt = _COMPONENT_FORMAT[accessor["componentType"]]
    return [value[0] for value in struct.iter_unpack(f"<{fmt}", raw)]


def create_thap_rua_ho_guom(seed: int = 42) -> SceneMesh:
    """Tạo scene Tháp Rùa - Hồ Gươm từ dữ liệu GLB đã trích.

    Tham số ``seed`` được giữ để cùng chữ ký với các scene procedural trong barem.
    Dữ liệu model gồm hồ nước, đảo cỏ, tháp, mái, vòm cửa, cây ven hồ và nhãn nền.
    """
    gltf, bin_blob = _parse_glb(_embedded_glb_bytes())
    mesh_index = gltf["nodes"][0]["mesh"]
    mesh = gltf["meshes"][mesh_index]
    scene = SceneMesh(mesh.get("name", "Thap_Rua_Ho_Guom_Hanoi"))

    for material in gltf.get("materials", []):
        name = material.get("name", "material")
        pbr = material.get("pbrMetallicRoughness", {})
        base_texture, normal_texture = _texture_pair_for_material(name)
        has_texture = base_texture is not None
        color = tuple(pbr.get("baseColorFactor", (1.0, 1.0, 1.0, 1.0)))
        scene.add_material(
            name,
            _texture_color_factor(name, color, has_texture),
            metallic=float(pbr.get("metallicFactor", 0.0)),
            roughness=float(pbr.get("roughnessFactor", 0.82)),
            double_sided=bool(material.get("doubleSided", True)),
            base_color_texture=_texture_path(base_texture),
            normal_texture=_texture_path(normal_texture),
            normal_scale=0.45,
        )

    first_primitive = mesh["primitives"][0]
    position_accessor = first_primitive["attributes"]["POSITION"]
    normal_accessor = first_primitive["attributes"]["NORMAL"]
    scene.positions = _read_vec3_accessor(gltf, bin_blob, position_accessor)
    scene.normals = _read_vec3_accessor(gltf, bin_blob, normal_accessor)
    scene.texcoords = _generate_planar_texcoords(scene.positions, scene.normals)

    material_names = [material.get("name", "material") for material in gltf.get("materials", [])]
    for primitive in mesh["primitives"]:
        material_index = int(primitive.get("material", 0))
        material_name = material_names[material_index] if material_index < len(material_names) else "material"
        if material_name in LEGACY_TREE_MATERIALS:
            # Bỏ hàng cây/cụm bụi cũ dạng hộp thấp-poly; thay bằng cây procedural mới ở dưới.
            scene.indices_by_material[material_index] = []
            continue
        if material_name in LEGACY_FRONT_LABEL_MATERIALS:
            # Bỏ bảng tên cũ không dấu/mỏng; thay bằng bảng tên tiếng Việt có dấu ở dưới.
            scene.indices_by_material[material_index] = []
            continue
        if material_name in LEGACY_TOWER_GREEN_MOSS_MATERIALS:
            # Bỏ các mảng xanh lá vuông trên thân tháp theo yêu cầu mới.
            scene.indices_by_material[material_index] = []
            continue
        if material_name in LEGACY_SQUARE_WATER_UNDERLAY_MATERIALS:
            # Mảng nước xanh dưới đảo là hình chữ nhật rõ cạnh; vẽ lại bằng mép cong ở dưới.
            scene.indices_by_material[material_index] = []
            continue
        indices = _read_scalar_accessor(gltf, bin_blob, primitive["indices"])
        if material_name in LOW_ISLAND_STONE_MATERIALS:
            indices = _without_low_island_stone_boxes(indices, scene.positions)
        scene.indices_by_material[material_index] = indices

    _add_curved_shallow_water_underlay(scene)
    _add_subtle_lake_display_base(scene)
    _add_front_vietnamese_label(scene)
    _add_natural_island_stones(scene, seed)

    tree_materials = _add_tree_materials(scene)
    add_hoan_kiem_lakeside_trees(scene, tree_materials, seed=seed)

    scene.validate()
    return scene


__all__ = ["create_thap_rua_ho_guom"]
