# SPEC — AI Product Hackathon

**Nhóm:** 5
**Zone:** 1
**Track:** ☐ VinFast · ☐ Vinmec · ☐ VinUni-VinSchool · ☐ XanhSM · ☒ Open: Vin Biocare

**Problem statement (1 câu):** Bệnh nhân nhận kết quả xét nghiệm nhưng không hiểu ý nghĩa, giáo dục y tế không đủ, có nhiều lo lắng — AI phân tích kết quả, giải thích ý nghĩa, cảnh báo nguy cơ tiềm ẩn, giảm 80% thời gian tư vấn ban đầu và nâng cao hiểu biết bệnh nhân.

---

## 1. AI Product Canvas

|   | Value | Trust | Feasibility |
|---|-------|-------|-------------|
| **Câu hỏi** | User nào? Pain gì? AI giải gì? | Khi AI sai thì sao? User sửa bằng cách nào? | Cost/latency bao nhiêu? Risk chính? |
| **Trả lời** | Bệnh nhân nhận kết quả xét nghiệm nhưng 70% không hiểu → lo lắng, phải chờ tư vấn bác sĩ 3-7 ngày — AI phân tích kết quả 30s, giải thích bằng ngôn ngữ bình dân, đánh dấu giá trị bất thường, gợi ý tư vấn cần thiết | AI giải thích sai → bệnh nhân xác nhận/sửa (feedback), hoặc hỏi lại bác sĩ, AI học từ correction và expert validation | ~$0.05/lần phân tích (embedding + LLM), latency <3s, risk: hallucinate chẩn đoán (không phải AI's role), miss cảnh báo nguy hiểm |

**Automation hay augmentation?** ☐ Automation · ☒ Augmentation
Justify: *Augmentation — AI gợi ý giải thích & cảnh báo, bệnh nhân và bác sĩ vẫn quyết định, cost of reject ≈ 0, tăng độ tin tưởng vì có human review*

**Learning signal:**

1. User correction đi vào đâu? **Database feedback từ bệnh nhân + bác sĩ validation → retraining**
2. Product thu signal gì để biết tốt lên hay tệ đi? **% bệnh nhân đánh giá giải thích hữu ích (5 star), % correction từ bác sĩ, click "liên hệ bác sĩ ngay"**
3. Data thuộc loại nào? ☒ User-specific · ☒ Domain-specific · ☒ Real-time · ☒ Human-judgment · ☐ Khác: ___
   Có marginal value không? **Có — model LLM biết medical knowledge chung, nhưng data local (Vinmec reference ranges, bệnh nhân VN, thuật ngữ tiếng Việt) là competitive advantage mà pretrained model chưa có. Feedback từ bác sĩ Vinmec tạo moat dữ liệu riêng**

---

## 2. User Stories — 4 paths

Mỗi feature chính = 1 bảng. AI trả lời xong → chuyện gì xảy ra?

### Feature: Phân tích & giải thích kết quả xét nghiệm

**Trigger:** *Bệnh nhân upload ảnh/PDF kết quả xét nghiệm → AI phân tích → hiển thị giải thích & cảnh báo*

| Path | Câu hỏi thiết kế | Mô tả |
|------|-------------------|-------|
| Happy — AI đúng, tự tin | User thấy gì? Flow kết thúc ra sao? | Bệnh nhân upload xét nghiệm máu → AI hiển thị: "Hemoglobin 12.5 (bình thường) — khỏe mạnh. Cholesterol 240 (cao) — cần monitor chế độ ăn" → user hiểu, không lo lắng, có thể bookmark để chia sẻ bác sĩ |
| Low-confidence — AI không chắc | System báo "không chắc" bằng cách nào? User quyết thế nào? | Xét nghiệm hiếm gặp → UI hiển thị: "Giải thích này cần xác nhận bác sĩ 🔶" + button "Chat với bác sĩ ngay 30 phút" → bệnh nhân có lựa chọn |
| Failure — AI sai | User biết AI sai bằng cách nào? Recover ra sao? | AI sai diễn dịch giá trị (VD: nhầm unit) → bệnh nhân flag "Giải thích này không đúng" → goes to review queue. Hoặc bác sĩ thấy feedback → request correction → AI học |
| Correction — user sửa | User sửa bằng cách nào? Data đó đi vào đâu? | Bác sĩ xem feedback bệnh nhân + AI output → edit giải thích đúng, đánh dấu "validated by doctor" → data vào training set, improve model accuracy |

### Feature: Tư vấn & liên hệ bác sĩ

**Trigger:** *Bệnh nhân thấy cảnh báo hoặc muốn tư vấn → AI gợi ý follow-up actions → bệnh nhân liên hệ bác sĩ hoặc book khám*

| Path | Câu hỏi thiết kế | Mô tả |
|------|-------------------|-------|
| Happy — bệnh nhân quyết định kịp thời | User thấy gì? Flow kết thúc ra sao? | Đường huyết cao → AI hiển thị: "⚠️ Cần tư vấn nhanh" + "Book khám nội tiết trong 3 ngày" → bệnh nhân book ngay 10 phút |
| Low-confidence — cần bác sĩ | System báo "không chắc" bằng cách nào? | Tìm thấy giá trị bất thường nhưng không chắc severity → "Đề nghị liên hệ bác sĩ để an tâm" + priority (High/Medium/Low) |
| Failure — miss cảnh báo | User biết bị miss như thế nào? | AI không flag giá trị bất thường (edge case) → bệnh nhân phải chờ thêm 1 tuần → delay điều trị, thời gian quan trọng bị mất. Mitigation: bác sĩ review định kỳ & bổ sung flag patterns |
| Correction — bác sĩ refine | User sửa bằng cách nào? | Bác sĩ thấy bệnh nhân follow-up thế nào → feedback "cảnh báo này tốt" hoặc "không cần alert này" → model calibrate |

*Lặp lại cho feature thứ 2-3 nếu có.*

---

## 3. Eval metrics + threshold

**Optimize precision hay recall?** ☒ Precision · ☒ Recall (tùy theo tầng)
Tại sao? **Hai tầng khác nhau cần ưu tiên khác nhau:**
- **Cảnh báo nguy hiểm (red-flag) → Recall-first (≥95%):** Không được miss ca nguy hiểm — false negative trong y tế = delay điều trị = nguy hiểm tính mạng. Cảnh báo thừa (false positive) tuy gây lo lắng nhưng bác sĩ verify được, còn miss cảnh báo thì không ai catch.
- **Giải thích kết quả (explanation) → Precision-first (≥92%):** Nếu AI giải thích sai, bệnh nhân hiểu lầm tình trạng sức khỏe → hành động sai. Giải thích phải đúng, thiếu thì bác sĩ bổ sung được.

Nếu sai ngược lại thì chuyện gì xảy ra? *Nếu cảnh báo recall thấp → miss ca nguy hiểm → bệnh nhân không biết cần khám gấp → health risk nghiêm trọng. Nếu giải thích precision thấp → bệnh nhân hiểu sai → mất niềm tin hoặc tự điều trị sai.*

| Metric | Threshold | Red flag (dừng khi) |
|--------|-----------|---------------------|
| Precision — giải thích đúng | ≥92% | <85% trong 1 tuần → audit training data |
| Recall — cảnh báo red-flag | ≥95% | <90% → dừng deploy, add edge cases ngay |
| Recall — giải thích chung | ≥88% | <80% → review coverage |
| User satisfaction (⭐ 5-point) | ≥4.0 | <3.5 liên tiếp 2 tuần |
| Doctor correction rate | ≤5% | >10% → model retraining |

---

## 4. Top 3 failure modes

*Liệt kê cách product có thể fail — không phải list features.*
*"Failure mode nào user KHÔNG BIẾT bị sai? Đó là cái nguy hiểm nhất."*

| # | Trigger | Hậu quả | Mitigation |
|---|---------|---------|------------|
| 1 | AI miss cảnh báo (VD: giá trị bất thường nhưng model không detect) | Bệnh nhân không biết tình trạng nguy hiểm → delay treatment → health risk | Recall ≥95% cho red-flag values. Bác sĩ validate all outputs. Add manual override button / second opinion |
| 2 | AI hallucinate explanation (VD: tạo nội dung không dựa trên data gốc) | Bệnh nhân hiểu sai, làm theo AI advice sai → harm. Data privacy breach nếu generate sensitive info | Restrict AI to template-based explanation. Validate output vs source data. Watermark AI-generated content. Audit logs |
| 3 | Dữ liệu xét nghiệm bị nhầm (patient data mix-up) | Bệnh nhân A nhận giải thích của B → sai diagnosis → harm | Implement strong data validation: OCR quality check, manual verification cho first 100 cases, patient ID matching |

---

## 5. ROI 3 kịch bản

|   | Conservative | Realistic | Optimistic |
|---|-------------|-----------|------------|
| **Assumption** | 500 bệnh nhân/tháng, 60% active, 40% giảm thời gian tư vấn | 2000 bệnh nhân/tháng, 75% active, 60% giảm thời gian tư vấn | 8000 bệnh nhân/tháng (Vinmec platform), 85% active, 75% giảm thời gian tư vấn |
| **Cost** | $150/tháng (API + hosting) | $400/tháng | $800/tháng |
| **Benefit** | 300 bệnh nhân × $10 (giảm 20 phút tư vấn/ca) = $3,000/tháng | 1,500 × $10 = $15,000/tháng | 5,100 × $10 = $51,000/tháng, +$15K từ retention |
| **Net** | $2,850/tháng | $14,600/tháng | $65,200/tháng |

**Kill criteria:** *Khi nào nên dừng? Nếu doctor correction rate >15% liên tiếp 3 tuần, hoặc user churn >20%/tháng, hoặc serious adverse event xảy ra*

---

## 6. Mini AI spec (1 trang)

*Tóm tắt tự do — viết bằng ngôn ngữ tự nhiên, không format bắt buộc.*
*Gom lại: product giải gì, cho ai, AI làm gì (auto/aug), quality thế nào (precision/recall), risk chính, data flywheel ra sao.*

### Mô tả sản phẩm:
**TestAdvisor** — Ứng dụng AI giúp bệnh nhân hiểu kết quả xét nghiệm y tế và nhận tư vấn ban đầu trước khi gặp bác sĩ.

### Ai dùng?
Bệnh nhân (25-65 tuổi) tại Vinmec Health Network: 70% không hiểu kết quả xét nghiệm, phải chờ 3-7 ngày tư vấn bác sĩ, lo lắng không cần thiết.

### AI làm gì?
1. **OCR + Parse**: Nhận dạng ảnh/PDF kết quả → extract giá trị, unit, tên xét nghiệm
2. **Augmented Explanation**: LLM giải thích từng chỉ số, so sánh với range bình thường, cảnh báo nếu bất thường
3. **CTA Recommendation**: Dựa trên findings → gợi ý follow-up (tư vấn ngay, monitor, appointment)
4. **Quality Control**: Confidence score; nếu thấp → "Xác nhận bác sĩ cần thiết"

### Precision vs Recall:
- **Precision ≥92% (explanation)**: Giải thích phải chính xác ít nhất 92% — bệnh nhân tin tưởng AI, sai sẽ gây hiểu lầm
- **Recall ≥95% (red-flag)**: Cảnh báo nguy hiểm không được miss — false negative trong y tế = delay điều trị
- **Recall ≥88% (general)**: Giải thích chung có thể thiếu, bác sĩ bổ sung được

### Risk chính:
1. **Miss critical pathology** → built-in validation, doctor review tier-1 results
2. **Hallucinate giải thích** → template-based + constraint generation, audit logs
3. **Data privacy** → encrypt patient data, zero-retention policy, comply HIPAA-equivalent

### Data flywheel:
- Bệnh nhân feedback (⭐ rating, "useful/not useful", corrections)
- Bác sĩ validation (approve explanation, flag errors)
- Correction log → fine-tuning dataset
- Monthly accuracy audit → retraining

### Success metric:
- 90% explanation satisfaction
- <5% doctor override rate
- 60% bệnh nhân skip initial consultation (ROI proof)
- Zero adverse events attributed to AI error
