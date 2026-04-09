# Phân tích Failure Modes - VinBiocare AI

## 1. Top 3 Failure Modes nguy hiểm nhất

| # | Trigger | Hậu quả | Mitigation |
|---|---------|---------|------------|
| 1 | **Nhập sai đơn vị đo:** User nhập `100` cho Glucose nhưng quên đổi đơn vị (mg/dL vs mmol/L). | Rule-engine đánh giá ngưỡng sai, báo "Bình thường" (hoặc ngược lại). **User không biết**, tin tưởng mình an toàn. | **Phát hiện Outlier:** Cảnh báo nếu giá trị nằm ngoài range logic của đơn vị (VD: mmol/L hiếm khi > 30). Bắt buộc chọn đơn vị trên UI. |
| 2 | **LLM sinh lời khuyên sai (Hallucination):** Phản hồi của LLM bảo user "Nên ngưng dùng thuốc hạ huyết áp" khi thấy huyết áp thấp. | Hậu quả nguy hiểm sức khỏe trực tiếp. User tin AI hơn do có lời giải thích "có vẻ khoa học", **áp dụng sai cách**. | **Cứng hóa System Prompt:** Cấm AI đưa ra lời khuyên thay đổi phác đồ điều trị. **UI Disclaimer:** Luôn ghi "AI không thay thế bác sĩ". |
| 3 | **Thiếu context bệnh lý nền / thai kỳ:** User là phụ nữ mang thai hoặc có bệnh mãn tính, nhưng rule-engine dùng ngưỡng chung. | Phân loại sai lệch (VD: đường huyết thai kỳ có ngưỡng nghiêm ngặt hơn). **User không nhận thức được nguy hiểm**. | **Thêm Context Input:** Yêu cầu người dùng chọn "Có thai không / Có bệnh lý nền không" trước khi Analyze để đối chiếu đúng bảng. |

---

## 2. Phân tích mở rộng

### Severity × Likelihood Matrix

Xếp failure modes vào ma trận để ưu tiên mitigation:

```text
            Likelihood thấp          Likelihood cao
          ┌────────────────────┬────────────────────┐
Severity  │ FM2: LLM khuyên sai│ FM1: Sai đơn vị đo │
cao       │ FM3: Thiếu context │                    │
          │ (Monitor + plan)   │ (FIX NGAY)         │
          ├────────────────────┼────────────────────┤
Severity  │                    │                    │
thấp      │                    │                    │
          │                    │                    │
          └────────────────────┴────────────────────┘
```

**Phân tích chi tiết:** 
- **FM1 (Sai đơn vị đo)**: Likelihood cao (rất dễ gõ nhầm) + Severity cao (kết quả phân tích bị đảo lộn hoàn toàn). **Cần fix ngay bằng Validation rules**.
- **FM2 (LLM khuyên sai y tế)**: Likelihood thấp (do đã có prompt) nhưng Severity cực cao nếu xảy ra. Cần Monitor chặt chẽ.
- **FM3 (Thiếu context)**: Likelihood trung bình/thấp, Severity cao với các nhóm đặc biệt (như phụ nữ mang thai).

### Cascade Failure

Chuỗi hậu quả cho failure mode nguy hiểm nhất (**FM1: Sai đơn vị đo kết hợp FM2**):

```text
1. User bị tiểu đường, đo được Glucose 100 mmol/L (thực tế máy đo hiển thị mg/dL là bình thường).
2. Rule engine hiểu lầm là 100 mmol/L (chỉ số cực kỳ cao và đe dọa tính mạng) -> Báo động đỏ.
3. LLM nhận Context "Nguy hiểm", sinh ra lời khuyên "Bạn bị tiểu đường cấp tính, cần đi cấp cứu / chích Insulin ngay".
4. User hoang mang, tự tiêm thêm Insulin tại nhà.
5. User bị hạ đường huyết đột ngột -> Suy hô hấp, đưa đi cấp cứu thực sự.
```

Chuỗi dài **4 bước** trước khi có sự can thiệp của bác sĩ (người phát hiện lỗi). Hậu quả cuối cùng từ 1 nhầm lẫn UI dẫn đến thiệt hại tính mạng.

### Adversarial / Misuse Scenarios

| Scenario | Hậu quả | Phòng tránh |
|----------|---------|-------------|
| *User nhập prompt injection vào input* | AI trả lời sai mục đích (trở thành bot giải toán, hacker lộ System Prompt). | Dùng LLM Guardrails để chặn prompt injection. Bắt buộc filter từ khóa y tế. |
| *User spam request để tăng cost* | Cạn kiệt OpenAI API key budget, sập server backend do quá tải. | **Đáng phòng nhất:** Implement Rate Limiting (VD: 10 req/phút/IP) ở FastAPI. |
| *User dùng AI output làm bằng chứng sai* | Kiện cáo công ty vì "AI của công ty bảo tôi bình thường", rủi ro pháp lý. | Gắn Watermark/Disclaimer cứng trên file PDF/UI không thể ẩn: "Chỉ tham khảo". |

*Cần ưu tiên phòng tránh Spam Request (tốn chi phí thực)* và *Dùng AI làm bằng chứng sai (rủi ro pháp lý)* ở môi trường production thực tế.

### Các vấn đề Scale và Vận hành

1. **Failure mode nào sẽ xuất hiện ở scale lớn mà ở prototype không thấy?** 
   Sự đa dạng hóa của chuẩn phòng lab. Mỗi bệnh viện lưu PDF định dạng khác nhau, dùng tên khác nhau (VD: Fasting Blood Sugar vs Glucose). Khi user nhập data đa nguồn, Regex/Rule engine sẽ parse sai và fail diện rộng.
   
2. **Nếu product chạy 6 tháng không ai theo dõi, failure nào sẽ tệ dần theo thời gian (model drift)?** 
   Quy chuẩn y tế/Ngưỡng chẩn đoán y tế có thể thay đổi (WHO update ngưỡng mới cho tiểu đường). Các ngưỡng Hardcode trong `indicators.json` trở nên lỗi thời, khiến toàn bộ chẩn đoán bị sai lệch ngầm mà hệ thống không báo lỗi.
   
3. **Automation → augmentation có giảm được failure mode nào không?** 
   Có. Nếu hạ mức độ từ Automation (AI chẩn đoán trực tiếp cho bệnh nhân) sang Augmentation (AI tạo báo cáo nháp, **Bác sĩ duyệt** rồi mới gửi bệnh nhân), hệ thống sẽ triệt tiêu hoàn toàn **FM2 (LLM sinh lời sai)** và giảm thiểu **FM1**, vì bác sĩ sẽ có cơ hội kiểm tra và can thiệp trước khi kết quả đến tay bệnh nhân.
