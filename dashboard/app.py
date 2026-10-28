import requests
import streamlit as st

st.title("AI-Assisted SOC")

if st.button("Analyze Alert"):
    response = requests.post("http://localhost:8000/triage")
    result = response.json()
    st.subheader("AI Analysis")
    st.write(result["analysis"])
