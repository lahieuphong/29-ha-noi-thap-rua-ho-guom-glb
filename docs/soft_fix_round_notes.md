# Ghi chú bản fix mềm hóa đá/cây/nước

Bản này chỉ chỉnh các phần được yêu cầu ở vòng cuối, các phần còn lại giữ nguyên:

- Bỏ các viên đá/hòn đất nhỏ dạng hộp trên thảm cỏ bằng cách lọc tam giác thấp của material `old light grey stone`.
- Dựng lại các viên đá trên cỏ bằng pebble/boulder bo tròn procedural, dùng `natural_pebble_basecolor.png` và `natural_pebble_normal.png`.
- Bỏ các mảng rêu xanh lá hình chữ nhật trên thân tháp (`green moss on old tower`, `dark damp moss`). Tường vẫn còn vân cũ/rêu nhẹ trong texture plaster.
- Mặt nước và side skirt/đáy nước dùng alpha BLEND trong GLB để nhìn trong mờ hơn.
- Tán cây tăng rings/segments, normal mượt hơn và thêm nhiều lá rời/lá chùm và lá rủ để giảm cảm giác vuông vức.
- Texture lá được sinh lại dày hơn: nhiều lá nhỏ, ít khe tối hơn, nhìn tán đặc hơn.

File source chính đã sửa:

```text
src/glb_forge/scenes/thap_rua_ho_guom.py
src/glb_forge/trees.py
src/glb_forge/scene_writer.py
scripts/generate_textures.py
```
