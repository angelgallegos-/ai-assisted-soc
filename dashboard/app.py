import os

import requests
import streamlit as st

API_URL = os.getenv("API_URL", "http://localhost:8000")

VERDICT_STYLE = {
    "true_positive": ("🔴", "True positive"),
    "false_positive": ("🟢", "False positive"),
    "benign": ("🟢", "Benign"),
    "needs_investigation": ("🟠", "Needs investigation"),
}

st.title("AI-Assisted SOC")

if st.button("Analyze Alert"):
    try:
        with st.spinner("Triaging alert with the local LLM..."):
            response = requests.post(f"{API_URL}/triage", timeout=300)
        response.raise_for_status()
    except requests.RequestException as exc:
        detail = ""
        if getattr(exc, "response", None) is not None:
            try:
                detail = exc.response.json().get("detail", "")
            except ValueError:
                detail = exc.response.text
        st.error(f"Triage request failed: {detail or exc}")
        st.stop()

    data = response.json()
    result = data["result"]
    icon, label = VERDICT_STYLE.get(result["verdict"], ("⚪", result["verdict"]))

    if data["fallback"]:
        st.warning("The model's output never matched the schema, so this alert was routed to manual review.")

    st.subheader(f"{icon} {label}")
    st.progress(result["confidence"] / 100, text=f"Confidence: {result['confidence']}%")
    st.write(result["summary"])

    st.markdown("**Reasoning**")
    st.write(result["reasoning"])

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**MITRE ATT&CK**")
        for technique in result["mitre_techniques"] or ["None identified"]:
            st.markdown(f"- {technique}")
    with col2:
        st.markdown("**IOCs**")
        for ioc in result["iocs"] or ["None identified"]:
            st.markdown(f"- `{ioc}`")

    st.markdown("**Recommended actions**")
    for i, action in enumerate(result["recommended_actions"], start=1):
        st.markdown(f"{i}. {action}")

    st.caption(
        f"Alert {data['alert_id']} · {data['model']} · prompt {data['prompt_version']} · "
        f"{data['attempts']} attempt(s) · {data['latency_ms']} ms"
    )
    with st.expander("Raw JSON"):
        st.json(data)
