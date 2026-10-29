# Architecture

## Components

### FastAPI

Provides REST endpoints.

### Ollama

Provides local LLM inference.

### Streamlit

Provides analyst dashboard.

## Data Flow

Alert
 ↓
Prompt
 ↓
LLM
 ↓
Analysis
 ↓
Dashboard