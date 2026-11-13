# Greenko ESG / Safety Incident Intelligence Dashboard

A React/Vite dashboard and FastAPI backend using the original six-row incident CSV for live analytics, category fallback training, and historical retrieval. It provides dataset-backed analytics, incident filtering, local incident screening, TF-IDF/cosine retrieval, summaries, recommendations, CSV validation and evaluation disclosure. It does not call an LLM. Severity uses transparent keyword rules; category classification uses TF-IDF/LinearSVC with a keyword prior. A separate 180-row synthetic development set is used only for reproducible offline model-selection diagnostics; it is never displayed as company incident history or used in runtime training/retrieval.

## Run in VS Code (Windows PowerShell)

Open the project folder `work/05_esg_safety_incident_intelligence_dashboard` in VS Code. Open two terminals at that folder.

**Terminal 1 — backend:**

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m uvicorn backend.app:app --reload --host 127.0.0.1 --port 8000
```

**Terminal 2 — frontend:**

```powershell
cd frontend
npm install
npm run dev
```

Open the Vite URL shown in Terminal 2 (normally `http://localhost:5173`). The Vite development proxy forwards `/api` and `/health` to the local backend. Swagger is at `http://127.0.0.1:8000/docs`. Use Python 3.10 or newer and Node.js compatible with Vite 8.

## Verify

From the project root: `python -m pytest backend/test_app.py -q`. From `frontend`: `npm run build`.

## API and data behavior

- `GET /health`, `GET /api/demo`, `GET /api/incidents`, `GET /api/analytics`
- `POST /api/analyze` with JSON `{"text":"..."}`
- `POST /api/incidents/upload` with a CSV containing a `narrative` column

The supplied CSV is preserved. Uploads are parsed and validated but not persisted or used to update models. Analyzer explanations are local and work without `OPENAI_API_KEY`; that key is not used by this code. New text is analyzed on demand and retrieved against the six original narratives. Similarity retrieval returns up to three matches at/above a 0.12 textual cosine threshold. Category prediction confidence is not calibrated. The response's additive `severity_indicators` field identifies matched severity rules.

## Synthetic development evaluation

`data/synthetic_development_incidents.csv` is explicitly synthetic (180 unique narratives; balanced across three categories and severities). Rebuild it and reproduce candidate comparison with:

```powershell
python -m backend.generate_synthetic_data
python -m backend.evaluate_synthetic
```

Evaluation reports a stratified, scenario-group-isolated holdout and training-only stratified group cross-validation for selection, candidate comparison, class distributions, macro precision/recall/F1 and confusion matrices. Metrics describe only generated examples; they are not production accuracy or independent validation on real incidents. See `MODEL_EVALUATION.md` and `data/SYNTHETIC_DATA_NOTICE.md`.

## Deploy

The project is prepared for separate Railway backend and frontend services. Follow [RAILWAY_DEPLOYMENT.md](RAILWAY_DEPLOYMENT.md) for exact root directories, service config paths, commands, domains, and environment variables. Set frontend build variable `VITE_API_URL` to the FastAPI base URL and backend `CORS_ORIGINS` to the frontend's exact HTTPS origin. The Vite proxy is development-only; the production client refuses to fall back to a relative API URL when `VITE_API_URL` is missing. No deployment has been performed. The original dataset is too small for real-data validation; synthetic diagnostics cannot support production accuracy claims. See `MODEL_EVALUATION.md`, `LIMITATIONS_AND_FUTURE_WORK.md`, and `AUDIT_RESULTS.md`.
