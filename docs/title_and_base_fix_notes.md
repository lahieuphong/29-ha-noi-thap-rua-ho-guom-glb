# Title & Base Fix Notes

Bản hiện tại chỉ sửa đúng các phần được yêu cầu sau khi kiểm tra preview:

```text
1. Bảng tên đổi thành: THÁP RÙA - HỒ GƯƠM
2. Lấy lại phong cách bảng chữ cũ, không dùng bảng title-plaque lớn nữa.
3. Chỉnh UV/mặt bảng để chữ không bị ngược/soi gương.
4. Mặt đáy và side skirt dưới hồ dày hơn, dùng texture nước thay vì texture đá.
5. Chân/bệ phụ của bảng dùng texture nước theo yêu cầu.
```

## Source đã sửa

```text
src/glb_forge/scenes/thap_rua_ho_guom.py
  - giữ bệ/bảng thấp cũ, bỏ chữ cũ không dấu
  - thêm _add_front_vietnamese_label(scene)
  - thêm _add_textured_label_quad(...) với UV riêng cho mặt chữ
  - sửa _add_subtle_lake_display_base(scene) để dày hơn và dùng water texture

scripts/generate_textures.py
  - thêm generate_vietnamese_label_texture()
  - sinh museum_label_vi_basecolor.png bằng Pillow để render Unicode tiếng Việt
```

## Texture chính của bảng

```text
assets/textures/thap_rua_ho_guom/museum_label_vi_basecolor.png
```

Texture bảng tên được tạo bằng code, không lấy ảnh từ báo/du lịch. Font hệ thống chỉ được dùng để render chữ vào ảnh, không đóng gói file font vào project.
