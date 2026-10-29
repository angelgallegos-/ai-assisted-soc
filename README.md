# AI-Assisted SOC

AI-powered security alert triage, enrichment, and investigation workflow.

## Features

- Alert ingestion
- AI-powered triage
- FastAPI backend
- Streamlit dashboard
- Local LLM support via Ollama

## Architecture

Alert JSON
    ↓
FastAPI
    ↓
LLM (Ollama)
    ↓
Analysis
    ↓
Dashboard

## Quick Start

### Clone Repository

git clone https://github.com/<username>/ai-assisted-soc.git

### Create Virtual Environment

python -m venv .venv

### Activate Environment

Windows:
.venv\Scripts\activate

Linux/macOS:
source .venv/bin/activate

### Install Dependencies

pip install -r requirements.txt

### Install Ollama

https://ollama.com/download

### Download Model

ollama pull llama3.1:8b

### Start Ollama

ollama serve

### Start API

uvicorn api.main:app --reload

### Start Dashboard

streamlit run dashboard/app.py

### Open

API:
http://localhost:8000/docs

Dashboard:
http://localhost:8501

## Documentation

See:

- docs/setup.md
- docs/architecture.md
- docs/roadmap.md