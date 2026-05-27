# Final water / tree / back label fix

Bản này chỉ sửa các phần người dùng yêu cầu ở vòng cuối:

- Làm mềm nền nước/đáy nước: đổi đáy nước thành material alpha thấp, không double-sided; side skirt bo cong bằng superellipse để không lộ hình vuông xanh đậm khi nhìn từ trên.
- Tạo `water_underside_soft_basecolor.png` có alpha fade mềm để mặt đáy nhìn trong mờ hơn.
- Giữ mặt trước bảng chữ `THÁP RÙA - HỒ GƯƠM`; mặt sau dùng `museum_label_blank_basecolor.png`, không còn chữ soi gương/ngược khi xoay model.
- Cây ven hồ được làm mềm hơn và dày hơn bằng thêm lớp cây xen kẽ nhẹ, tán oval, cụm lá và texture lá dày hơn.
- Các phần còn lại của tháp, đảo, bảng trước, đá/pebble và vật liệu chính giữ nguyên theo bản trước.

Generate thử thành công:

```text
Output: output/29_ha_noi/thap_rua_ho_guom.glb
Vertices: 525,680
Materials: 54
Images embedded: 28 PNG
Textures embedded: 28
```
