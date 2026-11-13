from typing import Literal

from pydantic import BaseModel, Field

Verdict = Literal["true_positive", "false_positive", "benign", "needs_investigation"]


class TriageResult(BaseModel):
    """Structured verdict returned by the LLM triage step.

    This schema is passed to the model as a JSON-schema constraint and used to
    validate its reply, so field descriptions double as instructions.
    """

    summary: str = Field(description="One or two sentence executive summary of the alert.")
    verdict: Verdict = Field(description="Triage decision for this alert.")
    confidence: int = Field(ge=0, le=100, description="Confidence in the verdict, 0-100.")
    reasoning: str = Field(description="Key evidence from the alert that supports the verdict.")
    mitre_techniques: list[str] = Field(
        default_factory=list,
        description="Relevant MITRE ATT&CK technique IDs with names, e.g. 'T1059.001 PowerShell'.",
    )
    iocs: list[str] = Field(
        default_factory=list,
        description="Indicators of compromise found in the alert (hosts, users, hashes, IPs, commands).",
    )
    recommended_actions: list[str] = Field(
        default_factory=list,
        description="Concrete next steps for the SOC analyst, most important first.",
    )


class TriageResponse(BaseModel):
    """What the triage pipeline returns: the result plus how it was produced."""

    alert_id: str
    result: TriageResult
    model: str
    prompt_version: str
    attempts: int
    fallback: bool = Field(description="True when the LLM output never validated and a safe default was used.")
    latency_ms: int
    error: str | None = None
