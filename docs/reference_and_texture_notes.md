# Reference & Texture Notes

Bản nâng cấp này dùng nguồn online chỉ để tham khảo hình dáng/chất liệu tổng quát của Tháp Rùa: tháp nằm trên gò nhỏ giữa Hồ Gươm, có nhiều tầng thu nhỏ dần, cửa cuốn/vòm, mái cong, bề mặt cũ rêu phong và bóng phản chiếu trên nước.

Không có ảnh báo, ảnh du lịch hay ảnh trên web nào được copy vào texture. Tất cả file PNG trong `assets/textures/thap_rua_ho_guom/` là procedural texture tự sinh bằng `scripts/generate_textures.py`.

Các nhóm texture chính:

- `wall_old_plaster`: tường cũ vàng-xám, mảng mốc, vệt mưa, nứt nhỏ.
- `roof_old_tile`: mái ngói nâu đậm, đường hàng ngói, rêu/lichen nhẹ.
- `moss`: rêu xanh đậm/nhạt để phủ mảng cũ.
- `stone_crack`: đá xám, mạch vữa, nứt.
- `water`: nước Hồ Gươm xanh ngọc/xanh thẫm, gợn nhẹ.
- `grass_island`: cỏ đảo/gò Rùa.
- `mud_bank`: mép đất ẩm quanh đảo.
- `tree_leaf` và `tree_bark`: cây ven hồ.
- `tree_leaf_warm`: lá lộc vừng vàng/cam/đỏ nhẹ, dùng ít để phá đều tán xanh.
- `old_label`: bảng/biển cũ.
- `museum_label_vi_basecolor`: bảng tên kiểu cũ, có dấu `THÁP RÙA - HỒ GƯƠM`.

File GLB gốc không có UV map, nên code tạo `TEXCOORD_0` tự động bằng planar mapping theo normal của mặt. Đây là bản nâng cấp nhanh, đẹp hơn màu phẳng. Muốn giống ảnh chụp hơn nữa thì nên unwrap UV thủ công và thay texture bằng ảnh chụp/scan hợp pháp.


## Tree Upgrade Notes

Hàng cây cũ trong GLB nguồn là các khối thân/cụm lá đơn giản, nên bản này bỏ primitive cũ thuộc nhóm material `distant lakeside tree trunks`, `deep Hoan Kiem tree green`, `sunlit leaves`, `dark lakeside foliage`, `faint Hanoi lakeside silhouettes`, rồi sinh lại cây bằng `src/glb_forge/trees.py`.

Logic mới:

- Thân và cành là các frustum cong nhẹ, có taper để không còn thẳng đều.
- Tán lá là nhiều ellipsoid méo chồng lớp, có cụm tối/sáng riêng.
- Lá nhỏ dạng diamond ở viền tán giúp cây có chi tiết khi nhìn gần.
- Một ít lá vàng/cam gợi mùa lộc vừng quanh Hồ Gươm.
- Bụi ven kè được tạo từ nhiều cụm ellipsoid thay cho hộp chữ nhật.

Texture và mesh đều do code sinh ra; không có ảnh báo/ảnh du lịch nào được copy vào model.


## Bản fix cuối

- Bảng chữ chính hiện dùng `museum_label_vi_basecolor.png`, không dùng `title_plaque` cho mặt bảng.
- Đáy/side skirt và chân bảng dùng texture nước.
- Cây được tăng mật độ lá và texture lá.
