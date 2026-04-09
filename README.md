# VinBiocare AI — Prototype

Short demo prototype: an AI chatbot that analyzes lab indicators using a rule-based engine and uses OpenAI Chat API to summarize and explain results.

## Features

- Chat-style UI for users to paste or type lab values
- Rule-based analysis (`/analyze`) producing canonical JSON `rule_output`
- OpenAI (Chat Completions) integration via `/chat` to generate friendly summaries, explanations and actionable suggestions

## Prerequisites

- Python 3.10+
- pip
- An OpenAI API key (set via `OPENAI_API_KEY` environment variable)

## Setup

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Set your OpenAI API key (PowerShell):

```powershell
$env:OPENAI_API_KEY = "YOUR_OPENAI_KEY"
```

(Or on Windows permanently: `setx OPENAI_API_KEY "YOUR_OPENAI_KEY"`.)

## Run backend (FastAPI)

From project root you can run:

```bash
uvicorn backend.main:app --reload --port 8000
```

- API docs: http://127.0.0.1:8000/docs

## Run frontend (static)

Open `frontend/index.html` in a browser, or serve the folder:

```bash
cd frontend
python -m http.server 8080
```

Then open: http://127.0.0.1:8080

## Important env vars

- `OPENAI_API_KEY` — required for `/chat`
- `APP_ENV` — optional (e.g., `dev`)

## Notes

- Do NOT commit secrets or `.env` files (a `.gitignore` is included).
- The backend exposes two main endpoints (design):
  - `POST /analyze` — run rule-based analysis and return `rule_output`
  - `POST /chat` — send `messages` + optional `rule_output` to OpenAI and return its reply plus the canonical `rule_output`

## Quick demo flow

1. Start backend
2. Open frontend
3. Paste lab values into chat input and click Analyze

## Troubleshooting

- If port 8000 is in use, choose a different `--port` when running `uvicorn`.
- If OpenAI returns auth errors, verify `OPENAI_API_KEY` is set and valid.

---

File: README.md
