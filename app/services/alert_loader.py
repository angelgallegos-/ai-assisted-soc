import json
from pathlib import Path

from app import config
from app.models.alert import Alert


def load_alert(path: str | Path) -> Alert:
    path = Path(path)
    if not path.is_absolute():
        path = config.PROJECT_ROOT / path
    with open(path, "r", encoding="utf-8") as file:
        data = json.load(file)
    return Alert(**data)
