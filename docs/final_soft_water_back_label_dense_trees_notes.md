# Final small visual fix: soft water, blank rear label, denser trees

Các thay đổi ở vòng fix này chỉ áp dụng cho các phần người dùng chỉ ra, không đổi hình khối tháp và vật liệu chính.

## 1. Nước nền / đáy nước mềm hơn

- Bỏ nền nước chữ nhật gốc bằng `RECTANGULAR_BASE_WATER_MATERIALS`.
- Thêm mặt nước bo mềm bằng `_add_soft_lake_water_surface(scene)`.
- Dùng `water_underlay_soft_basecolor.png` cho mặt hồ bo mềm để mép không lộ vuông.
- Dùng `water_underside_soft_basecolor.png` cho đáy/side skirt; texture này có alpha fade để không lộ mảng xanh đậm vuông khi nhìn từ trên.
- Giảm alpha các material nước phụ:
  - `soft rounded transparent Ho Guom water`: alpha 0.23
  - `soft transparent lake water underside`: alpha 0.085
  - `soft transparent lake water side skirt`: alpha 0.11

## 2. Mặt sau bảng tên không còn chữ ngược

- Mặt trước vẫn dùng `museum_label_vi_basecolor.png` với chữ **THÁP RÙA - HỒ GƯƠM**.
- Mặt sau đổi sang `museum_label_blank_basecolor.png`, cùng style bảng cũ nhưng không có chữ.
- Không còn render chữ ở mặt sau, nên khi xoay model sẽ không thấy chữ soi gương.

## 3. Cây mềm và dày hơn

- Hàng cây chính tăng mật độ lên 16 cây.
- Thêm lớp cây nhỏ xen kẽ bằng `_add_lakeside_infill_tree` để khoảng trống bớt thưa.
- Tán cây dùng nhiều cụm ellipsoid méo, leaf cards oval và hanging leaves để giảm cảm giác khối vuông.
- Bụi thấp ven kè vẫn giữ organic shrub, không quay lại khối hộp.

## Output đã test

```text
output/29_ha_noi/thap_rua_ho_guom.glb
Vertices: 525,680
Materials: 54
Images embedded: 28 PNG
Textures embedded: 28
```
