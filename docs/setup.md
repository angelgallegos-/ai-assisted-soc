# Development Setup

## Prerequisites

- Python 3.11+
- Git
- [Ollama](https://ollama.com/download)
- About 5 GB of disk space for the default model

## 1. Clone the repository

```bash
git clone https://github.com/angelgallegos-/ai-assisted-soc.git
cd ai-assisted-soc
```

## 2. Create and activate a virtual environment

```bash
python -m venv .venv
```

Windows (PowerShell):

```powershell
.venv\Scripts\Activate.ps1
```

Linux/macOS:

```bash
source .venv/bin/activate
```

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

## 4. Configure

Copy the example settings and adjust if needed:

```bash
cp .env.example .env
```

On Windows use `copy .env.example .env`. Every setting has a default, so this step is optional. See the configuration table in the [README](../README.md#configuration).

## 5. Download the model

```bash
ollama pull llama3.1:8b
```

To use a different model, pull it and set `OLLAMA_MODEL` in `.env`. The model must support Ollama's structured outputs (JSON schema in `format`).

## 6. Start Ollama

```bash
ollama serve
```

On Windows and macOS the Ollama desktop app usually runs this in the background already.

## 7. Run the API

From the project root:

```bash
uvicorn api.main:app --reload
```

Check it is up at http://localhost:8000/ (returns status, model and prompt version) and explore endpoints at http://localhost:8000/docs.

Try a triage from the command line:

```bash
curl -X POST http://localhost:8000/triage
```

Or send your own alert:

```bash
curl -X POST http://localhost:8000/triage -H "Content-Type: application/json" -d '{"id":"A002","title":"Test","severity":"Low","user":"bob","host":"HR-PC02","description":"Test alert."}'
```

## 8. Run the dashboard

In another terminal:

```bash
streamlit run dashboard/app.py
```

Open http://localhost:8501 and click **Analyze Alert**.

## Run tests

```bash
pytest
```

The LLM is mocked, so tests do not need Ollama running.

# Common Issues

## ModuleNotFoundError

Activate the virtual environment and install dependencies:

```bash
pip install -r requirements.txt
```

## API returns 503 / "Ollama request failed"

Ollama is not reachable or the model is missing. Start it with `ollama serve`, confirm the model is listed by `ollama list`, and check `OLLAMA_HOST` / `OLLAMA_MODEL` in `.env`.

## `ModuleNotFoundError: No module named 'api'` when starting uvicorn

Start uvicorn from the project root so the `api` and `app` packages can be imported.

## Dashboard shows "Triage request failed"

Make sure the API is running and `API_URL` points to it. The first request after starting Ollama can take minutes while the model loads; the dashboard waits up to 300 seconds.

## Result shows "routed to manual review"

The model's output did not match the schema after `TRIAGE_MAX_ATTEMPTS` tries. The `error` field in the raw JSON lists which fields failed. Try a larger model or raise `TRIAGE_MAX_ATTEMPTS`.
