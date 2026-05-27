# Square transparent underside fix

Yêu cầu: chỉ sửa phần đáy trong suốt/trắng nhìn từ dưới để nó không còn bo cong như mặt nước, mà trở lại dạng vuông/chữ nhật khớp với nền nước xanh vuông.

Đã làm:

- Giữ nguyên mặt nước xanh lục và mảng nước cong dưới đảo.
- Giữ nguyên cây, bảng chữ, đảo cỏ, đá, tháp và toàn bộ texture đã duyệt.
- Chỉ sửa hàm `_add_subtle_lake_display_base()` trong `src/glb_forge/scenes/thap_rua_ho_guom.py`.
- Vật liệu `thicker lake display water underside` vẫn dùng texture nước và alpha như bản trước, nhưng geometry đổi từ organic outline sang hình chữ nhật x [-25, 25], z [-19, 19].
