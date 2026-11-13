# Roadmap

## Phase 1: Foundation

- [x] Alert ingestion
- [x] Ollama integration
- [x] FastAPI
- [x] Streamlit

## Phase 2: Structured triage

- [x] Structured JSON output (schema-constrained and validated)
- [x] Retry on invalid output and fallback to manual review
- [x] Prompt-injection hardening for alert content
- [x] Versioned prompts and configuration via `.env`
- [x] MITRE ATT&CK mapping (LLM-suggested; accuracy not yet measured)
- [ ] Richer alert model (timestamp, source, process and command line, raw event)
- [ ] Labeled sample alerts covering each verdict
- [ ] Evaluation script (accuracy, confusion matrix, latency per model and prompt)
- [ ] Risk scoring

## Phase 3: Context and workflow

- [ ] Enrichment (asset criticality, user role, IOC reputation)
- [ ] Routing rules (auto-close, escalate) based on verdict, confidence and severity
- [ ] Persist triage results (alert, prompt version, model, raw output, latency)
- [ ] Analyst feedback (confirm or override verdict)
- [ ] Historical review

## Phase 4: Knowledge

- [ ] RAG
- [ ] Playbook recommendations

## Phase 5: Integration

- [ ] Microsoft Sentinel integration
