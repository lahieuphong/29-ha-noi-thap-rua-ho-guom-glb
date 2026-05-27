# Round 9 fix: nước mềm hơn, cây dày hơn, mặt sau bảng không chữ

Các phần được chỉnh trong vòng này:

```text
1. Mảng nước xanh đậm/vuông:
   - giảm alpha của các plane ripple/reflection từ GLB gốc
   - tạo lại mặt nước mềm bằng mesh bo gợn nhẹ `_add_soft_lake_water_surface`
   - mặt đáy/side skirt dùng `water_underside_soft_basecolor.png` có alpha fade ở rìa

2. Cây ven hồ:
   - tăng hàng cây chính và cây xen kẽ để bớt thưa
   - thêm `_add_lakeside_infill_tree` cho cây nhỏ chen giữa
   - tăng độ mượt thân/cành/tán và dùng lá oval 12 cạnh
   - texture `tree_leaf_basecolor.png` được làm dày/lá nhỏ hơn

3. Bảng tên:
   - mặt trước giữ `THÁP RÙA - HỒ GƯƠM` đúng chiều
   - mặt sau dùng `museum_label_blank_basecolor.png`, không còn chữ bị ngược

Các phần còn lại giữ nguyên theo bản trước.
```
