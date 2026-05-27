# Curved water underlay fix

Bản này chỉ sửa phần nước theo yêu cầu cuối:

- Giữ mặt nước xanh lục/texture nước kiểu cũ đã duyệt.
- Bỏ mảng `shallow jade water` hình chữ nhật nằm dưới đảo.
- Vẽ lại mảng nước đó bằng footprint cong, méo nhẹ như viền mặt cỏ để không còn cảm giác một hình vuông nằm dưới nước.
- Đáy/side skirt nước dày bên dưới cũng dùng outline cong, không còn 4 cạnh thẳng dạng hộp.
- Các phần khác như tháp, đảo, cây, đá, bảng chữ và mặt sau bảng được giữ nguyên.

File chính đã sửa:

```text
src/glb_forge/scenes/thap_rua_ho_guom.py
```

Hàm liên quan:

```python
_add_curved_shallow_water_underlay(scene)
_add_subtle_lake_display_base(scene)
```
