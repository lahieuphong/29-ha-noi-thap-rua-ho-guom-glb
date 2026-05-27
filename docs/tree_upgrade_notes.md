# Tree Upgrade Notes

Bản nâng cấp cây tập trung sửa phần nhìn giả trong hàng cây ven hồ. GLB nguồn có các thân cây thẳng và tán/bụi dạng khối, nên source mới bỏ các primitive cây cũ rồi sinh lại bằng Python.

## Ý tưởng tham khảo

- Hồ Gươm có nhiều cây lộc vừng; khi chuyển mùa, lá có thể vàng/đỏ trước khi rụng.
- Khu quanh Hồ Hoàn Kiếm cũng có cây cổ thụ/banyan lâu năm, vì vậy hàng cây không nên đều như mô hình block mà nên có thân cong, rễ nổi nhẹ và tán không đối xứng.
- Về kỹ thuật, cây procedural thường dùng thân/cành dạng trụ hoặc nón cụt taper, chia nhánh nhiều cấp, sau đó đặt cụm lá không đều theo nguyên tắc fractal/self-similar.

## Những gì source đã làm

```text
src/glb_forge/trees.py
  add_hoan_kiem_lakeside_trees()
    - tạo 12 cây chính ven bờ xa
    - tạo 7 cây silhouette nền
    - tạo 10 cụm bụi thấp organic
    - tạo thân cong/taper + rễ nổi + cành phân nhánh
    - tạo tán bằng nhiều cụm ellipsoid méo
    - thêm lá diamond và lá rủ
```

## Ghi chú bản quyền

Nguồn online chỉ được dùng để tham khảo đặc điểm tổng quát. Texture lá/vỏ cây và geometry cây đều được tạo bằng code, không copy ảnh từ web vào GLB.

## Bản fix mật độ lá mới

```text
- texture tree_leaf_basecolor.png được sinh lại bằng nhiều cụm lá nhỏ dạng ellipse
- tăng số cụm tán phụ cho cây chính
- tăng lá rời/leaf cards ở mép tán
- thêm cành con mảnh để thân cây bớt thẳng và bớt giả
- vẫn giữ vị trí cây và tổng bố cục như bản trước
```
