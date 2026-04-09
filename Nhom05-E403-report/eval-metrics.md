# Eval metrics + threshold

Chọn metrics, đặt threshold, xác định red flag. Câu hỏi quan trọng nhất: **optimize precision hay recall?**

## Precision hay recall?

☒ Precision — khi AI nói "có" thì thực sự đúng (ít false positive)
☒ Recall — tìm được hết những cái cần tìm (ít false negative)
=> Cả 2 và thay đổi linh hoạt

**Tại sao?** Với VinBiocare, có 2 tầng chất lượng khác nhau:
- **Cảnh báo red-flag** phải ưu tiên **recall** vì nếu miss ca nguy hiểm, bệnh nhân có thể chậm khám và tăng rủi ro sức khỏe.
- **Giải thích kết quả** phải ưu tiên **precision** vì nếu giải thích sai, bệnh nhân hiểu sai tình trạng của mình và mất niềm tin vào hệ thống.

**Nếu sai ngược lại thì sao?**
- Nếu recall của cảnh báo thấp: AI bỏ sót bất thường quan trọng, bệnh nhân không biết cần đi khám sớm.
- Nếu precision của giải thích thấp: AI nói sai hoặc nói quá mức, làm người dùng hiểu lầm hoặc lo lắng không cần thiết.

## Metrics table

| Metric | Threshold | Red flag (dừng khi) |
|--------|-----------|---------------------|
| Precision — giải thích đúng | ≥92% | <85% trong 1 tuần → audit prompt/rules ngay |
| Recall — cảnh báo red-flag | ≥95% | <90% → dừng deploy/pilot, bổ sung edge cases |
| Recall — giải thích/chạm đúng vấn đề chung | ≥88% | <80% → review coverage của rules và indicator set |
| User satisfaction (5-point) | ≥4.0/5 | <3.5 trong 2 tuần liên tiếp |
| Doctor correction rate | ≤5% | >10% → phải review output và hiệu chỉnh hệ thống |

## Gợi ý cách đo

- **Precision — giải thích đúng**:
  Số câu/ý giải thích được bác sĩ hoặc bộ đáp án chấm là đúng / tổng số ý giải thích được sinh ra.

- **Recall — cảnh báo red-flag**:
  Số ca bất thường nguy hiểm được AI flag đúng / tổng số ca nguy hiểm thực tế có trong tập test.

- **Recall — giải thích chung**:
  Số chỉ số bất thường được AI giải thích đúng ý chính / tổng số chỉ số bất thường cần giải thích.

- **User satisfaction**:
  Điểm đánh giá sau mỗi lần phân tích: “Giải thích này có hữu ích không?” theo thang 1-5.

- **Doctor correction rate**:
  Số output bị bác sĩ sửa / tổng số output được bác sĩ review.

## Ghi chú

Các threshold trên là **target cho pilot** của sản phẩm, không phải số đã đạt ở prototype hiện tại. Ở bản demo hiện tại, team mới có rule-based analysis + LLM explanation cho một số indicator chính, nên cần thêm test set và human review để đo chính thức.
