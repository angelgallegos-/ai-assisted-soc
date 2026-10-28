import json
from app.models.alert import Alert

def load_alert(path: str) -> Alert:
    with open(path, "r") as file:
        data = json.load(file)
    return Alert(**data)
