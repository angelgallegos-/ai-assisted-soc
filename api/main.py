from fastapi import FastAPI, HTTPException

from app import config
from app.models.alert import Alert
from app.models.triage_result import TriageResponse
from app.services.alert_loader import load_alert
from app.services.llm_service import LLMUnavailableError
from app.services.triage_service import analyze_alert

SAMPLE_ALERT = config.ALERTS_DIR / "suspicious_powershell.json"

app = FastAPI(title="AI-Assisted SOC")


@app.get("/")
def root():
    return {"status": "healthy", "model": config.OLLAMA_MODEL, "prompt_version": config.PROMPT_VERSION}


@app.post("/triage", response_model=TriageResponse)
def triage(alert: Alert | None = None) -> TriageResponse:
    """Triage the alert in the request body, or the bundled sample alert if none is sent."""
    if alert is None:
        alert = load_alert(SAMPLE_ALERT)
    try:
        return analyze_alert(alert)
    except LLMUnavailableError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
