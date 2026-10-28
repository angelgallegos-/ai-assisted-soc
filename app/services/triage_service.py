from pathlib import Path
from app.services.llm_service import generate_response

PROMPT_PATH = Path("app/prompts/triage_prompt.txt")

def analyze_alert(alert):
    template = PROMPT_PATH.read_text()
    prompt = template.format(alert=alert.model_dump_json(indent=2))
    return generate_response(prompt)
