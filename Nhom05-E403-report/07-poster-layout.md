# Poster layout — 1 trang

Poster/slides tóm tắt trưng khi trình bày. Peer nhìn poster/slides trong lúc nghe demo.

---

## Sketch tổng thể

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│        🏥  VINBIOCARE AI — Giải thích kết quả xét nghiệm        │
│                                                                 │
│   70% bệnh nhân không hiểu kết quả xét nghiệm, chờ 3-7 ngày   │
│   mới gặp bác sĩ giải thích → lo lắng không cần thiết.         │
│   → AI phân tích chỉ số, giải thích tiếng Việt, cảnh báo       │
│     nguy hiểm ngay lập tức.                                     │
│                                                                 │
├────────────────────────────┬────────────────────────────────────┤
│                            │                                    │
│     ❌  BEFORE (hiện tại)   │      ✅  AFTER (với AI)            │
│                            │                                    │
│  ┌──────────┐              │  ┌──────────┐                      │
│  │ Bệnh nhân│              │  │ Bệnh nhân│                      │
│  └────┬─────┘              │  └────┬─────┘                      │
│       ↓                    │       ↓                            │
│  Nhận giấy xét nghiệm     │  Nhập số liệu / chụp ảnh          │
│       ↓                    │  xét nghiệm (OCR tự đọc)          │
│  Không hiểu các chỉ số     │       ↓                            │
│  (Glucose? LDL? Creatinine?)│  AI phân tích rule-based          │
│       ↓                    │  (xanh/vàng/đỏ từng chỉ số)       │
│  Tra Google → hoang mang   │       ↓                            │
│  thêm, thông tin mâu thuẫn │  LLM giải thích tiếng Việt        │
│       ↓                    │  + lời khuyên cụ thể               │
│  Đặt lịch khám bác sĩ     │       ↓                            │
│  (chờ 3-7 ngày)            │  Biết ngay: bình thường hay        │
│       ↓                    │  cần gặp bác sĩ gấp               │
│  Bác sĩ giải thích         │       ↓                            │
│  (15-20 phút/bệnh nhân)   │  Hỏi thêm AI nếu thắc mắc        │
│                            │  (chat nhiều lượt)                 │
│                            │                                    │
│  📊 6 bước · 3-7 ngày      │  📊 3 bước · dưới 3 giây           │
│                            │                                    │
├────────────────────────────┴────────────────────────────────────┤
│                                                                 │
│                        💻  LIVE DEMO                             │
│                                                                 │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │                                                         │   │
│   │  ┌─────────────────────┐  ┌──────────────────────────┐  │   │
│   │  │  💬 Chat AI          │  │  📊 Dashboard chỉ số     │  │   │
│   │  │                     │  │                          │  │   │
│   │  │ User: "Glucose 155, │  │  Glucose  155  🔴 Danger  │  │   │
│   │  │  Insulin 1.2,       │  │  ████████████░░ (155/100)│  │   │
│   │  │  BMI 33.6,          │  │                          │  │   │
│   │  │  LDL 165"           │  │  BMI      33.6 🔴 Danger  │  │   │
│   │  │                     │  │  ██████████░░░ (33.6/25) │  │   │
│   │  │ AI: "Glucose đường  │  │                          │  │   │
│   │  │  huyết lúc đói cao  │  │  LDL      165  🟡 Warning │  │   │
│   │  │  (155 mg/dL, bình   │  │  ████████░░░░ (165/130)  │  │   │
│   │  │  thường: 70-100),   │  │                          │  │   │
│   │  │  gợi ý nguy cơ      │  │  HDL       55  🟢 Normal  │  │   │
│   │  │  tiền tiểu đường..."│  │  ██████░░░░░░ (55/40)    │  │   │
│   │  │                     │  │                          │  │   │
│   │  │ [📷 Upload ảnh XN]   │  │  ⚠️ Triage: URGENT       │  │   │
│   │  └─────────────────────┘  └──────────────────────────┘  │   │
│   │                                                         │   │
│   │  📷 Upload ảnh → OCR tự đọc số → phân tích tự động       │   │
│   │  5 demo sẵn: Tim mạch | Tiểu đường | Thận | Bình thường │   │
│   │                                                         │   │
│   │  Scan thử:  [QR CODE]   hoặc link: _______________     │   │
│   │                                                         │   │
│   └─────────────────────────────────────────────────────────┘   │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│                        📊  IMPACT                                │
│                                                                 │
│   Thời gian hiểu kết quả   3-7 ngày ──→ <3 giây    ▼ ~99%     │
│   Thời gian tư vấn BS      15-20 phút ─→ giảm 60%  ▼ 60%      │
│   Precision (giải thích)    — ──────────→ ≥92%      target      │
│   Recall (red-flag)         — ──────────→ ≥95%      target      │
│   BS phải sửa lại          — ──────────→ ≤5%       target      │
│   Cost / lần phân tích     200-500k VNĐ → ~1,250đ  ▼ 99%      │
│   ROI (2000 user/tháng)    — ──────────→ +$14,600  /tháng      │
│                                                                 │
├──────────────────────────────┬──────────────────────────────────┤
│                              │                                  │
│  ⚠  FAILURE MODES            │  🔄  LEARNING SIGNAL              │
│                              │                                  │
│  1. Nhập sai đơn vị         │  Doctor correction rate:          │
│     (mg/dL vs mmol/L)       │  BS sửa kết quả AI → nếu >10%   │
│     → AI báo "CẤP CỨU" sai │  → retrain prompt & rules        │
│     ✔ Fix: kiểm tra tính    │       ↓                          │
│       hợp lý + bắt buộc     │  User satisfaction:               │
│       chọn đơn vị           │  Rating <3.5/5 liên tiếp         │
│                              │  → review UX + prompt            │
│  2. LLM ảo giác y khoa      │       ↓                          │
│     (VD: "ngưng thuốc")     │  So sánh AI vs thực tế:          │
│     → Nguy hiểm sức khỏe    │  User chọn gì sau gợi ý?        │
│     ✔ Fix: system prompt     │  Khác vs AI → correction signal  │
│       cấm đề xuất thuốc +   │       ↓                          │
│       disclaimer mọi response│  Kiến trúc 2 tầng:              │
│                              │  Rule engine (deterministic)     │
│  3. OCR đọc sai từ ảnh mờ   │  + LLM (generative)              │
│     → Phân tích sai          │  → Tách lỗi logic / lỗi ngôn ngữ│
│     ✔ Fix: validate output,  │  → Debug dễ, cải thiện nhanh    │
│       cho user sửa lại      │                                  │
│                              │  📈 Càng dùng → càng chính xác   │
│                              │                                  │
└──────────────────────────────┴──────────────────────────────────┘
```

---

## 5 phần bắt buộc

| # | Phần | Mục đích | Ghi chú |
|---|------|----------|---------|
| 1 | **Tên product + problem statement** | Peer biết ngay product làm gì | 1 câu, font lớn nhất |
| 2 | **Before \| After** | So sánh flow cũ vs flow mới | 2 cột, có flow diagram + số liệu (bước, thời gian) |
| 3 | **Live demo** | Peer thấy product chạy thật | Screenshot UI + QR code hoặc link để peer thử ngay |
| 4 | **Impact** | Chứng minh product có giá trị | Số cụ thể: thời gian, accuracy, cost — trước vs sau |
| 5 | **Failure modes \| Learning signal** | Nhóm hiểu giới hạn + hướng cải thiện | 2 cột: khi AI sai thì sao \| product học gì từ user |

---

## Tips

- Font lớn, đọc được từ 1-2 mét — peer đứng xem
- Ít chữ, nhiều hình — screenshot, diagram, flow > mô tả text
- Dùng Canva template "poster" nếu muốn design nhanh
- Không cần đẹp, cần rõ: peer nhìn 10 giây hiểu product làm gì
- Before/After nên dùng flow diagram thay vì chỉ viết text
- QR code trỏ đến live demo → peer scan thử ngay = ấn tượng hơn

---

## Mở rộng (optional — bonus)

### Before/After chi tiết hơn

| | Before (hiện tại) | After (với VinBiocare AI) |
|---|---|---|
| **Screenshot / sketch** | *(giấy xét nghiệm + Google search)* | *(Chat AI + Dashboard chỉ số màu)* |
| **Số bước** | 6 bước, 3-7 ngày | 3 bước, <3 giây |
| **Pain point chính** | Không hiểu chỉ số, chờ lâu, lo lắng | AI giải thích ngay, cảnh báo nguy hiểm tức thì |
| **Ai quyết định** | Bệnh nhân tự tra Google hoặc chờ BS | AI phân tích + gợi ý, BS xác nhận nếu cần |

### QR code đến live demo

In QR code trên poster → peer scan = thử demo ngay trên điện thoại. Ấn tượng hơn nhiều so với chỉ nhìn screenshot.

- Dùng bất kỳ QR generator nào (free) trỏ đến link deploy
- Nếu chưa deploy: QR trỏ đến video recording demo

### Impact dashboard mock

```
┌──────────────────────────────────────┐
│ Thời gian hiểu kết quả  3-7d → <3s  │
│ Thời gian tư vấn BS     20m → 8m    │
│ Precision giải thích     — → ≥92%    │
│ Recall red-flag          — → ≥95%    │
│ Chi phí / phân tích      500k → 1.2k │
│ User hài lòng            — → ≥4/5   │
└──────────────────────────────────────┘
```

Dùng số thật từ test (nếu có) hoặc ước lượng có cơ sở.

### Câu hỏi mở rộng

- Peer chỉ nhìn poster 10 giây — thông tin nào PHẢI thấy đầu tiên?
- Poster có thể "đứng một mình" (không cần người giải thích) không?
- Nếu phải bỏ 1 phần trên poster, bỏ phần nào? Tại sao?
