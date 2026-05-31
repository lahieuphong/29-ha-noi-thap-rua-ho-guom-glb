# Tóm tắt tài liệu Tháp Rùa Hồ Gươm GLB

File này gom lại nội dung các ghi chú cũ trong `docs/` thành một tài liệu ngắn gọn. Root `README.md` vẫn là tài liệu chính của project.

## Mục tiêu

Project tạo mô hình `.glb` cho **Tháp Rùa - Hồ Gươm, Hà Nội** bằng Python thuần. Mô hình hiện tại kết hợp dữ liệu GLB nguồn nhúng sẵn với các phần procedural để cải thiện texture, nước, cây, đá và bảng tên.

Output chính:

```text
output/29_ha_noi/thap_rua_ho_guom.glb
```

Registry key:

```text
29-ha-noi/thap-rua-ho-guom
```

## Nguồn và texture

Ảnh tham chiếu chỉ dùng để hiểu đặc điểm tổng quát của Tháp Rùa: tháp nằm trên gò nhỏ giữa Hồ Gươm, có nhiều tầng thu nhỏ dần, cửa vòm, mái cũ, bề mặt rêu phong và nước xanh quanh đảo.

Không copy ảnh báo, ảnh du lịch hoặc ảnh web vào texture. Các file PNG trong `assets/textures/thap_rua_ho_guom/` là texture procedural sinh bằng `scripts/generate_textures.py`.

Nhóm texture chính:

- `wall_old_plaster`: tường cũ vàng xám, vệt mưa, mốc nhẹ, nứt nhỏ.
- `roof_old_tile`: mái ngói nâu đậm, hàng ngói, rêu/lichen nhẹ.
- `stone_crack` và `natural_pebble`: đá xám, vết nứt, đá cuội tự nhiên.
- `water`: nước Hồ Gươm xanh ngọc/xanh thẫm, gợn nhẹ.
- `grass_island` và `mud_bank`: cỏ đảo, gò đất và mép bùn ẩm.
- `tree_leaf`, `tree_leaf_warm`, `tree_bark`: lá xanh, lá lộc vừng vàng/cam/đỏ nhẹ và vỏ cây.
- `museum_label_vi_basecolor`: mặt trước bảng tên có chữ `THÁP RÙA - HỒ GƯƠM`.
- `museum_label_blank_basecolor`: mặt sau bảng tên, cùng phong cách nhưng không có chữ.

## Các chỉnh sửa đã gom lại

Các note cũ chủ yếu xoay quanh một số vòng chỉnh thị giác. Trạng thái cuối cùng được tóm tắt như sau:

- GLB nguồn không có UV map, nên code tự tạo `TEXCOORD_0` bằng planar mapping theo hướng mặt.
- Material của tường, mái, đá, nước, cỏ, bùn, cây và bảng được map sang texture procedural.
- Hàng cây cũ dạng hộp/low-poly được bỏ và thay bằng cây procedural trong `src/glb_forge/trees.py`.
- Cây mới có thân cong, rễ nổi nhẹ, cành phân nhánh, tán ellipsoid méo, leaf-card oval, lá rủ và một ít lá vàng đỏ gợi lộc vừng quanh Hồ Gươm.
- Các mảng rêu xanh vuông trên thân tháp bị loại khỏi geometry; cảm giác cũ/rêu nhẹ vẫn nằm trong texture tường.
- Đá/đất nhỏ dạng hộp trên cỏ được lọc bỏ và thay bằng boulder/pebble bo tròn procedural.
- Mảng `shallow jade water` hình chữ nhật dưới đảo được dựng lại bằng footprint cong, méo nhẹ để giảm cảm giác vuông cứng.
- Đáy/bệ nước `thicker lake display water underside` giữ footprint chữ nhật theo bản fix cuối, dùng texture nước và alpha trong suốt.
- Bảng tên mặt trước dùng chữ tiếng Việt có dấu `THÁP RÙA - HỒ GƯƠM`.
- Mặt sau bảng tên dùng texture trống để không còn chữ bị soi gương khi xoay model.
- Chân bảng và bệ phụ dùng texture nước theo yêu cầu các vòng fix trước.

## File code liên quan

```text
src/glb_forge/scenes/thap_rua_ho_guom.py
  Đọc GLB nhúng, map texture, lọc primitive cũ, thêm nước cong, bảng tên, đá tự nhiên và cây mới.

src/glb_forge/trees.py
  Sinh hàng cây ven Hồ Gươm procedural.

src/glb_forge/scene_writer.py
  Ghi GLB 2.0, nhúng texture PNG vào BIN chunk, bật alphaMode BLEND cho material có alpha < 1.

scripts/generate_textures.py
  Sinh lại toàn bộ texture procedural, bao gồm bảng chữ tiếng Việt bằng Pillow.
```

## Sinh lại texture

Texture đã có sẵn, không cần sinh lại để generate GLB. Nếu cần tạo lại texture:

```bash
python3 scripts/generate_textures.py
```

Script cần Pillow để render chữ Unicode tiếng Việt:

```bash
python3 -m pip install Pillow
```

## Ghi chú bảo trì

- Khi chỉnh material texture, cập nhật `MATERIAL_TEXTURES` trong `src/glb_forge/scenes/thap_rua_ho_guom.py`.
- Khi chỉnh mesh procedural, kiểm tra lại `scene.validate()` và generate thử GLB.
- Nếu cần giống ảnh chụp hơn, bước tiếp theo nên là unwrap UV thủ công hoặc dùng texture ảnh/scan có quyền sử dụng hợp lệ.