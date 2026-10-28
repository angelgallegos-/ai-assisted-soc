from app.services.alert_loader import load_alert

def test_alert_loads():
    alert = load_alert("data/alerts/suspicious_powershell.json")
    assert alert.id == "A001"
