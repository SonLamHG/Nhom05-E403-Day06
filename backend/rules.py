import json
from pathlib import Path

DATA_PATH = Path(__file__).parent / "data" / "indicators.json"

def load_indicators():
    with open(DATA_PATH, encoding="utf-8") as f:
        return json.load(f)

INDICATORS = load_indicators()


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

    return {
        "name": info["name"],
        "value": value,
        "unit": info["unit"],
        "status": status,
        "color": color,
        "message": message,
        "reference": f"{info['normal_min']}–{info['normal_max']} {info['unit']}"
    }


def generate_summary(results: list[dict]) -> str:
    """Generate overall health summary based on evaluated indicators."""
    danger = [r for r in results if r["color"] == "red"]
    warning = [r for r in results if r["color"] == "yellow"]

    if not danger and not warning:
        return "Các chỉ số xét nghiệm của bạn đều nằm trong giới hạn bình thường. Hãy tiếp tục duy trì lối sống lành mạnh!"

    # Collect raw indicator keys from results for pattern detection
    raw_keys = set()
    for r in danger + warning:
        for key, info in INDICATORS.items():
            if info["name"] == r["name"]:
                raw_keys.add(key)

    has_lipid = bool(raw_keys & {"LDL", "HDL"})
    has_glucose = "Glucose" in raw_keys
    has_insulin = "Insulin" in raw_keys
    has_kidney = "Creatinine" in raw_keys
    has_bp = "BloodPressure" in raw_keys
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
        bp_results = [r for r in danger + warning for key, info in INDICATORS.items()
                      if key == "BloodPressure" and info["name"] == r["name"]]
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
    abnormal_keys = set()
    for r in danger + warning:
        for key, info in INDICATORS.items():
            if info["name"] == r["name"]:
                abnormal_keys.add(key)

    # Also track direction (high/low) for bidirectional indicators
    abnormal_values = {}
    for r in danger + warning:
        for key, info in INDICATORS.items():
            if info["name"] == r["name"]:
                abnormal_values[key] = r["value"]

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
    if "BloodPressure" in abnormal_keys:
        bp_val = abnormal_values.get("BloodPressure", 120)
        if bp_val > 120:
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

    return advice


def analyze(data: dict, age: int | None = None, smoking: bool = False) -> dict:
    """Main analysis function."""
    results = []
    for name, value in data.items():
        if name in ("age", "smoking"):
            continue
        results.append(evaluate_indicator(name, value))

    summary = generate_summary(results)
    advice = generate_advice(results, age=age, smoking=smoking)

    return {
        "indicators": results,
        "summary": summary,
        "advice": advice
    }
