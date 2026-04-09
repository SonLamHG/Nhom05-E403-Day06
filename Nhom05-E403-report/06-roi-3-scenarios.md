# ROI 3 kịch bản - VinBiocare AI

Ước lượng ROI cho 3 trường hợp: conservative, realistic, optimistic. Mục tiêu không phải dự báo tuyệt đối chính xác, mà để trả lời câu hỏi: với phạm vi sản phẩm hiện tại, dự án có đáng tiếp tục build và pilot không?

---

## 1. Hệ thống hóa dự án

### Bài toán đang giải

- Người dùng khó tự đọc phiếu xét nghiệm và không biết chỉ số nào đáng lo.
- Nhân viên tư vấn hoặc điều dưỡng phải lặp lại phần giải thích sơ bộ cho nhiều ca giống nhau.
- Kết quả xét nghiệm thường đến dưới dạng ảnh/chụp màn hình, khó nhập lại thủ công.
- Nếu không có lớp validation rõ ràng, hệ thống AI dễ trả lời sai hoặc gây hiểu nhầm.

### Giải pháp hiện tại trong project

- Nhập chỉ số xét nghiệm theo text có cấu trúc.
- Upload ảnh xét nghiệm để OCR và chuẩn hóa về JSON.
- Rule-based engine để phân loại chỉ số, tạo summary, advice, triage.
- AI chat để giải thích lại kết quả theo ngôn ngữ dễ hiểu, có thể trả lời follow-up.
- So sánh 2 kết quả xét nghiệm gần nhất khi có history.
- Feedback like/dislike để thu thập correction log cho các lần cải thiện sau.
- Validation đầu vào để chặn input sai trước khi gọi LLM.

### Giá trị cốt lõi của demo

- Giảm thời gian giải thích sơ bộ cho các ca xét nghiệm phổ biến.
- Tăng khả năng nhận biết ca cần tái khám hoặc tư vấn chuyên khoa.
- Tạo trải nghiệm “đọc kết quả xét nghiệm dễ hiểu” cho người dùng cuối.
- Tạo vòng lặp dữ liệu thực tế qua feedback để tối ưu prompt, OCR và UX.

### Giới hạn hiện tại cần nhìn thẳng

- Mới phù hợp cho tư vấn sơ bộ, không phải công cụ chẩn đoán.
- Bộ chỉ số đang còn giới hạn, chưa bao phủ toàn bộ xét nghiệm bệnh viện.
- OCR hiện là lợi thế lớn cho demo, nhưng accuracy phải được đo trên phiếu thật trước pilot.
- ROI chỉ tốt nếu gắn với một flow thật: giảm thời gian vận hành hoặc tăng booking/tái khám.

---

## 2. ROI 3 kịch bản

Giả định chung để tính:

- Đơn vị thời gian: theo tháng.
- Giá trị 1 giờ nhân sự tư vấn/điều dưỡng: khoảng 120.000 VNĐ/giờ.
- Giá trị biên của 1 lịch khám/tái khám phát sinh: khoảng 250.000 VNĐ.
- Cost đã gồm OpenAI API, hosting cơ bản, monitoring và thời gian maintain tối thiểu.

|   | Conservative | Realistic | Optimistic |
|---|-------------|-----------|------------|
| **Assumption** | Pilot tại 1 phòng khám nhỏ, 250 phiếu xét nghiệm/tháng, 30% ca dùng AI, mỗi ca tiết kiệm 5 phút, phát sinh 4 lịch khám/tái khám mỗi tháng | Pilot tại 1 bệnh viện nhỏ hoặc 2 khoa, 600 phiếu/tháng, 55% ca dùng AI, mỗi ca tiết kiệm 7 phút, phát sinh 18 lịch khám/tái khám mỗi tháng | Mở rộng sang 1 bệnh viện + đối tác xét nghiệm, 1.500 phiếu/tháng, 70% ca dùng AI, mỗi ca tiết kiệm 8 phút, phát sinh 50 lịch khám/tái khám mỗi tháng |
| **Cost** | ~2,5 triệu VNĐ/tháng (API chat + OCR, hosting demo, theo dõi lỗi, vận hành part-time) | ~5 triệu VNĐ/tháng (API nhiều hơn, logging/monitoring tốt hơn, tinh chỉnh prompt, hỗ trợ pilot) | ~12 triệu VNĐ/tháng (volume cao hơn, OCR nhiều, QA dữ liệu, vận hành gần production) |
| **Benefit** | Tiết kiệm 75 ca x 5 phút = 6,25 giờ x 120.000 = 0,75 triệu; cộng 4 lịch khám x 250.000 = 1,0 triệu; tổng ~1,75 triệu/tháng | Tiết kiệm 330 ca x 7 phút = 38,5 giờ x 120.000 = 4,62 triệu; cộng 18 lịch khám x 250.000 = 4,5 triệu; tổng ~9,12 triệu/tháng | Tiết kiệm 1.050 ca x 8 phút = 140 giờ x 120.000 = 16,8 triệu; cộng 50 lịch khám x 250.000 = 12,5 triệu; tổng ~29,3 triệu/tháng |
| **Net** | ~-0,75 triệu VNĐ/tháng | ~+4,12 triệu VNĐ/tháng | ~+17,3 triệu VNĐ/tháng |

### Đọc bảng theo góc nhìn sản phẩm

- Kịch bản conservative cho thấy nếu chỉ dừng ở mức demo nhỏ, ROI có thể chưa dương ngay.
- Kịch bản realistic đã bắt đầu hợp lý nếu sản phẩm thật sự giảm thời gian tư vấn và kéo được một lượng tái khám nhỏ nhưng đều.
- Kịch bản optimistic cho thấy upside lớn nhất không nằm ở chatbot đơn thuần, mà ở việc gắn AI với OCR + triage + booking/tái khám.

### Lợi ích phụ chưa đưa vào bảng

- Giảm thời gian onboarding cho nhân sự mới vì có khung giải thích chuẩn.
- Tăng trải nghiệm người dùng khi đọc kết quả xét nghiệm tại nhà.
- Tạo correction log để cải thiện prompt, validation, OCR accuracy và trust của hệ thống.
- Có thể dùng làm lớp intake trước khi đẩy sang bác sĩ hoặc call center.

---

## 3. Kill criteria

Nên dừng pilot hoặc thu hẹp phạm vi nếu sau 6 đến 8 tuần xảy ra một trong các điều kiện sau:

- Tỷ lệ sử dụng thực tế dưới 35% số ca đủ điều kiện.
- OCR đọc đúng dưới 80% trên tối thiểu 50 phiếu xét nghiệm thực.
- Trên 30% ca cần người sửa tay trước khi có thể dùng kết quả.
- Lợi ích quy đổi ra tiền vẫn thấp hơn chi phí trong 2 tháng liên tiếp.
- Người dùng dislike hoặc sửa kết quả quá nhiều, cho thấy trust chưa đủ để tiếp tục mở rộng.

---

## 4. Kết luận: có đáng build không?

Có, nhưng nên định vị đúng.

VinBiocare AI đáng tiếp tục build nếu được xem là một assistant cho giải thích xét nghiệm sơ bộ, triage nhẹ và điều hướng tái khám; chưa nên định vị là công cụ chẩn đoán. Với feature hiện tại, hướng đi hợp lý nhất là tối ưu 4 thứ theo thứ tự:

1. Accuracy của structured input và OCR.
2. Validation chặt để không gọi LLM khi input còn bẩn.
3. Audit log và feedback review để cải thiện chất lượng phản hồi.
4. Gắn kết quả phân tích với CTA rõ ràng như so sánh kết quả, tái khám hoặc tư vấn chuyên khoa.

Nếu pilot đạt mức realistic trở lên, đây là một demo có khả năng bước tiếp thành sản phẩm nội bộ hoặc pilot với đối tác y tế.
