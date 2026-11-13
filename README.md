# AI-Assisted SOC

A proof-of-concept that uses a local LLM to help SOC analysts triage security alerts. Each alert gets a structured verdict, confidence score, MITRE ATT&CK mapping, IOCs, and recommended next steps, validated against a schema before it reaches the analyst.

## Features

- Alert ingestion from JSON
- LLM triage with **structured, schema-validated output**
- Automatic retry on invalid output, and a fail-safe that routes to manual review
- Prompt-injection hardening: alert content is delimited and treated as untrusted data
- FastAPI backend with a typed response model
- Streamlit dashboard for analysts
- Local inference via Ollama (no data leaves the machine)

## How it works

```
Alert JSON
    ↓
FastAPI  POST /triage
    ↓
Prompt   versioned system prompt + <alert> delimited as untrusted data
    ↓
Ollama   output constrained to the TriageResult JSON schema
    ↓
Validate Pydantic check → retry once with errors → fallback to manual review
    ↓
TriageResponse
    ↓
Dashboard
```

See [docs/architecture.md](docs/architecture.md) for details.

## Quick start

Requires Python 3.11+ and [Ollama](https://ollama.com/download).

```bash
git clone https://github.com/angelgallegos-/ai-assisted-soc.git
cd ai-assisted-soc
python -m venv .venv
```

Activate the environment (Windows: `.venv\Scripts\activate`, Linux/macOS: `source .venv/bin/activate`), then:

```bash
pip install -r requirements.txt
cp .env.example .env        # Windows: copy .env.example .env
ollama pull llama3.1:8b
```

Run each of these in its own terminal from the project root:

```bash
ollama serve
uvicorn api.main:app --reload
streamlit run dashboard/app.py
```

Then open:

- Dashboard: http://localhost:8501
- API docs: http://localhost:8000/docs

Full instructions and troubleshooting: [docs/setup.md](docs/setup.md).

## Example output

`POST /triage` returns a `TriageResponse` (values are illustrative):

```json
{
  "alert_id": "A001",
  "result": {
    "summary": "PowerShell launched with base64-encoded commands on a finance workstation.",
    "verdict": "needs_investigation",
    "confidence": 60,
    "reasoning": "Encoded commands are a common obfuscation technique, but the alert lacks context to confirm intent.",
    "mitre_techniques": ["T1059.001 PowerShell", "T1027 Obfuscated Files or Information"],
    "iocs": ["FIN-PC01", "alice"],
    "recommended_actions": ["Decode the PowerShell command", "Review alice's recent logons"]
  },
  "model": "llama3.1:8b",
  "prompt_version": "triage_v1",
  "attempts": 1,
  "fallback": false,
  "latency_ms": 12480,
  "error": null
}
```

`verdict` is one of `true_positive`, `false_positive`, `benign`, or `needs_investigation`. If the model never produces valid output, `fallback` is `true` and the verdict is `needs_investigation` with confidence 0.

> Schema validation guarantees the output's **shape**, not its **accuracy**. Small local models can still suggest wrong MITRE IDs or list non-IOCs, so treat results as analyst assistance, not decisions.

## Configuration

Settings are read from `.env` (see `.env.example`):

| Variable | Default | Purpose |
|---|---|---|
| `OLLAMA_MODEL` | `llama3.1:8b` | Model used for triage |
| `OLLAMA_HOST` | Ollama default (`http://localhost:11434`) | Ollama server URL |
| `LLM_TEMPERATURE` | `0` | Sampling temperature; 0 for repeatable results |
| `TRIAGE_MAX_ATTEMPTS` | `2` | Attempts before falling back to manual review |
| `PROMPT_VERSION` | `triage_v1` | Prompt file in `app/prompts/` |
| `API_URL` | `http://localhost:8000` | API address used by the dashboard |

## Project layout

```
api/main.py                     FastAPI app
app/config.py                   Settings loaded from .env
app/models/alert.py             Alert input model
app/models/triage_result.py     TriageResult schema and TriageResponse
app/prompts/triage_v1.txt       Versioned system prompt
app/services/alert_loader.py    Loads alerts from JSON
app/services/llm_service.py     Ollama client with schema-constrained output
app/services/triage_service.py  Prompt building, validation, retry, fallback
dashboard/app.py                Streamlit analyst dashboard
data/alerts/                    Sample alerts
tests/                          Pytest suite (LLM mocked)
```

## Tests

```bash
pytest
```

Tests mock the LLM, so Ollama does not need to be running.

## Documentation

- [Setup](docs/setup.md)
- [Architecture](docs/architecture.md)
- [Roadmap](docs/roadmap.md)
