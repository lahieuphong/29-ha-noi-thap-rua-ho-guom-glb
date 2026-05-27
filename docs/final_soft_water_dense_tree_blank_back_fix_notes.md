# Final soft-water / dense-tree / blank-back label fix

Các chỉnh sửa đúng theo yêu cầu mới:

- Đáy nước xanh đậm không còn là tấm vuông: chuyển sang footprint oval hữu cơ, alpha BLEND và texture `water_underside_soft_basecolor.png` có fade ở rìa.
- Nước chính được làm mềm texture hơn, giảm cảm giác ô/tile.
- Hàng cây ven hồ tăng mật độ so với bản trước: thêm cây xen kẽ, nhưng giữ vị trí ven bờ và không thay phần tháp/đảo.
- Tán cây dùng ellipsoid mềm, leaf-card oval và cụm lá dày hơn để bớt vuông vức.
- Bảng tên phía trước giữ chữ `THÁP RÙA - HỒ GƯƠM`; mặt sau dùng `museum_label_blank_basecolor.png`, không hiển thị chữ nữa nên không còn chữ ngược khi xoay model.
- Các phần khác giữ nguyên logic/material chính của bản trước.

Output đã generate thử:

```text
output/29_ha_noi/thap_rua_ho_guom.glb
Vertices: 525,680
Materials: 54
Images embedded: 28 PNG
Textures embedded: 28
```
