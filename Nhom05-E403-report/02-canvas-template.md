# AI Product Canvas — VinBiocare AI Chatbot

---

## Canvas

|   | Value | Trust | Feasibility |
|---|-------|-------|-------------|
| **Câu hỏi guide** | User nào? Pain gì? AI giải quyết gì mà cách hiện tại không giải được? | Khi AI sai thì user bị ảnh hưởng thế nào? User biết AI sai bằng cách nào? User sửa bằng cách nào? | Cost bao nhiêu/request? Latency bao lâu? Risk chính là gì? |
| **Trả lời** | Bệnh nhân 25–65 tuổi tại Vinmec, không có nền tảng y tế, chờ 3–7 ngày gặp bác sĩ. 70% không hiểu kết quả xét nghiệm → lo lắng hoặc bỏ qua dấu hiệu nguy hiểm. Tự Google → thông tin không tin cậy, thiếu ngữ cảnh cá nhân. AI giải thích chỉ số bất thường bằng tiếng Việt trong 30 giây, phân loại Normal/Warning/Danger. | AI sai → bệnh nhân hoang mang hoặc bỏ sót nguy hiểm. Bác sĩ đối chiếu khi tái khám → phát hiện sai lệch. Luôn có nút CTA đặt lịch Vinmec + disclaimer "tham khảo, không thay thế bác sĩ". Target: Recall ≥ 95%, Precision ≥ 92%, Doctor correction ≤ 5%. | **Build:** Phân tích 9 chỉ số cơ bản, giải thích tiếng Việt qua chatbot, cảnh báo 3 mức, nút đặt lịch Vinmec. **NOT build:** Chẩn đoán bệnh, OCR phiếu xét nghiệm, tích hợp EMR. **Risk:** Hallucinate thông tin y tế sai → cần guardrails + disclaimer. |

---

## Automation hay augmentation?

☐ Automation
☑ **Augmentation** — AI giải thích & gợi ý, bệnh nhân vẫn cần bác sĩ xác nhận. Y tế sai = nguy hiểm → không để AI tự quyết.

---

## Learning signal

| # | Câu hỏi | Trả lời |
|---|---------|---------|
| 1 | User correction đi vào đâu? | Bác sĩ đính chính → correction log → cải thiện prompt/model. Target: correction rate ≤ 5%. |
| 2 | Signal tốt lên/tệ đi? | Implicit: tỷ lệ nhấn đặt lịch sau Danger. Explicit: rating ≥ 4.0/5. Correction: doctor correction rate. |
| 3 | Data loại nào? | ☑ Domain-specific (y tế) · ☑ User-specific (kết quả cá nhân) · ☑ Human-judgment (bác sĩ đính chính) |

**Marginal value:** Có — correction data từ bác sĩ Vinmec là unique, giúp model hiểu ngữ cảnh y tế Việt Nam mà model chung không có.
