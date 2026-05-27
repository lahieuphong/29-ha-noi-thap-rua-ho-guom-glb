# Soft Water + Dense Tree + Blank Label Back Fix

Bản fix này chỉ chỉnh các phần người dùng yêu cầu, các phần còn lại giữ nguyên từ bản trước.

## Nội dung sửa

```text
1. Nền nước xanh đậm phía dưới:
   - bỏ mặt đáy chữ nhật đậm trước đó
   - thay bằng underside nước dạng elip lượn nhẹ, alpha thấp
   - cập nhật water texture mềm hơn, hạn chế cảm giác tile/ô vuông

2. Cây ven hồ:
   - tăng mật độ hàng cây chính từ 12 lên 17 cây
   - thêm cây nền nhẹ vào khe giữa để hàng cây bớt thưa
   - tán cây dùng lá oval, texture lá dày/mịn hơn
   - giữ bố cục ven hồ, không sửa tháp/đảo/bảng trước

3. Bảng chữ:
   - mặt trước giữ nguyên chữ: THÁP RÙA - HỒ GƯƠM
   - mặt sau chuyển thành nền bảng trống, không còn hiển thị chữ ngược
```

## File source chính đã sửa

```text
src/glb_forge/scenes/thap_rua_ho_guom.py
src/glb_forge/trees.py
scripts/generate_textures.py
README.md
```

## Output kiểm tra

```text
output/29_ha_noi/thap_rua_ho_guom.glb
Vertices: 538,821
Materials: 52
Primitives: 44
Images embedded: 25 PNG
```
