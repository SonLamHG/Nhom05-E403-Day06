import base64
import json
import math
import os
from datetime import datetime
from collections import OrderedDict
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from openai import OpenAI, OpenAIError
from pydantic import BaseModel, ConfigDict, Field, field_validator

from .rules import analyze, INDICATORS

load_dotenv()

app = FastAPI(title="VinBiocare AI", version="2.0.0")

_ALLOWED_ORIGINS = [
    o.strip()
    for o in os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost:8000,http://127.0.0.1:8000"
    ).split(",")
    if o.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_ALLOWED_ORIGINS,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

FRONTEND_DIR = Path(__file__).parent.parent / "frontend"
PROMPTS_DIR = Path(__file__).parent / "prompts"
LOGS_DIR = Path(__file__).parent / "logs"
CORRECTION_LOG_PATH = LOGS_DIR / "correctionLog.json"
REVIEW_QUEUE_PATH = LOGS_DIR / "reviewQueue.jsonl"

# Load system prompt
SYSTEM_PROMPT = (PROMPTS_DIR / "system.txt").read_text(encoding="utf-8")
OCR_SYSTEM_PROMPT = (PROMPTS_DIR / "ocr.txt").read_text(encoding="utf-8")

# OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
LLM_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
VISION_MODEL = os.getenv("OPENAI_VISION_MODEL", "gpt-4.1-mini")

# LRU cache for repeated prompts — capped to avoid memory leak
_LLM_CACHE_MAX = 500
_llm_cache: OrderedDict[str, str] = OrderedDict()


# --- Models ---

class AnalyzeRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    indicators: dict[str, float] = Field(min_length=1)
    age: int | None = Field(default=None, ge=0, le=120)
    smoking: bool = False

    @field_validator("indicators")
    @classmethod
    def validate_indicators(cls, value: dict[str, float]) -> dict[str, float]:
        errors: list[str] = []

        for key, indicator_value in value.items():
            normalized_key = key.strip() if isinstance(key, str) else ""
            if not normalized_key:
                errors.append("Tên chỉ số không được để trống")
                continue

            if not math.isfinite(indicator_value):
                errors.append(f"{normalized_key}: giá trị phải là số hữu hạn")
                continue

            if indicator_value < 0 or indicator_value > 10000:
                errors.append(
                    f"{normalized_key}: giá trị {indicator_value} nằm ngoài khoảng cho phép [0, 10000]"
                )

        if errors:
            raise ValueError("; ".join(errors))

        return value


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: list[ChatMessage]
    context: dict | None = None
    analysis_history: list[dict] | None = None


class FeedbackRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    session_id: str = Field(min_length=1, max_length=200)
    user_input: str = Field(min_length=1, max_length=5000)
    ai_response: str = Field(min_length=1, max_length=10000)
    correction_type: str
    feedback_reason: str | None = Field(default=None, max_length=500)
    flow_state: str | None = Field(default=None, max_length=50)
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    source: str | None = Field(default=None, max_length=50)
    needs_review: bool = False

    @field_validator("correction_type")
    @classmethod
    def validate_correction_type(cls, value: str) -> str:
        normalized = value.strip().lower()
        if normalized not in {"positive", "negative", "doctor_review"}:
            raise ValueError("correction_type must be 'positive', 'negative', or 'doctor_review'")
        return normalized

    @field_validator("flow_state")
    @classmethod
    def validate_flow_state(cls, value: str | None) -> str | None:
        if value is None:
            return None

        normalized = value.strip().lower()
        if normalized not in {"happy", "low_confidence", "failure", "correction"}:
            raise ValueError("flow_state must be one of: happy, low_confidence, failure, correction")
        return normalized


# --- Endpoints ---

@app.get("/api/indicators")
def get_indicators():
    """Return available indicators with their reference ranges."""
    return INDICATORS


@app.post("/api/analyze")
def analyze_indicators(req: AnalyzeRequest):
    """Analyze health indicators using rule-based engine (no LLM)."""
    try:
        return analyze(req.indicators, age=req.age, smoking=req.smoking)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@app.post("/api/ocr")
async def ocr_extract(image: UploadFile = File(...)):
    """Extract health indicators from a lab test image using GPT vision."""
    # Validate file type
    if not image.content_type or not image.content_type.startswith("image/"):
        raise HTTPException(status_code=422, detail="File không phải hình ảnh. Vui lòng chọn file PNG, JPG hoặc JPEG.")

    # Read and validate size (max 10MB)
    image_bytes = await image.read()
    if len(image_bytes) > 10 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="File quá lớn. Vui lòng chọn file dưới 10MB.")

    # Encode to base64 data URL
    b64 = base64.b64encode(image_bytes).decode("utf-8")
    data_url = f"data:{image.content_type};base64,{b64}"

    # Call GPT vision
    try:
        vision_response = client.chat.completions.create(
            model=VISION_MODEL,
            messages=[
                {"role": "system", "content": OCR_SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Hãy đọc các chỉ số xét nghiệm từ hình ảnh này và trả về JSON."},
                        {"type": "image_url", "image_url": {"url": data_url, "detail": "high"}},
                    ],
                },
            ],
            temperature=0.0,
            max_tokens=500,
        )
    except OpenAIError as e:
        raise HTTPException(status_code=502, detail=f"Lỗi kết nối dịch vụ AI: {e}")

    # Parse response — strip markdown fences if present
    raw_text = vision_response.choices[0].message.content.strip()
    if raw_text.startswith("```"):
        raw_text = raw_text.split("\n", 1)[1]
        raw_text = raw_text.rsplit("```", 1)[0]

    try:
        extracted = json.loads(raw_text.strip())
    except json.JSONDecodeError:
        raise HTTPException(status_code=422, detail="Không thể đọc chỉ số từ ảnh này. Vui lòng thử ảnh rõ hơn hoặc nhập thủ công.")

    # Filter: keep only known indicators with numeric values
    valid_keys = set(INDICATORS.keys())
    extracted = {k: float(v) for k, v in extracted.items() if k in valid_keys and isinstance(v, (int, float))}

    if not extracted:
        raise HTTPException(status_code=422, detail="Không nhận diện được chỉ số xét nghiệm nào từ ảnh. Vui lòng thử ảnh khác.")

    # Run rule-based analysis
    try:
        rule_output = analyze(extracted)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    return {"extracted_indicators": extracted, "rule_output": rule_output}


@app.post("/api/feedback/correction")
def log_correction(feedback: FeedbackRequest):
    """Append user feedback for later review and prompt tuning."""
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    record = {
        **feedback.model_dump(),
        "created_at": datetime.utcnow().isoformat() + "Z",
    }
    queued_for_review = feedback.needs_review or feedback.correction_type in {"negative", "doctor_review"}

    with CORRECTION_LOG_PATH.open("a", encoding="utf-8") as log_file:
        json.dump(record, log_file, ensure_ascii=False)
        log_file.write("\n")

    if queued_for_review:
        review_record = {
            **record,
            "review_status": "pending",
        }
        with REVIEW_QUEUE_PATH.open("a", encoding="utf-8") as queue_file:
            json.dump(review_record, queue_file, ensure_ascii=False)
            queue_file.write("\n")

    return {"status": "logged", "queued_for_review": queued_for_review}


@app.post("/api/chat")
def chat(req: ChatRequest):
    """Chat endpoint: combines rule_output context with OpenAI for natural responses."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY not configured")

    # Build messages for OpenAI
    openai_messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    # If rule_output context provided, inject it
    rule_output = None
    if req.context and req.context.get("rule_output"):
        rule_output = req.context["rule_output"]
        context_msg = (
            f"Dữ liệu phân tích từ rule-based engine:\n"
            f"```json\n{json.dumps(rule_output, ensure_ascii=False, indent=2)}\n```\n"
            f"Hãy dựa vào dữ liệu trên để trả lời câu hỏi của người dùng."
        )
        openai_messages.append({"role": "system", "content": context_msg})

    # If analysis history has 2+ entries, inject comparison context
    if req.analysis_history and len(req.analysis_history) >= 2:
        last_two = req.analysis_history[-2:]
        comparison_msg = (
            f"Người dùng muốn so sánh 2 kết quả xét nghiệm gần nhất:\n\n"
            f"**Kết quả lần {len(req.analysis_history) - 1}:**\n"
            f"```json\n{json.dumps(last_two[0], ensure_ascii=False, indent=2)}\n```\n\n"
            f"**Kết quả lần {len(req.analysis_history)}:**\n"
            f"```json\n{json.dumps(last_two[1], ensure_ascii=False, indent=2)}\n```\n\n"
            f"Hãy so sánh 2 kết quả trên, chỉ ra các chỉ số thay đổi (tốt hơn/xấu hơn/không đổi) và đưa ra nhận xét tổng thể."
        )
        openai_messages.append({"role": "system", "content": comparison_msg})

    # Add conversation history
    for msg in req.messages:
        openai_messages.append({"role": msg.role, "content": msg.content})

    # Check cache
    cache_key = json.dumps(openai_messages, ensure_ascii=False)
    if cache_key in _llm_cache:
        return {"reply": _llm_cache[cache_key], "rule_output": rule_output}

    # Call OpenAI
    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=openai_messages,
        temperature=0.7,
        max_tokens=500,
    )

    reply = response.choices[0].message.content
    _llm_cache[cache_key] = reply
    if len(_llm_cache) > _LLM_CACHE_MAX:
        _llm_cache.popitem(last=False)  # evict oldest entry

    return {"reply": reply, "rule_output": rule_output}


# --- Serve frontend ---

app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")


@app.get("/")
def serve_frontend():
    return FileResponse(str(FRONTEND_DIR / "index.html"))
