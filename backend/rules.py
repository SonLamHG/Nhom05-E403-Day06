import json
from pathlib import Path

DATA_PATH = Path(__file__).parent / "data" / "indicators.json"

def load_indicators():
    with open(DATA_PATH, encoding="utf-8") as f:
        return json.load(f)

INDICATORS = load_indicators()

# Reverse map: display name → key (built once at startup)
_NAME_TO_KEY: dict[str, str] = {info["name"]: key for key, info in INDICATORS.items()}

# Plausible physiological bounds — values outside these are likely data-entry errors
_PLAUSIBLE_BOUNDS: dict[str, tuple[float, float]] = {
    "Glucose":                  (20.0,  600.0),
    "Insulin":                  (0.0,   300.0),
    "BMI":                      (10.0,  70.0),
    "BP_Systolic":              (40.0,  220.0),
    "BP_Diastolic":             (30.0,  140.0),
    "SkinThickness":            (1.0,   80.0),
    "DiabetesPedigreeFunction": (0.0,   2.5),
    "LDL":                      (0.0,   400.0),
    "HDL":                      (5.0,   200.0),
    "Creatinine":               (0.1,   20.0),
}


def validate_indicators(data: dict[str, float]) -> None:
    """Raise ValueError if any indicator value is outside plausible physiological bounds."""
    import math
    errors: list[str] = []
    for key, value in data.items():
        if math.isnan(value) or math.isinf(value):
            errors.append(f"{key}: giá trị không hợp lệ ({value})")
            continue
        bounds = _PLAUSIBLE_BOUNDS.get(key)
        if bounds and not (bounds[0] <= value <= bounds[1]):
            errors.append(f"{key}: {value} nằm ngoài khoảng sinh lý cho phép [{bounds[0]}, {bounds[1]}]")
    if errors:
        raise ValueError("Dữ liệu đầu vào không hợp lệ: " + "; ".join(errors))


def calculate_confidence(value: float, info: dict) -> float:
    """Return a confidence score in [0,1] for a given indicator value.

    Heuristics:
    - If value is well inside the normal range -> high confidence (0.95)
    - If value is near a boundary (within 10% of normal span) -> lower confidence (~0.60)
    - If value clearly outside normal or clearly in danger -> medium-high confidence (~0.85)
    - If no reference info available -> 0.5
    """
    try:
        normal_min = info["normal_min"]
        normal_max = info["normal_max"]
    except Exception:
        return 0.5

    span = max(1e-6, normal_max - normal_min)
    # distance to nearest normal boundary
    if value < normal_min:
        dist = normal_min - value
    elif value > normal_max:
        dist = value - normal_max
    else:
        # inside normal range
        # closeness to center increases confidence
        center = (normal_min + normal_max) / 2.0
        rel = abs(value - center) / (span / 2.0)  # 0 at center, 1 at edges
        if rel <= 0.5:
            return 0.95
        if rel <= 1.0:
            return 0.80
        return 0.70

    # outside normal range: compare to warning bounds if present
    warning_min = info.get("warning_min", normal_min)
    warning_max = info.get("warning_max", normal_max)

    # If within warning zone (near boundary)
    if warning_min <= value <= warning_max:
        # distance relative to warning span
        warn_span = max(1e-6, warning_max - warning_min)
        rel_warn = dist / warn_span
        if rel_warn <= 0.1:
            return 0.60
        if rel_warn <= 0.5:
            return 0.75
        return 0.85

    # Far outside warning bounds -> high confidence it's abnormal
    return 0.90


def evaluate_indicator(name: str, value: float) -> dict:
    """Evaluate a single indicator against rules. Returns status + message."""
    info = INDICATORS.get(name)
    if info is None:
        return {
            "name": name,
            "value": value,
            "status": "unknown",
            "color": "gray",
            "message": f"Không có dữ liệu tham chiếu cho chỉ số {name}"
        }

    is_bidirectional = info.get("bidirectional", False)
    is_inverse = info.get("inverse", False)

    if is_bidirectional:
        # Both too high and too low are bad
        warning_max = info.get("warning_max", info["normal_max"])
        warning_min = info.get("warning_min", info["normal_min"])

        if info["normal_min"] <= value <= info["normal_max"]:
            status, color = "Bình thường", "green"
            message = f"{info['description']} ở mức bình thường."
        elif value > info["normal_max"] and value <= warning_max:
            status, color = "Cảnh báo", "yellow"
            risk = info.get("risk_high", info.get("risk", ""))
            message = f"{info['description']} hơi cao. {risk}"
        elif value > warning_max:
            status, color = "Nguy hiểm", "red"
            risk = info.get("risk_high", info.get("risk", ""))
            message = f"{info['description']} ở mức cao. {risk}"
        elif value < info["normal_min"] and value >= warning_min:
            status, color = "Cảnh báo", "yellow"
            risk = info.get("risk_low", info.get("risk", ""))
            message = f"{info['description']} hơi thấp. {risk}"
        else:
            status, color = "Nguy hiểm", "red"
            risk = info.get("risk_low", info.get("risk", ""))
            message = f"{info['description']} quá thấp. {risk}"

    elif is_inverse:
        # Lower is worse (e.g. HDL)
        warning_min = info.get("warning_min", info["normal_min"])
        if value >= info["normal_min"]:
            status, color = "Bình thường", "green"
            message = f"{info['description']} ở mức bình thường."
        elif value >= warning_min:
            status, color = "Cảnh báo", "yellow"
            message = f"{info['description']} hơi thấp. {info.get('risk', '')}"
        else:
            status, color = "Nguy hiểm", "red"
            message = f"{info['description']} quá thấp. {info.get('risk', '')}"

    else:
        # Higher is worse (e.g. LDL, Creatinine, DPF)
        warning_max = info.get("warning_max", info["normal_max"])
        if value <= info["normal_max"]:
            status, color = "Bình thường", "green"
            message = f"{info['description']} ở mức bình thường."
        elif value <= warning_max:
            status, color = "Cảnh báo", "yellow"
            risk = info.get("risk_high", info.get("risk", ""))
            message = f"{info['description']} hơi cao. {risk}"
        else:
            status, color = "Nguy hiểm", "red"
            risk = info.get("risk_high", info.get("risk", ""))
            message = f"{info['description']} ở mức cao. {risk}"

    conf = calculate_confidence(value, info)

    return {
        "name": info["name"],
        "value": value,
        "unit": info["unit"],
        "status": status,
        "color": color,
        "message": message,
        "reference": f"{info['normal_min']}–{info['normal_max']} {info['unit']}",
        "confidence": round(float(conf), 2)
    }


def generate_summary(results: list[dict]) -> str:
    """Generate overall health summary based on evaluated indicators."""
    danger = [r for r in results if r["color"] == "red"]
    warning = [r for r in results if r["color"] == "yellow"]

    if not danger and not warning:
        return "Các chỉ số xét nghiệm của bạn đều nằm trong giới hạn bình thường. Hãy tiếp tục duy trì lối sống lành mạnh!"

    # Collect raw indicator keys from results for pattern detection
    raw_keys = {_NAME_TO_KEY.get(r["name"], r["name"]) for r in danger + warning}

    has_lipid = bool(raw_keys & {"LDL", "HDL"})
    has_glucose = "Glucose" in raw_keys
    has_insulin = "Insulin" in raw_keys
    has_kidney = "Creatinine" in raw_keys
    has_bp = bool(raw_keys & {"BP_Systolic", "BP_Diastolic"})
    has_bmi = "BMI" in raw_keys
    has_skin = "SkinThickness" in raw_keys
    has_dpf = "DiabetesPedigreeFunction" in raw_keys

    parts = []

    # Metabolic syndrome detection
    metabolic_factors = sum([has_lipid, has_glucose, has_bp, has_bmi])
    if metabolic_factors >= 3:
        parts.append("Bạn có nhiều dấu hiệu của hội chứng chuyển hóa (rối loạn lipid, đường huyết, huyết áp, BMI).")
    elif has_lipid and has_glucose:
        parts.append("Bạn có dấu hiệu của hội chứng chuyển hóa (rối loạn lipid kết hợp đường huyết cao).")
    elif has_lipid:
        parts.append("Hệ tim mạch của bạn đang chịu áp lực do rối loạn lipid máu.")

    # Diabetes risk cluster
    diabetes_factors = sum([has_glucose, has_insulin, has_dpf, has_bmi])
    if diabetes_factors >= 2 and not (has_lipid and has_glucose):
        parts.append("Nhiều chỉ số cho thấy nguy cơ tiểu đường đáng kể (đường huyết, insulin, yếu tố di truyền, BMI).")
    elif has_glucose and not has_lipid:
        parts.append("Chỉ số đường huyết cho thấy nguy cơ tiền tiểu đường hoặc tiểu đường.")

    if has_insulin and "Insulin" not in str(parts):
        # Check if insulin is low or high
        insulin_results = [r for r in danger + warning if r["name"] == "Insulin"]
        if insulin_results:
            parts.append("Chỉ số insulin bất thường, cần đánh giá chức năng tuyến tụy.")

    if has_kidney:
        parts.append("Chức năng thận có dấu hiệu suy giảm, cần theo dõi thêm.")

    if has_bp:
        bp_results = [r for r in danger + warning
                      if _NAME_TO_KEY.get(r["name"]) in {"BP_Systolic", "BP_Diastolic"}]
        if bp_results:
            val = bp_results[0]["value"]
            if val < 90:
                parts.append("Huyết áp thấp, có nguy cơ thiếu máu nuôi các cơ quan.")
            else:
                parts.append("Huyết áp ở mức cần chú ý, có nguy cơ tăng huyết áp.")

    if has_skin and "Độ dày" not in str(parts):
        parts.append("Chỉ số mỡ dưới da bất thường, liên quan nguy cơ tiểu đường tuýp 2.")

    if has_dpf and "di truyền" not in str(parts):
        parts.append("Yếu tố di truyền tiểu đường từ gia đình ở mức cao.")

    if not parts:
        if danger:
            parts.append("Một số chỉ số sức khỏe của bạn đang ở mức đáng lo ngại.")
        else:
            parts.append("Một số chỉ số sức khỏe cần được chú ý.")

    if danger:
        parts.append(f"Có {len(danger)} chỉ số ở mức nguy hiểm.")
    if warning:
        parts.append(f"Có {len(warning)} chỉ số ở mức cảnh báo.")

    return " ".join(parts)


def generate_advice(results: list[dict], age: int | None = None, smoking: bool = False) -> list[str]:
    """Generate health advice based on results."""
    advice = []
    danger = [r for r in results if r["color"] == "red"]
    warning = [r for r in results if r["color"] == "yellow"]

    # Map result names back to raw keys
    abnormal_keys = {_NAME_TO_KEY.get(r["name"], r["name"]) for r in danger + warning}
    abnormal_values = {_NAME_TO_KEY.get(r["name"], r["name"]): r["value"] for r in danger + warning}

    # Lipid advice
    if abnormal_keys & {"LDL", "HDL"}:
        advice.append("Hạn chế thực phẩm giàu chất béo bão hòa và cholesterol (đồ chiên, nội tạng, thức ăn nhanh).")
        advice.append("Tăng cường rau xanh, trái cây, và các loại cá giàu omega-3.")
        advice.append("Tập thể dục ít nhất 30 phút mỗi ngày, 5 ngày/tuần.")

    # Glucose advice
    if "Glucose" in abnormal_keys:
        glucose_val = abnormal_values.get("Glucose", 999)
        if glucose_val > 100:
            advice.append("Hạn chế đường, tinh bột trắng và đồ ngọt.")
            advice.append("Ăn nhiều chất xơ, ngũ cốc nguyên hạt.")
            advice.append("Kiểm tra đường huyết định kỳ.")
        else:
            advice.append("Đường huyết thấp: nên ăn nhẹ thường xuyên, tránh nhịn ăn quá lâu.")
            advice.append("Luôn mang theo kẹo hoặc nước trái cây phòng khi hạ đường huyết đột ngột.")

    # Insulin advice
    if "Insulin" in abnormal_keys:
        insulin_val = abnormal_values.get("Insulin", 0)
        if insulin_val > 24.9:
            advice.append("Insulin cao: giảm cân nếu thừa cân, tăng vận động để cải thiện độ nhạy insulin.")
            advice.append("Hạn chế carbohydrate tinh chế và đường.")
        else:
            advice.append("Insulin thấp: cần theo dõi chức năng tuyến tụy, có thể cần hỗ trợ insulin y khoa.")

    # Kidney advice
    if "Creatinine" in abnormal_keys:
        advice.append("Uống đủ nước mỗi ngày (1.5–2 lít).")
        advice.append("Hạn chế muối và protein động vật quá mức.")
        advice.append("Tránh sử dụng thuốc giảm đau không kê đơn thường xuyên.")

    # BP advice
    if abnormal_keys & {"BP_Systolic", "BP_Diastolic"}:
        sys_val = abnormal_values.get("BP_Systolic", abnormal_values.get("BP_Diastolic", 120))
        if sys_val > 120:
            advice.append("Giảm muối trong khẩu phần ăn (dưới 5g/ngày).")
            advice.append("Hạn chế rượu bia và caffeine.")
            advice.append("Kiểm tra huyết áp thường xuyên tại nhà.")
        else:
            advice.append("Huyết áp thấp: uống đủ nước, tránh đứng dậy quá nhanh.")
            advice.append("Ăn đủ bữa, có thể bổ sung muối vừa phải nếu huyết áp quá thấp.")

    # BMI advice
    if "BMI" in abnormal_keys:
        bmi_val = abnormal_values.get("BMI", 22)
        if bmi_val > 24.9:
            advice.append("Duy trì chế độ ăn cân bằng, kiểm soát lượng calo nạp vào.")
            advice.append("Tăng cường vận động thể chất hàng ngày.")
        else:
            advice.append("BMI thấp: tăng cường dinh dưỡng, ăn đủ bữa và bổ sung protein.")
            advice.append("Nên kiểm tra tình trạng loãng xương và suy dinh dưỡng.")

    # SkinThickness advice
    if "SkinThickness" in abnormal_keys:
        skin_val = abnormal_values.get("SkinThickness", 20)
        if skin_val > 25:
            advice.append("Mỡ dưới da cao: kết hợp chế độ ăn và tập luyện để giảm mỡ cơ thể.")
        else:
            advice.append("Mỡ dưới da thấp: cần đánh giá rối loạn phân bố mỡ, nên tham vấn bác sĩ.")

    # DPF advice
    if "DiabetesPedigreeFunction" in abnormal_keys:
        advice.append("Có yếu tố di truyền tiểu đường: duy trì lối sống lành mạnh là cách phòng ngừa tốt nhất.")
        advice.append("Kiểm tra đường huyết định kỳ 6 tháng/lần dù chưa có triệu chứng.")

    # Smoking
    if smoking:
        advice.append("Bỏ thuốc lá ngay – hút thuốc làm tăng đáng kể nguy cơ tim mạch và nhiều bệnh khác.")

    # Age factor
    if age and age >= 45:
        advice.append("Ở độ tuổi trên 45, nên khám sức khỏe tổng quát định kỳ 6 tháng/lần.")

    if danger:
        advice.append("Bạn nên đặt lịch khám chuyên khoa tại Vinmec để được tư vấn chi tiết.")

    if not advice:
        advice.append("Tiếp tục duy trì lối sống lành mạnh và khám sức khỏe định kỳ.")

    advice.append("Lưu ý: AI chỉ cung cấp thông tin tham khảo, KHÔNG thay thế chẩn đoán của Bác sĩ.")

    return advice


def analyze(data: dict, age: int | None = None, smoking: bool = False) -> dict:
    """Main analysis function."""
    indicator_data = {k: v for k, v in data.items() if k not in ("age", "smoking")}
    validate_indicators(indicator_data)

    results = []
    for name, value in indicator_data.items():
        results.append(evaluate_indicator(name, value))

    summary = generate_summary(results)
    advice = generate_advice(results, age=age, smoking=smoking)

    critical = [r["name"] for r in results if r["color"] == "red"]
    if critical:
        triage = "urgent"
    elif any(r["color"] == "yellow" for r in results):
        triage = "monitor"
    else:
        triage = "ok"

    # compute overall confidence: take the minimum indicator confidence as conservative measure
    confidences = [r.get("confidence", 0.5) for r in results]
    overall_confidence = round(float(min(confidences)) if confidences else 0.5, 2)
    low_confidence = overall_confidence < 0.6 or any(c < 0.6 for c in confidences)

    return {
        "indicators": results,
        "summary": summary,
        "advice": advice,
        "triage": triage,
        "critical_indicators": critical,
        "confidence_overall": overall_confidence,
        "low_confidence": low_confidence,
    }
