# Demo script — 5 phút trình bày + 5 phút Q&A

Cấu trúc demo cho demo round. Tổng 10 phút/nhóm: 5 phút trình bày + 5 phút Q&A từ peer và GV. Mỗi người trong nhóm nói ít nhất 1 phần.

---

## Structure (5 phút trình bày)

| Phần | Thời gian | Nội dung | Ai nói |
|------|-----------|----------|--------|
| **Problem + Before** | 45 giây | Bệnh nhân nhận kết quả xét nghiệm nhưng 70% không hiểu → chờ 3-7 ngày gặp BS → lo lắng không cần thiết. Flow cũ: 6 bước, phụ thuộc hoàn toàn vào lịch khám BS. | **Tú** |
| **Solution + After** | 45 giây | VinBiocare AI — mô hình Augmented (AI hỗ trợ, BS vẫn quyết định). Kiến trúc 2 tầng: Rule engine (deterministic) + LLM (giải thích tiếng Việt). Flow mới: 3 bước, <3 giây. Hỗ trợ nhập tay + OCR chụp ảnh. | **Đạt** |
| **Live demo** | 120 giây | *(chi tiết bên dưới)* | **Ly** |
| **Impact + Lessons** | 45 giây | Thời gian: 3-7 ngày → <3s. Cost: 500k → 1.2k VNĐ/lần. Recall red-flag ≥95%. Failure mode chính: nhập sai đơn vị → AI báo cấp cứu sai. Bài học: kiến trúc 2 tầng giúp tách lỗi logic khỏi lỗi ngôn ngữ. | **Lâm** |

---

## Chi tiết Live Demo (120 giây — Ly)

### Happy path (80 giây)

```
Bước 1 (15s): Mở app → giới thiệu giao diện 2 panel (Chat + Dashboard)
Bước 2 (20s): Chọn demo "Tiểu đường" hoặc nhập thủ công:
              "Glucose: 155, Insulin: 1.2, BMI: 33.6, LDL: 165"
Bước 3 (15s): Chỉ vào Dashboard bên phải:
              - Glucose 🔴 Danger, BMI 🔴 Danger, LDL 🟡 Warning
              - Triage banner: ⚠️ URGENT
Bước 4 (15s): Chỉ vào Chat bên trái:
              - AI giải thích tiếng Việt từng chỉ số
              - Lời khuyên + disclaimer "AI không thay thế BS"
Bước 5 (15s): Hỏi thêm: "Tôi cần gặp bác sĩ không?"
              → AI trả lời dựa trên context đã phân tích
```

### Edge case (40 giây)

```
Bước 1 (15s): Upload ảnh xét nghiệm (chuẩn bị sẵn 1 ảnh)
              → OCR tự đọc số, chuyển đổi đơn vị
              → Kết quả hiện trên Dashboard tự động
Bước 2 (25s): Nhập chỉ số bình thường hoàn toàn
              (Glucose: 85, BMI: 22, LDL: 90...)
              → Dashboard toàn xanh 🟢
              → AI: "Các chỉ số trong giới hạn bình thường"
              → Nói: "AI không chỉ cảnh báo nguy hiểm,
                      mà còn trấn an khi mọi thứ bình thường"
```

---

## Q&A — Chuẩn bị trả lời (5 phút)

| Câu hỏi thường gặp | Ai trả lời | Gợi ý trả lời |
|---------------------|------------|----------------|
| "Auto hay aug?" | **Tú** | Augmented — AI giải thích & phân loại, BS vẫn là người quyết định cuối cùng. Mọi response đều có disclaimer. |
| "Failure mode chính?" | **Lâm** | Nhập sai đơn vị (mg/dL vs mmol/L) → rule engine đánh giá ngược. Fix: validate tính hợp lý + bắt buộc chọn đơn vị. |
| "AI sai thì sao?" | **Đạt** | 3 lớp bảo vệ: (1) System prompt cấm đề xuất thuốc, (2) Disclaimer mọi câu trả lời, (3) Doctor correction loop nếu >10% sai → retrain. |
| "Tại sao không dùng ChatGPT trực tiếp?" | **Ly** | ChatGPT không có rule engine y khoa, không validate đơn vị, không có dashboard trực quan, không có safety guardrails chuyên biệt cho y tế. VinBiocare kết hợp rule-based (chính xác) + LLM (dễ hiểu). |
| "Phần mình làm gì?" | **Mỗi người** | *(tự trả lời theo phân công thực tế)* |

---

## Checklist trước demo

- [ ] Mở sẵn app trên browser (backend + frontend đã chạy)
- [ ] Chuẩn bị 1 ảnh xét nghiệm để demo OCR
- [ ] Dry run ít nhất 1 lần, bấm giờ đủ 5 phút
- [ ] Mỗi người đọc qua phần mình, nắm rõ nội dung
- [ ] Backup: screenshot các bước demo phòng app crash
- [ ] Mỗi người trả lời được: "Auto hay aug?", "Failure mode chính?", "Phần mình làm gì?"

---

## Backup plan nếu demo crash

```
Nói: "Demo đang gặp lỗi kết nối — đây cũng là 1 failure mode thực tế.
      Để tôi show kết quả đã chạy trước đó."
→ Mở screenshot/video đã chuẩn bị sẵn
→ Tiếp tục trình bày bình thường
```

---

## Tips

- **Show, don't tell:** demo chạy thật, chỉ vào màn hình khi nói
- **Nói chậm:** 5 phút ngắn hơn bạn nghĩ — nói nhanh = peer không hiểu
- **Mỗi người nói:** Tú → Đạt → Ly → Lâm, chuyển tiếp tự nhiên
- **Mở sẵn mọi thứ:** trước khi peer đến, laptop mở sẵn demo
- **Đừng show code** — peer cần thấy product, không cần thấy code
- **Đừng giải thích API** — "dùng GPT-4o-mini" là đủ

---

## Mở rộng (optional — bonus)

### Before → After live comparison

1. **30 giây:** Mở Google, search "Glucose 155 mg/dL có nguy hiểm không" → kết quả lộn xộn, mâu thuẫn, tiếng Anh
2. **30 giây:** Mở VinBiocare AI, nhập cùng chỉ số → kết quả rõ ràng, tiếng Việt, có màu sắc phân loại

### Hỏi peer thử ngay

- Đưa laptop cho peer, nói: "Thử nhập chỉ số xét nghiệm gần nhất của bạn xem AI nói gì"
- Hoặc cho peer chọn 1 trong 5 demo sẵn (Tim mạch / Tiểu đường / Thận / Bình thường / Hỗn hợp)
