# CookieCooking Wiki

Chào mừng đến với Wiki chính thức của **CookieCooking**! Đây là một plugin nấu ăn chạy trên nền tảng **PySpigot**, mang đến trải nghiệm nhập vai nấu nướng cực kỳ chân thực với 4 trạm nấu ăn (Cooking Stations) tương tác trực tiếp bằng Hologram và GUI.

---

## 🌟 1. Tổng Quan Hệ Thống

CookieCooking hỗ trợ tích hợp sâu với các plugin item tùy chỉnh. Bạn có thể sử dụng các item từ:
*   **Vanilla Minecraft** (`minecraft ITEM_ID`)
*   **MMOItems** (`mmoitems TYPE:ID`)
*   **CraftEngine** (`craftengine KEY:ID`)
*   **NeigeItems** (`neigeitems ID`)

Hệ thống cung cấp 4 trạm làm việc chính:
1.  **Thớt (Chopping Board):** Dùng dao thái nguyên liệu trên thớt.
2.  **Chảo (Wok):** Xào nấu nguyên liệu với các mức lửa khác nhau, có thể bị cháy hoặc sống.
3.  **Cối Xay (Grinder):** Xay nghiền vật phẩm theo thời gian thực.
4.  **Nồi Hấp (Steamer):** Hấp thực phẩm với cơ chế cần nước (Moisture) và nhiên liệu (Fuel).

---

## 🛠️ 2. Cài Đặt & Lệnh Cơ Bản

### Lệnh (Commands)
Tất cả các lệnh đều bắt đầu bằng `/cookiecooking` hoặc `/cook`.

*   `/cook reload`: Tải lại cấu hình (Config.yml) và tất cả công thức (Recipes).
*   `/cook clear`: Xóa các thực thể Item Display bị lỗi ở gần người chơi (bán kính 0.5 block).
*   `/cook hand`: Xem thông tin NBT của vật phẩm đang cầm trên tay (hữu ích cho debug/làm recipe).

### Permissions (Quyền)
Bạn cần cấp các quyền sau cho người chơi hoặc staff:

*   **Lệnh Admin:**
    *   `cookiecooking.command.reload`: Quyền dùng lệnh reload.
    *   `cookiecooking.command.clear`: Quyền xóa hologram lỗi.
    *   `cookiecooking.command.hand`: Quyền xem thông tin vật phẩm.
*   **Tương tác Trạm (Stations):**
    *   `cookiecooking.choppingboard.interaction`: Quyền đặt/lấy đồ trên thớt.
    *   `cookiecooking.choppingboard.cut`: Quyền dùng dao cắt.
    *   `cookiecooking.wok.interaction`: Quyền xem thông tin/đặt đồ vào chảo.
    *   `cookiecooking.wok.stirfry`: Quyền dùng sạn đảo đồ trong chảo.
    *   `cookiecooking.wok.serveout`: Quyền dùng bát múc đồ ăn ra.
    *   `cookiecooking.grinder.interaction`: Quyền sử dụng cối xay.
    *   `cookiecooking.steamer.interaction`: Quyền mở GUI nồi hấp.
    *   `cookiecooking.steamer.addmoisture`: Quyền thêm nước vào nồi hấp.
    *   `cookiecooking.steamer.addfuel`: Quyền thêm củi/đốt lò dưới nồi hấp.
*   **Quyền theo Công thức (Recipe):** Bạn có thể gán quyền riêng cho từng công thức trong các file YAML (ví dụ: `chop.use`, `fry.use`).

---

## 🔪 3. Thớt (Chopping Board)

**Block mặc định:** `OAK_LOG` (Gỗ sồi) - *Có thể đổi trong Config.yml*
**Dụng cụ yêu cầu:** `IRON_AXE` (Rìu sắt đóng vai trò làm Dao)

**Cơ chế:**
1. Cầm nguyên liệu (VD: Thịt bò) -> `Shift + Chuột trái` vào thớt để đặt lên.
2. Cầm Dao (`IRON_AXE`) -> `Shift + Chuột trái` vào thớt nhiều lần để cắt.
3. Khi đủ số nhát cắt, nguyên liệu mới sẽ tự rớt ra.
4. *Lưu ý:* Có tỉ lệ bị đứt tay (mất máu) khi cắt! Nhấp `Chuột phải` tay không để lấy đồ ra nếu không muốn cắt nữa.

**Cách tạo Recipe (ChoppingBoard.yml):**
```yaml
# Item đầu vào (Namespace ITEM_ID)
minecraft BEEF:
  # Số nhát dao cần để cắt xong
  Count: 5
  # Danh sách Item đầu ra theo định dạng: "Namespace ITEM_ID Số_Lượng Tỉ_Lệ_Rớt(%)"
  Output:
  - minecraft COOKED_BEEF 1 90
  - minecraft BONE 1 15
  # Độ bền dao bị trừ mỗi nhát cắt (Mặc định: 1)
  Durability: 2
  # Quyền để cắt món này (Không bắt buộc)
  Permission: "chop.use"
  # Ghi đè cài đặt rủi ro đứt tay (Không bắt buộc)
  Damage:
    Chance: 12  # 12% bị đứt tay
    Value: 2    # Mất 2 máu
```

---

## 🍳 4. Chảo (Wok)

**Block mặc định:** `IRON_BLOCK` (Khối sắt)
**Dụng cụ yêu cầu:** `IRON_SHOVEL` (Xẻng sắt đóng vai trò làm Sạn/Vá)
**Nguồn nhiệt (Bên dưới chảo):** Cấp 1 (`CAMPFIRE`), Cấp 2 (`MAGMA_BLOCK`), Cấp 3 (`LAVA`).

**Cơ chế:**
1. Cầm nguyên liệu -> `Shift + Chuột phải` vào chảo để bỏ vào.
2. Cầm Sạn (`IRON_SHOVEL`) -> `Shift + Chuột trái` vào chảo để đảo đều.
3. Nếu đảo đủ số lần yêu cầu, dùng Bát (Bowl) -> `Shift + Chuột phải` để múc ra.
4. *Lưu ý:* Nếu không đảo trong một khoảng thời gian (Timeout), thức ăn sẽ biến thành món khét (`BURNT`). Nếu múc ra khi chưa đảo đủ, sẽ ra món sống (`RAW`). Lửa càng lớn làm món ăn phức tạp nhưng cũng dễ cháy nếu không chú ý.

**Cách tạo Recipe (Wok.yml):**
```yaml
# Item kết quả khi nấu thành công (Namespace ITEM_ID)
minecraft COOKED_BEEF:
  # Tổng số lần đảo (Stir) yêu cầu cho toàn bộ món ăn. Có thể để 1 số hoặc khoảng "min-max"
  Count: "10-14"
  # Cấp độ lửa yêu cầu (1=Campfire, 2=Magma, 3=Lava)
  HeatControl: 2
  # Số lượng món ăn ra lò
  Amount: 2
  # Độ sai số (Cho phép bạn đảo dư/thiếu vài nhát so với công thức mà vẫn thành công)
  FaultTolerance: 2
  # Nguyên liệu cần thiết (Ghi theo thứ tự cho dễ nhìn, bỏ vào chảo theo thứ tự nào cũng được)
  # Định dạng: Namespace ITEM_ID Số_lượng_cần Số_nhát_đảo_cần (có thể để range)
  Item:
  - minecraft BEEF 1 5-7
  - minecraft CARROT 1 3-4
  # Kết quả nếu nấu thất bại (thiếu lửa/chưa chín)
  RAW: minecraft BEEF
  # Kết quả nếu nấu khét (để quá lâu không đảo / đảo lố tay)
  BURNT: minecraft CHARCOAL
  # Quyền nấu món này
  Permission: "fry.use"
```

---

## ⚙️ 5. Cối Xay (Grinder)

**Block mặc định:** `GRINDSTONE` (Đá mài)

**Cơ chế:**
1. Cầm nguyên liệu -> `Shift + Chuột trái` vào Cối xay để bỏ vào.
2. Máy sẽ tự động chạy (xuất hiện particle và có âm thanh). Màn hình sẽ hiện đếm ngược thời gian.
3. Hết thời gian, đồ sẽ tự động rớt ra. Không thể nhét thêm đồ khi máy đang chạy.

**Cách tạo Recipe (Grinder.yml):**
```yaml
# Item đầu vào
minecraft WHEAT:
  # Danh sách Output: "Namespace ITEM_ID Số_Lượng Tỉ_Lệ_Rớt(%)"
  Output:
  - minecraft SUGAR 2 100
  # Thời gian xay (Giây)
  GrindingTime: 5
  # Quyền sử dụng
  Permission: "grinder.use"
```

---

## 🫕 6. Nồi Hấp (Steamer)

**Block mặc định:** `BARREL` (Thùng)
**Nguồn nhiệt yêu cầu (Bên dưới nồi):** Lò nung (`FURNACE`) hoặc Lò hun khói (`SMOKER`)

**Cơ chế phức tạp:**
Steamer hoạt động bằng giao diện GUI và yêu cầu tài nguyên duy trì: **Moisture (Nước/Hơi ẩm)** và **Steam (Hơi nước)**.
1. **Tiếp củi (Nhiệt độ):** Cầm Than/Gỗ -> `Shift + Chuột phải` vào Lò Nung bên dưới nồi để nạp nhiên liệu (thời gian cháy). Lò nung phải đang cháy thì Nồi mới hoạt động.
2. **Tiếp nước (Moisture):** Cầm Xô Nước/Chai Nước -> `Shift + Chuột phải` vào Nồi Hấp (`BARREL`) để bơm Moisture.
3. Nồi hấp sẽ tự động đun nóng Nước (Moisture) thành Hơi nước (Steam) nếu lò bên dưới đang cháy.
4. `Shift + Chuột phải` (tay không) vào Lò nung để xem thông tin: Thời gian cháy còn lại, Lượng Moisture, Lượng Steam, % Nấu chín.
5. `Shift + Chuột phải` vào Nồi Hấp (khi Lò đang cháy) để mở GUI. Đặt đồ sống vào GUI, đóng lại, và đợi nó hấp chín dần. Lượng hơi nước (Steam) sẽ bị tiêu hao dần để làm chín thức ăn.

*(Cài đặt Fuel và Moisture được định nghĩa trong `Config.yml` chứ không nằm trong file Recipe)*

**Cách tạo Recipe (Steamer.yml):**
```yaml
# Item đầu vào
minecraft POTATO:
  # Item đầu ra
  Output: minecraft BAKED_POTATO
  # Lượng Steam (Hơi nước) cần để làm chín. Steam càng cao, hấp càng lâu.
  Steam: 60
  # Quyền sử dụng
  Permission: "steam.use"
```

---

## 📝 7. Một Số Lưu Ý Cho Admin/Dev

1. **Namespace:** Tuyệt đối không quên ghi Namespace (ví dụ: `minecraft `) trước tên Item. Khoảng trắng rất quan trọng: `minecraft APPLE`.
2. **Reload Plugin:** Sau khi chỉnh sửa file `.yml`, luôn chạy lệnh `/jk reload` để áp dụng. Đôi khi nếu cấu hình sai nghiêm trọng, recipe sẽ không được load (kiểm tra console logs).
3. **Lỗi Hologram:** Nếu đập phá Block Trạm khi đang nấu bị kẹt dòng chữ lơ lửng, hãy đứng sát vị trí đó và gõ `/jk clear`.
4. **Việt Hóa:** Mọi tin nhắn (Messages) và Hologram (Actionbar, Title) đều có thể được Việt hóa và tùy chỉnh màu sắc bằng chuẩn MiniMessage (ví dụ: `<red>`, `<gradient:blue:green>`) trong file `Config.yml`.
