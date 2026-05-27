# 29 - Hà Nội - Tháp Rùa Hồ Gươm - GLB

Project Python thuần để tạo file `.glb` cho **Tháp Rùa - Hồ Gươm, Hà Nội**

Output hiện tại:

```text
output/29_ha_noi/thap_rua_ho_guom.glb
```

## Thông Số Model

```text
Scene:        Thap_Rua_Ho_Guom_Hanoi
Vertices:     531,483
Materials:    52
Primitives:   44
UV/TEXCOORD:  có, tạo tự động bằng planar mapping
Images:       26 PNG nhúng trong GLB
Textures:     26 texture slots
Registry key: 29-ha-noi/thap-rua-ho-guom
```

## Cấu Trúc Chính

```text
assets/
└─ textures/
   └─ thap_rua_ho_guom/
      ├─ wall_old_plaster_basecolor.png
      ├─ wall_old_plaster_normal.png
      ├─ roof_old_tile_basecolor.png
      ├─ roof_old_tile_normal.png
      ├─ moss_basecolor.png
      ├─ moss_normal.png
      ├─ stone_crack_basecolor.png
      ├─ stone_crack_normal.png
      ├─ natural_pebble_basecolor.png
      ├─ natural_pebble_normal.png
      ├─ water_basecolor.png
      ├─ water_normal.png
      ├─ water_underside_soft_basecolor.png # giữ lại để tham khảo, không dùng trong bản revert nước
      ├─ water_underlay_soft_basecolor.png   # giữ lại để tham khảo, không dùng trong bản revert nước
      ├─ grass_island_basecolor.png
      ├─ grass_island_normal.png
      ├─ mud_bank_basecolor.png
      ├─ mud_bank_normal.png
      ├─ tree_leaf_basecolor.png
      ├─ tree_leaf_normal.png
      ├─ tree_leaf_warm_basecolor.png
      ├─ tree_leaf_warm_normal.png
      ├─ tree_bark_basecolor.png
      ├─ tree_bark_normal.png
      ├─ old_label_basecolor.png
      ├─ old_label_normal.png
      ├─ museum_label_vi_basecolor.png
      ├─ museum_label_blank_basecolor.png # mặt sau bảng tên, không có chữ
      ├─ title_plaque_basecolor.png       # giữ lại để tham khảo, không dùng trong bản fix này
      └─ title_plaque_normal.png          # giữ lại để tham khảo, không dùng trong bản fix này

src/glb_forge/
├─ scene.py                         # primitive + Material có hỗ trợ texture
├─ scene_writer.py                  # ghi GLB, nhúng PNG texture vào BIN chunk
├─ trees.py                         # cây ven Hồ Gươm procedural chi tiết
├─ build.py                         # luồng generate dùng chung
├─ scenes/
│  ├─ thap_rua_ho_guom.py           # đọc mesh GLB nhúng, tạo UV, map texture
│  └─ thap_rua_ho_guom_data.py      # dữ liệu GLB nguồn nén gzip + base64
└─ sites/
   ├─ models.py
   ├─ registry.py
   └─ provinces/
      └─ ha_noi.py

generators/
└─ 29_ha_noi/
   └─ thap_rua_ho_guom.py           # lệnh chạy riêng di tích này

scripts/
├─ generate_site.py                 # generate theo registry key
├─ generate_all.py                  # generate toàn bộ di tích đã đăng ký
└─ generate_textures.py             # sinh lại texture PNG; bảng chữ dùng Pillow để render Unicode
```

## Chạy Code

1. Vào thư mục project:

```bash
cd 29-ha-noi-thap-rua-ho-guom-glb
```

2. Project cần Python `>= 3.10`:

```bash
python3 --version
```

3. Generate file GLB:

```bash
python3 generators/29_ha_noi/thap_rua_ho_guom.py
```

Hoặc generate theo registry key:

```bash
python3 scripts/generate_site.py 29-ha-noi/thap-rua-ho-guom
```

Hoặc generate toàn bộ di tích đã đăng ký:

```bash
python3 scripts/generate_all.py
```

Kết quả nằm tại:

```text
output/29_ha_noi/thap_rua_ho_guom.glb
```

## Sinh Lại Texture

Texture đã được tạo sẵn trong `assets/textures/thap_rua_ho_guom/`. Nếu muốn sinh lại ảnh texture bằng Python:

```bash
python3 scripts/generate_textures.py
```

GLB generator dùng được ngay vì texture đã có sẵn. Nếu muốn sinh lại texture, script cần Pillow để render chữ Unicode tiếng Việt cho bảng tên. Có thể cài bằng:

```bash
python3 -m pip install Pillow
```

Không cần Blender/Numpy.

## Cách Map Texture

Trong `src/glb_forge/scenes/thap_rua_ho_guom.py`, các material của GLB được map vào texture như sau. Các material cây mới được thêm sau khi bỏ hàng cây cũ dạng hộp:

```python
MATERIAL_TEXTURES = {
    "aged grey yellow plaster": ("wall_old_plaster_basecolor.png", "wall_old_plaster_normal.png"),
    "old dark brown grey roof": ("roof_old_tile_basecolor.png", "roof_old_tile_normal.png"),
    # Các mảng xanh cũ trên thân tháp được bỏ khỏi geometry vì quá vuông.
    "dark stone gaps and cracks": ("stone_crack_basecolor.png", "stone_crack_normal.png"),
    "soft natural island pebbles": ("natural_pebble_basecolor.png", "natural_pebble_normal.png"),
    # Mặt nước và bệ nước quay lại kiểu cũ đã duyệt.
    "ho guom deep green water": ("water_basecolor.png", "water_normal.png"),
    "shallow jade water": ("water_basecolor.png", "water_normal.png"),
    "mature loc vung trunk bark": ("tree_bark_basecolor.png", "tree_bark_normal.png"),
    "deep loc vung foliage clusters": ("tree_leaf_basecolor.png", "tree_leaf_normal.png"),
    "warm yellow red loc vung seasonal leaves": ("tree_leaf_warm_basecolor.png", "tree_leaf_warm_normal.png"),
    "vietnamese front label texture": ("museum_label_vi_basecolor.png", None),
    "label water foot block": ("water_basecolor.png", "water_normal.png"),
    "thicker lake display water underside": ("water_basecolor.png", "water_normal.png"),
}
```

File GLB gốc không có UV map, nên project tự tạo `TEXCOORD_0` bằng planar mapping theo hướng mặt. Đây là cách nâng cấp nhanh để bề mặt có vân, rêu, loang màu, gợn nước. Muốn giống ảnh chụp hơn nữa thì bước tiếp theo nên unwrap UV thủ công hoặc dùng ảnh texture thật đã được cấp quyền sử dụng.