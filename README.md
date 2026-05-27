# 29 Hà Nội - Tháp Rùa Hồ Gươm GLB

Project Python thuần để tạo file `.glb` cho **Tháp Rùa - Hồ Gươm, Hà Nội** theo cùng barem/cấu trúc với project mẫu `35-ninh-binh-nha-co-trang-an-glb`.

Bản này là bản **nâng cấp có texture procedural + cây ven hồ chi tiết hơn + bảng tên tiếng Việt có dấu**: code tự dùng các ảnh PNG được sinh bằng Python để tạo bề mặt tường cũ, mái ngói, rêu, đá nứt, nước Hồ Gươm, cỏ đảo, cây xanh và bảng tên. Hàng cây/bụi cũ dạng khối hộp đã được thay bằng cây lộc vừng/banyan procedural: thân cong, cành chia nhánh, tán lá nhiều cụm không đều, lá highlight và một ít lá vàng-đỏ theo mùa. Bảng tên trước mô hình đã đổi thành **THÁP RÙA - HỒ GƯƠM**, đồng thời bệ/đáy được làm dày hơn để nhìn chắc khối. File output GLB nhúng texture trực tiếp vào GLB nên có thể mở độc lập.

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

## Nâng Cấp Cây Ven Hồ

Trong `src/glb_forge/trees.py`, hàng cây cũ được dựng lại bằng Python procedural:

```text
- thân cây cong nhẹ bằng nhiều nón cụt taper
- rễ nổi nhỏ ở chân cây
- cành chính chia hướng không đều
- tán lá tạo từ nhiều ellipsoid méo/chồng lớp
- lá rủ và lá highlight dạng oval mềm, không còn hình thoi vuông cạnh
- bụi thấp ven kè thay khối hộp bằng cụm shrub organic
- vài mảng lá vàng/cam gợi cây lộc vừng Hồ Gươm theo mùa
```

Có thể chỉnh mật độ/hình dáng trong hàm `add_hoan_kiem_lakeside_trees`.

## Bảng Tên, Cây Dày Hơn Và Mặt Nước Quay Lại Bản Cũ

Bản fix mới chỉ sửa các phần được yêu cầu: bảng chữ, đáy/bệ và texture cây. Các phần tháp, nước mặt hồ, đảo cỏ và vật liệu chính được giữ như bản trước.

```text
- lấy lại kiểu bảng chữ cũ, nhưng đổi chữ thành: THÁP RÙA - HỒ GƯƠM
- mặt trước bảng có chữ đúng chiều; mặt sau dùng texture trống museum_label_blank_basecolor.png nên không còn chữ bị ngược khi xoay 3D
- texture bảng chữ mặt trước: museum_label_vi_basecolor.png
- chân bảng/bệ phụ dùng texture nước thay vì texture đá
- mặt nước/bệ nước đã quay lại kiểu cũ đã duyệt: dùng water_basecolor.png và water_normal.png, không dùng lớp nước trắng quá trong
- texture lá cây được làm dày hơn, lá nhỏ/gân lá dày hơn
- hàng cây ven hồ có thêm lớp cây xen kẽ nhẹ hơn, tán oval mềm hơn để giảm cảm giác thưa/vuông/facet nhưng file không quá nặng
- các viên đá/đất vuông trên cỏ được thay bằng pebble/boulder bo tròn dùng natural_pebble texture
- bỏ các mảng xanh lá vuông trên thân tháp
```

Các hàm chính:

```python
_add_front_vietnamese_label(scene)
_add_subtle_lake_display_base(scene)
_add_natural_island_stones(scene, seed)
add_hoan_kiem_lakeside_trees(scene, tree_materials, seed=seed)
```

## Ghi Chú

- Project không cần Blender để generate GLB.
- File texture đã có sẵn; chỉ cần Pillow nếu muốn chạy lại `scripts/generate_textures.py` để render bảng chữ Unicode.
- Bảng chữ kiểu cũ nằm ở `assets/textures/thap_rua_ho_guom/museum_label_vi_basecolor.png`; mặt sau trống nằm ở `museum_label_blank_basecolor.png`.
- Texture trong project là procedural texture tự sinh, không copy ảnh báo/ảnh du lịch vào model.
- GLB không lưu lại mã nguồn Unity/procedural gốc, nên phần `scenes/thap_rua_ho_guom.py` là bản khôi phục từ dữ liệu mesh/material của GLB rồi nâng cấp texture bằng Python.


## Final water revert

- Giữ nguyên cây dày, bảng chữ mặt sau trống và các chỉnh sửa gần nhất.
- Chỉ quay lại bề mặt nước/bệ nước kiểu cũ đã duyệt: mặt hồ xanh có texture nước rõ hơn, không dùng lớp nước trắng quá trong.

## Curved water underlay fix

- Giữ nguyên bề mặt nước xanh lục như bản đã duyệt.
- Chỉ đổi phần mảng nước xanh nằm dưới đảo từ hình chữ nhật sang outline cong/méo nhẹ như viền mặt cỏ.
- Đáy/khối nước dày bên dưới ở bản này đã được trả về footprint vuông/chữ nhật để khớp với nền nước xanh vuông khi nhìn từ dưới.
- Không chỉnh cây, tháp, đảo, bảng chữ, đá và các texture khác.

## Square transparent underside fix

- Chỉ sửa riêng phần đáy trong suốt/trắng khi nhìn từ dưới.
- Footprint của đáy nước được trả về hình vuông/chữ nhật khớp với mặt nước xanh gốc: x [-25, 25], z [-19, 19].
- Giữ nguyên mảng nước xanh cong dưới đảo, cây, bảng chữ, tháp, đảo cỏ, đá và các texture còn lại.
