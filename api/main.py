from fastapi import FastAPI
from app.services.alert_loader import load_alert
from app.services.triage_service import analyze_alert

app = FastAPI()

@app.get("/")
def root():
    return {"status": "healthy"}

@app.post("/triage")
def triage():
    alert = load_alert("data/alerts/suspicious_powershell.json")
    result = analyze_alert(alert)
    return {"analysis": result}
