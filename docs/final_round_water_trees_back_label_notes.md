# Final round fix: water nền mềm hơn, cây dày hơn, mặt sau bảng trống

Các thay đổi trong vòng này chỉ tập trung vào các phần người dùng yêu cầu, giữ nguyên tháp, đảo, texture tường/mái và bảng chữ mặt trước.

## 1. Nền nước xanh đậm bị vuông

- Bỏ nền nước chữ nhật gốc bằng cách lọc material `ho guom deep green water`.
- Thêm mặt nước procedural `soft rounded transparent Ho Guom water` dạng superellipse bo mềm, chia vòng/ring thay vì một quad lớn.
- Tạo texture `water_underlay_soft_basecolor.png` có alpha fade ở rìa để khi nhìn từ trên không còn thấy mảng vuông cứng.
- Đáy/side skirt dùng `water_underside_soft_basecolor.png`, alpha BLEND, mép oval và mờ hơn.

## 2. Cây mềm và dày hơn

- Tăng mật độ hàng cây chính nhưng vẫn giữ khoảng thở.
- Thêm lớp cây xen kẽ nhỏ hơn bằng `_add_lakeside_infill_tree()`.
- Giảm cảm giác vuông bằng ellipsoid tán lá nhiều ring, normal mượt, lá oval và cụm lá chồng lớp.
- Texture lá dùng ô lá nhỏ hơn để tán nhìn dày hơn khi nhìn gần.

## 3. Mặt sau bảng tên

- Mặt trước vẫn dùng `museum_label_vi_basecolor.png` với chữ `THÁP RÙA - HỒ GƯƠM`.
- Mặt sau đổi sang `museum_label_blank_basecolor.png`, cùng style bảng cũ nhưng không có chữ, tránh chữ bị ngược khi xoay mô hình 3D.

## Output đã kiểm tra

```text
output/29_ha_noi/thap_rua_ho_guom.glb
Vertices: 525,680
Materials: 54
Primitives: 45
Images embedded: 28 PNG
Textures embedded: 28
```
