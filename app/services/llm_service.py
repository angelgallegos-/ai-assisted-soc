import ollama

from app import config


class LLMUnavailableError(RuntimeError):
    """Raised when the LLM backend cannot be reached."""


_client = ollama.Client(host=config.OLLAMA_HOST) if config.OLLAMA_HOST else ollama.Client()


def generate_response(messages: list[dict], schema: dict | None = None) -> str:
    """Send a chat request and return the raw message content.

    When ``schema`` is given, Ollama constrains decoding to JSON matching it.
    """
    try:
        response = _client.chat(
            model=config.OLLAMA_MODEL,
            messages=messages,
            format=schema,
            options={"temperature": config.LLM_TEMPERATURE},
        )
    except (ConnectionError, ollama.ResponseError) as exc:
        raise LLMUnavailableError(f"Ollama request failed: {exc}") from exc
    return response["message"]["content"]
