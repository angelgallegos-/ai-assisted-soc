import json

import pytest
from fastapi.testclient import TestClient

from api.main import app
from app.services import triage_service
from app.services.alert_loader import load_alert
from app.services.llm_service import LLMUnavailableError

SAMPLE = "data/alerts/suspicious_powershell.json"

VALID = {
    "summary": "Encoded PowerShell on a finance workstation.",
    "verdict": "true_positive",
    "confidence": 85,
    "reasoning": "Base64-encoded commands are a common obfuscation technique.",
    "mitre_techniques": ["T1059.001 PowerShell", "T1027 Obfuscated Files or Information"],
    "iocs": ["FIN-PC01", "alice"],
    "recommended_actions": ["Isolate FIN-PC01", "Decode the command line"],
}


class FakeLLM:
    """Returns queued responses in order and records the messages it received."""

    def __init__(self, *responses):
        self.responses = list(responses)
        self.calls = []

    def __call__(self, messages, schema=None):
        self.calls.append({"messages": messages, "schema": schema})
        return self.responses.pop(0)


@pytest.fixture
def alert():
    return load_alert(SAMPLE)


def test_alert_loads(alert):
    assert alert.id == "A001"


def test_valid_response_is_parsed(monkeypatch, alert):
    fake = FakeLLM(json.dumps(VALID))
    monkeypatch.setattr(triage_service, "generate_response", fake)

    response = triage_service.analyze_alert(alert)

    assert response.result.verdict == "true_positive"
    assert response.result.confidence == 85
    assert response.attempts == 1
    assert response.fallback is False
    assert fake.calls[0]["schema"] == triage_service.TRIAGE_SCHEMA


def test_alert_is_delimited_as_untrusted_data(monkeypatch, alert):
    fake = FakeLLM(json.dumps(VALID))
    monkeypatch.setattr(triage_service, "generate_response", fake)

    triage_service.analyze_alert(alert)

    system, user = fake.calls[0]["messages"]
    assert system["role"] == "system" and "untrusted" in system["content"]
    assert user["content"].startswith("<alert>") and user["content"].endswith("</alert>")


def test_invalid_response_is_retried_with_errors(monkeypatch, alert):
    bad = json.dumps({**VALID, "verdict": "malicious", "confidence": 150})
    fake = FakeLLM(bad, json.dumps(VALID))
    monkeypatch.setattr(triage_service, "generate_response", fake)

    response = triage_service.analyze_alert(alert)

    assert response.attempts == 2
    assert response.fallback is False
    feedback = fake.calls[1]["messages"][-1]["content"]
    assert "verdict" in feedback and "confidence" in feedback


def test_falls_back_to_manual_review_when_never_valid(monkeypatch, alert):
    fake = FakeLLM("not json", "still not json")
    monkeypatch.setattr(triage_service, "generate_response", fake)

    response = triage_service.analyze_alert(alert)

    assert response.fallback is True
    assert response.result.verdict == "needs_investigation"
    assert response.result.confidence == 0
    assert response.error


def test_api_returns_structured_result(monkeypatch):
    monkeypatch.setattr(triage_service, "generate_response", FakeLLM(json.dumps(VALID)))

    resp = TestClient(app).post("/triage")

    assert resp.status_code == 200
    body = resp.json()
    assert body["alert_id"] == "A001"
    assert body["result"]["verdict"] == "true_positive"


def test_api_accepts_alert_in_body(monkeypatch):
    monkeypatch.setattr(triage_service, "generate_response", FakeLLM(json.dumps(VALID)))
    custom = {
        "id": "A999",
        "title": "Test",
        "severity": "Low",
        "user": "bob",
        "host": "HR-PC02",
        "description": "Test alert.",
    }

    resp = TestClient(app).post("/triage", json=custom)

    assert resp.status_code == 200
    assert resp.json()["alert_id"] == "A999"


def test_api_returns_503_when_llm_unavailable(monkeypatch):
    def unavailable(messages, schema=None):
        raise LLMUnavailableError("connection refused")

    monkeypatch.setattr(triage_service, "generate_response", unavailable)

    resp = TestClient(app).post("/triage")

    assert resp.status_code == 503
