import json
import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from openai import OpenAI
from pydantic import BaseModel

from rules import analyze, INDICATORS

load_dotenv()

app = FastAPI(title="VinBiocare AI", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

FRONTEND_DIR = Path(__file__).parent.parent / "frontend"
PROMPTS_DIR = Path(__file__).parent / "prompts"

# Load system prompt
SYSTEM_PROMPT = (PROMPTS_DIR / "system.txt").read_text(encoding="utf-8")

# OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
LLM_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# Cache for repeated prompts during demo
_llm_cache: dict[str, str] = {}


# --- Models ---

class AnalyzeRequest(BaseModel):
    indicators: dict[str, float]
    age: int | None = None
    smoking: bool = False


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: list[ChatMessage]
    context: dict | None = None


# --- Endpoints ---

@app.get("/api/indicators")
def get_indicators():
    """Return available indicators with their reference ranges."""
    return INDICATORS


@app.post("/api/analyze")
def analyze_indicators(req: AnalyzeRequest):
    """Analyze health indicators using rule-based engine (no LLM)."""
    return analyze(req.indicators, age=req.age, smoking=req.smoking)


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

    return {"reply": reply, "rule_output": rule_output}


# --- Serve frontend ---

app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")


@app.get("/")
def serve_frontend():
    return FileResponse(str(FRONTEND_DIR / "index.html"))
