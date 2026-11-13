import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent

load_dotenv(PROJECT_ROOT / ".env")

OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
OLLAMA_HOST = os.getenv("OLLAMA_HOST")  # None -> ollama client default (localhost:11434)
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0"))
TRIAGE_MAX_ATTEMPTS = int(os.getenv("TRIAGE_MAX_ATTEMPTS", "2"))
PROMPT_VERSION = os.getenv("PROMPT_VERSION", "triage_v1")

PROMPTS_DIR = PROJECT_ROOT / "app" / "prompts"
ALERTS_DIR = PROJECT_ROOT / "data" / "alerts"
