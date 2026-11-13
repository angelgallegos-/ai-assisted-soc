# Architecture

## Components

### FastAPI (`api/main.py`)

REST API. `POST /triage` triages the alert in the request body, or the bundled sample alert if the body is empty, and returns a `TriageResponse`. `GET /` is a health check that also reports the model and prompt version.

### Triage service (`app/services/triage_service.py`)

The core of the pipeline. Builds the prompt, calls the LLM, validates the reply, retries, and falls back to manual review when needed.

### LLM service (`app/services/llm_service.py`)

Thin Ollama client. Passes the `TriageResult` JSON schema as `format`, so the model can only generate JSON in that shape, and runs at temperature 0 for repeatable results. Connection and API errors are raised as `LLMUnavailableError`.

### Ollama

Local LLM inference. Alert data never leaves the machine.

### Streamlit dashboard (`dashboard/app.py`)

Analyst view: verdict badge, confidence bar, reasoning, MITRE techniques, IOCs, recommended actions, run metadata, and the raw JSON.

## Data flow

```
Alert (JSON file or request body)
 ↓
Alert model validation          app/models/alert.py
 ↓
Prompt build                    system: app/prompts/triage_v1.txt
                                user:   <alert>…</alert>
 ↓
LLM (Ollama)                    format = TriageResult JSON schema
 ↓
Validate with Pydantic ──fail──→ retry with field errors fed back
 ↓ pass                              ↓ still failing after TRIAGE_MAX_ATTEMPTS
 ↓                               fallback: needs_investigation, confidence 0
 ↓                                   ↓
TriageResponse  ←────────────────────┘
 ↓
API response → Dashboard
```

## Data models

### `Alert`

Input alert: `id`, `title`, `severity`, `user`, `host`, `description`.

### `TriageResult`

What the LLM must return. Field descriptions are part of the JSON schema sent to the model, so they also act as instructions.

| Field | Type | Notes |
|---|---|---|
| `summary` | string | One or two sentence executive summary |
| `verdict` | enum | `true_positive`, `false_positive`, `benign`, `needs_investigation` |
| `confidence` | int | 0–100 |
| `reasoning` | string | Evidence supporting the verdict |
| `mitre_techniques` | list[string] | ATT&CK technique IDs with names |
| `iocs` | list[string] | Indicators found in the alert |
| `recommended_actions` | list[string] | Next steps, most important first |

### `TriageResponse`

What the API returns: `alert_id`, `result` (a `TriageResult`), plus run metadata (`model`, `prompt_version`, `attempts`, `fallback`, `latency_ms`, `error`). The metadata makes each result traceable to the model and prompt that produced it.

## Design decisions

### Constrain, then validate

Ollama's schema-constrained decoding makes valid JSON very likely, but Pydantic still validates every reply. Constraints such as `confidence` between 0 and 100 are enforced in code, not trusted to the model.

### Fail safe

If output never validates, the system does not guess. It returns `needs_investigation` with confidence 0 and sets `fallback: true`, so the alert goes to a human.

### Untrusted alert content

Alert fields such as descriptions and command lines can be attacker-controlled. The alert is sent in a separate user message wrapped in `<alert>` tags, and the system prompt tells the model to treat anything inside as evidence, never as instructions.

### Versioned prompts

Prompts live in `app/prompts/<version>.txt`, selected by `PROMPT_VERSION`. Each response records the version used, so prompt changes can be compared.

### Configuration

All settings come from environment variables or `.env` via `app/config.py`. File paths are resolved from the project root, not the working directory.

## Error handling

| Situation | Behavior |
|---|---|
| Ollama unreachable or model missing | API returns HTTP 503 with the error detail |
| LLM output fails validation | Retried with errors fed back, then fallback result |
| Invalid alert in request body | FastAPI returns HTTP 422 |

## Limitations

- Validation checks structure, not correctness. The model can still return wrong MITRE IDs or list non-IOCs.
- The alert model is minimal and there is no enrichment (asset or user context), so the model often has little to reason over.
- Results are not persisted.
