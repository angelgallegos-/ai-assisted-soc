import logging
import time
from functools import lru_cache

from pydantic import ValidationError

from app import config
from app.models.alert import Alert
from app.models.triage_result import TriageResponse, TriageResult
from app.services.llm_service import generate_response

logger = logging.getLogger(__name__)

TRIAGE_SCHEMA = TriageResult.model_json_schema()


@lru_cache
def load_system_prompt(version: str = config.PROMPT_VERSION) -> str:
    return (config.PROMPTS_DIR / f"{version}.txt").read_text(encoding="utf-8")


def build_messages(alert: Alert) -> list[dict]:
    return [
        {"role": "system", "content": load_system_prompt()},
        {
            "role": "user",
            "content": f"<alert>\n{alert.model_dump_json(indent=2)}\n</alert>",
        },
    ]


def fallback_result(reason: str) -> TriageResult:
    """Safe default when the model never produces valid output: hand it to a human."""
    return TriageResult(
        summary="Automated triage failed; manual review required.",
        verdict="needs_investigation",
        confidence=0,
        reasoning=f"The LLM response could not be validated against the triage schema: {reason}",
        recommended_actions=["Triage this alert manually."],
    )


def analyze_alert(alert: Alert) -> TriageResponse:
    """Run LLM triage on an alert and return a validated, structured result.

    Invalid model output is retried with the validation error fed back to the
    model. If every attempt fails, the alert is routed to manual review rather
    than guessing. LLMUnavailableError propagates to the caller.
    """
    messages = build_messages(alert)
    start = time.perf_counter()
    last_error = ""

    for attempt in range(1, config.TRIAGE_MAX_ATTEMPTS + 1):
        raw = generate_response(messages, schema=TRIAGE_SCHEMA)
        try:
            result = TriageResult.model_validate_json(raw)
        except ValidationError as exc:
            last_error = "; ".join(
                f"{'.'.join(map(str, err['loc'])) or 'response'}: {err['msg']}" for err in exc.errors()
            )
            logger.warning("Alert %s attempt %d: invalid LLM output: %s", alert.id, attempt, last_error)
            messages = messages + [
                {"role": "assistant", "content": raw},
                {
                    "role": "user",
                    "content": f"That response did not match the schema. Errors: {last_error}. "
                    "Return corrected JSON only.",
                },
            ]
            continue

        return TriageResponse(
            alert_id=alert.id,
            result=result,
            model=config.OLLAMA_MODEL,
            prompt_version=config.PROMPT_VERSION,
            attempts=attempt,
            fallback=False,
            latency_ms=int((time.perf_counter() - start) * 1000),
        )

    return TriageResponse(
        alert_id=alert.id,
        result=fallback_result(last_error),
        model=config.OLLAMA_MODEL,
        prompt_version=config.PROMPT_VERSION,
        attempts=config.TRIAGE_MAX_ATTEMPTS,
        fallback=True,
        latency_ms=int((time.perf_counter() - start) * 1000),
        error=last_error,
    )
