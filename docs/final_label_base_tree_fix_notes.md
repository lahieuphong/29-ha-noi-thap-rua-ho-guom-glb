# Final label/base/tree fix notes

Các chỉnh sửa trong bản này:

- Bảng chữ dùng lại phong cách cũ, đổi thành `THÁP RÙA - HỒ GƯƠM` có dấu tiếng Việt.
- Không dùng một mặt `doubleSided` cho chữ nữa; source tạo 2 mặt bảng riêng để khi xoay model chữ không bị lật/ngược.
- Chân bảng/bệ phụ đổi sang texture nước theo yêu cầu.
- Mặt đáy/side skirt dưới hồ được làm dày hơn và dùng texture nước, không dùng texture đá.
- Texture lá cây được sinh lại dày hơn: nhiều đốm lá nhỏ, gân lá và lớp sáng/tối.
- Geometry cây trong `src/glb_forge/trees.py` được tăng mật độ cụm tán, lá rời và lá rủ; các phần khác của model được giữ nguyên.

File source chính:

```text
src/glb_forge/scenes/thap_rua_ho_guom.py
src/glb_forge/trees.py
scripts/generate_textures.py
```
