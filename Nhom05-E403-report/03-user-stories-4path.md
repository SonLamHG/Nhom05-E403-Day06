# User Stories — 4 Paths
## VinBiocare AI — Healthcare Chatbot

Mỗi feature AI chính = 1 bảng. AI trả lời xong → chuyện gì xảy ra? Viết cả 4 trường hợp.

---

## Feature 1: Analyze Lab Indicators (Phân tích chỉ số xét nghiệm)

**Trigger:** 
User nhập chỉ số xét nghiệm (glucose, insulin, BMI, huyết áp, v.v.) → API `/analyze` chạy rule-based engine → trả về kết quả màu sắc (green/yellow/red) + message + pattern detection (metabolic syndrome, diabetes risk)

**Design Questions:**
- Khi nào user biết được kết quả?
- Khi nào hệ thống không chắc chắn?
- Khi nào hệ thống sai, user phát hiện thế nào?
- User sửa chỉ số được không? Data lưu vào đâu?

| Path | Câu hỏi thiết kế | Mô tả |
|------|-------------------|-------|
| **Happy** — Phân tích đúng, tự tin | User thấy gì? Flow kết thúc ra sao? | User nhập: Glucose=88, Insulin=12.5, BMI=23, BloodPressure=115, HDL=55, LDL=100 → Engine trả về 4 chỉ số **green** (bình thường) → General summary: "Các chỉ số xét nghiệm của bạn đều nằm trong giới hạn bình thường. Hãy tiếp tục duy trì lối sống lành mạnh!" → User thấy badge xanh + lý do từng chỉ số → tin tưởng → tiếp tục hoặc chat hỏi thêm |
| **Low-confidence** — Hệ thống gặp ambiguity | System báo bằng cách nào? User quyết định thế nào? | User nhập: Glucose=101 (chỉ hơi cao, trong warning_max=126) → Engine báo "Cảnh báo" (yellow) kèm message: "Chỉ số đường huyết hơi cao. Tiền tiểu đường hoặc tiểu đường khi >126 mg/dL" + % tự tin (VD: 75%) → UI hiện "⚠️ Nên kiểm tra thêm" + nút "Ask AI for clarification" → User click → chat với AI để hiểu sâu hơn / biết nên làm gì tiếp |
| **Failure** — Rule sai hoặc logic bug | User biết sai bằng cách nào? Recover thế nào? | User nhập: Glucose=300 (rõ ràng nguy hiểm) nhưng engine trả về green do bug logic → Hoặc user nhập indicator không tồn tại ("XYZ=100") → Engine trả "unknown" (gray) → User thấy kết quả không hợp lý → Click vào indicator → xem tham chiếu → so sánh thủ công → phát hiện sai → feedback button "Report error" → gửi log + screenshot → dev fix |
| **Correction** — User sửa dữ liệu | User sửa bằng cách nào? Data đi vào đâu? | User báo: "Mình nhập sai, glucose phải là 85 chứ không phải 180" → UI cho phép edit input → re-analyze → kết quả thay đổi → Tùy chọn A: Lưu correction vào correctionLog.json (chưa implement) → Tùy chọn B: Share feedback "My glucose was XX, but I corrected to YY" → Data này có thể dùng để retrain rule hoặc feedback loop trong tương lai |

**Edge Cases & Ambiguities:**

| Edge case | Dự đoán Engine sẽ xử lý | UX nên phản ứng ra sao |
|-----------|-------------------------|------------------------|
| Input chứa negative value (glucose=-50) | Validate sơ sài → trả "unknown" hoặc error | Toast: "Giá trị không hợp lệ, hãy nhập số dương" + focus vào input |
| Input quá cao/quá thấp ngoài phạm vi logic (glucose=5000) | Logic check → "Nguy hiểm" (red) nhưng message có thể misleading | Badge red + warning "⚠️ Giá trị bất thường, kiểm tra lại input hoặc liên hệ bác sĩ" |
| User không nhập đủ indicator (chỉ nhập glucose, thiếu cái khác) | Rule engine chỉ xử lý những gì có, không infer những gì thiếu | UI hiện missing fields hint "Thêm BMI, insulin để phân tích toàn diện" + mini pattern detection chỉ dựa trên data có |
| Indicator có giá trị 0 (Insulin=0) | Logic treat =0 như is_inverse=true → "Nguy hiểm" | Xem như low-confidence → suggest "Insulin = 0 rất hiếm, hãy kiểm tra lại"? |
| Chỉ là thay đổi nhỏ (từ 69→70, hay từ 101→100) | Logic trigger status change (yellow→green) | UI highlight "✓ Status changed: Warning → Normal" → user thấy impact của sửa |

## Feature 2: Chat with AI for Health Advice (Hỏi đáp AI về kết quả xét nghiệm)

**Trigger:** 
User nhập câu hỏi bằng ngôn ngữ tự nhiên (VD: "Glucose cao thế này có nguy hiểm không?") → Frontend gọi `/api/chat` + inject `rule_output` context từ previous `/analyze` call → OpenAI GPT-4o-mini process → trả về explanation + actionable advice

**Design Questions:**
- AI trả lời có dựa trên context rule_output không?
- Khi nào user phát hiện AI sai (hallucination)?
- Khi nào user muốn sửa AI?
- Làm sao track user corrections để improve?

| Path | Câu hỏi thiết kế | Mô tả |
|------|-------------------|-------|
| **Happy** — AI đúng, có context, tự tin | User thấy gì? Flow kết thúc ra sao? | User: "Glucose 115 có nguy hiểm không?" → Frontend gửi: `{messages: [{role: "user", content: "..."}], context: {rule_output: {...green, yellow, red}}}` → AI nhận context → trả: "Glucose 115 ở mức cao (bình thường là 70-100). Đây là dấu hiệu tiền tiểu đường. Nên kiểm tra lại trong 3-6 tháng, hạn chế đồ ngọt, tập luyện 30 phút/ngày." (dựa vào rule_output + prompt system) → User thấy answer có dựa vào kết quả xét nghiệm → tin tưởng → in ra / share |
| **Low-confidence** — AI không chắc hoặc indicator không đủ | System báo bằng cách nào? | User: "Tôi có mắc tiểu đường không?" nhưng lịch sử chat chỉ có **1 chỉ số** (glucose=110) → AI nhận rule_output không đủ → trả: "(?) Dựa trên đường huyết 110, bạn có dấu hiệu tiền tiểu đường. Tuy nhiên, để chẩn đoán chính xác, cần xem thêm: Insulin, BMI, huyết áp. Bạn có data khác không?" → UI hiện badge "More data needed" + link "Add more indicators" → User click → quay lại Analyze dialog |
| **Failure** — AI hallucinate, sai dữ liệu, hoặc ignore context | User biết sai thế nào? Recover ra sao? | User: "Glucose 85 có bị tiểu đường không?" → Glucose 85 = green (bình thường) → AI trả: "Bạn có nguy cơ tiểu đường cao" (khác với rule_output → HALLUCINATE) → User: "Không, test result của mình xanh mà (green)" → User click feedback "AI không chính xác" → gửi: `{user_question, ai_response, rule_output, feedback: "contradiction"}` → log để review/fine-tune prompt |
| **Correction** — User sửa lỗi AI, giáo dục AI | User sửa bằng cách nào? Feedback đi đâu? | User: "AI ơi, bạn nói sai. Tôi hỏi là nên tập luyện bao lâu, mà bạn trả về điều khác." → UI ask: "Nhận xét của bạn?" → User: [✓] "AI sai", [✓] "Trả lời không liên quan", [!] "Thêm lý do: Tôi hỏi về vận động, không phải chế độ ăn" → Gửi feedback object: `{user_input, ai_response, correction_reason, user_suggestion}` → Store vào feedbackLog.json → Dùng để: prompt tuning, RLHF, improve system prompt |

**Edge Cases & Ambiguities:**

| Edge case | Dự đoán AI sẽ xử lý | UX nên phản ứng ra sao |
|-----------|-------------------------|------------------------|
| User hỏi medical emergency ("Tôi bị tim đau") | Model trả: generic health advice, không escalate | UI detect keyword high-risk (tim đau, khó thở, etc.) → show warning: "⚠️ Đây có thể là emergency, gọi 115 ngay" + disable chat recommendation |
| Chat history quá dài (>20 messages) | TokenLimit → API error hoặc timeout | Frontend auto-summarize last 5-10 messages trước gửi → "Tôi đã hỏi về X, Y, Z. Câu hỏi tiếp theo: ..." |
| rule_output context mâu thuẫn lẫn nhau (Glucose=normal nhưng HbA1c=danger) | AI try to reconcile hoặc báo mâu thuẫn | AI: "Có mâu thuẫn: glucose hôm nay bình thường nhưng HbA1c (3 tháng) cao. Nên tái khám để kiểm tra thêm." |
| User hỏi về indicator không trong dataset (VD: Epstein-Barr virus) | AI không biết logic rule-based → generic answer | AI: "Indicator này không trong bộ xét nghiệm của ứng dụng. Hãy tư vấn với bác sĩ." + suggest "Chọn indicator từ danh sách: Glucose, Insulin, ..." |
| User spam chat (>50 messages trong 1 phút) | No rate limiting → có thể gây cost spike OpenAI | Backend add rate limiter: 10 messages/phút/session → "Hãy đợi một chút" |
| API key expire hoặc config sai | OpenAI Error 401 → trả error về frontend | UI show toast: "❌ Service error, vui lòng thử lại sau" + log error để dev debug (không expose key) |

## Feature 3 (Bonus): Pattern Detection & Health Risk Summary

_Hiện đã implement nhưng chưa có user story rõ_

**Trigger:**
Khi `/analyze` detect >2 indicator ở warning/danger zone + pattern matching (VD: cao glucose + cao insulin + cao BMI) → generate summary pattern: "metabolic syndrome", "diabetes risk", "kidney dysfunction"

| Path | Câu hỏi thiết kế | Mô tả |
|------|-------------------|-------|
| **Happy** — Pattern đúng, rõ ràng | User thấy gì? | Glucose=140, Insulin=45, BMI=28, BloodPressure=135 → Engine detect: `metabolic_factors=3` → summary: "Bạn có nhiều dấu hiệu của hội chứng chuyển hóa (rối loạn lipid, đường huyết, huyết áp, BMI). Nên gặp bác sĩ để kiểm tra thêm (cholesterol, chức năng gan)." → User thấy tóm tắt nguy cơ toàn cảnh → tin tưởng → chat để hỏi "Tôi nên làm gì?" |
| **Low-confidence** — Pattern không rõ | System báo bằng cách nào? | 2 factor borderline → summary: "Bạn có thể có xu hướng hội chứng chuyển hóa. Nên theo dõi thêm 3 tháng." → badge "⚠️ Cần monitoring" |
| **Failure** — Pattern wrong logic | User biết sai thế nào? | Logic detect diabetes risk nhưng bỏ quên `DiabetesPedigreeFunction` → miss high-risk family history | UI feedback "Thiếu yếu tố di truyền trong pattern" |
| **Correction** — User giáo dục engine | User sửa thế nào? | User: "Người thân tôi có tiểu đường, cái `DiabetesPedigreeFunction` cao mà pattern không nhắc?" → Gửi feedback: `{pattern_name, missing_factor, reason}` → Dev add rule |