# Soft Stone, Transparent Water Base, Tower Green Patch, Tree Roundness Fix

Bản fix này chỉ chạm vào các phần được yêu cầu ở vòng sau:

```text
1. Đá/đất nhỏ trên thảm cỏ
   - Bỏ các viên hộp thấp của GLB gốc ở material `old light grey stone` khi y < 0.32.
   - Thêm lại 44 viên `soft natural island pebbles` bằng hình boulder bo tròn.
   - Texture mới: `natural_pebble_basecolor.png` và `natural_pebble_normal.png`.

2. Mảng xanh trên thân tháp
   - Bỏ geometry của `green moss on old tower` và `dark damp moss` vì các mảng này quá vuông.
   - Các texture/tường chính còn lại giữ nguyên.

3. Đáy/mặt bên nước
   - Material `thicker lake display water underside` dùng alpha 0.38.
   - `scene_writer.py` tự đặt `alphaMode: BLEND` cho material có alpha < 1.
   - Vẫn dùng texture nước, không dùng texture đá ở đáy.

4. Cây
   - Tán cây chuyển sang normal mượt theo ellipsoid thay vì normal phẳng từng mặt.
   - Tăng rings/segments cho các cụm lá.
   - Tăng lá rời, lá chùm và lá rủ để silhouette mềm hơn.
   - Texture `tree_leaf_basecolor.png` có lá nhỏ dày hơn.
```

Các phần khác như tháp, bảng chữ, mặt nước chính, đảo cỏ và bố cục giữ theo bản trước.
