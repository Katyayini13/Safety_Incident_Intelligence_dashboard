# End-to-end and NLP audit results

Updated 2026-11-13. The original six-row CSV and API contracts are preserved.

## Checks executed for the NLP update

- `python -m backend.generate_synthetic_data`: passed; generated 180 unique synthetic narratives, balanced at 60/category, 60/severity, and 20/category-severity pair.
- `python -m backend.evaluate_synthetic`: passed; reproducible stratified group model comparison and severity diagnostic written to `data/synthetic_evaluation.json`.
- `python -m pytest -q backend/test_app.py`: **26 passed**. The restricted local test run hung at its first in-process TestClient request; rerunning with approved local-network permissions completed successfully.
- `npm.cmd run build`: **passed**. Vite emitted an advisory that the minified JavaScript chunk exceeds 500 kB; there were no build errors.
- Regression coverage includes existing route/filter/upload checks, unseen narratives, deterministic ambiguous text, negated injury/fire, electrical severity trigger evidence, retrieval relevance threshold/top-three cap, preserved response fields, and synthetic-data disclosure.

## Evaluation results and boundaries

The selected category candidate was balanced LinearSVC with unigram/bigram TF-IDF, `min_df=1`, `sublinear_tf=False`, and `C=2.0`. Mean four-fold training-only stratified group CV macro-F1 was 0.9721 (SD 0.0198). The 36-row scenario-isolated synthetic holdout gave macro precision 1.0000, recall 1.0000, and F1 1.0000; confusion matrix order Environment, ESG Compliance, Safety: `[[11,0,0],[0,12,0],[0,0,13]]`.

Best balanced Logistic Regression had CV macro-F1 0.9368 (SD 0.0236) and holdout macro-F1 0.9429. This is synthetic-only evidence and likely optimistic; no production claim is made. Rule-based severity on the same synthetic holdout gave macro precision 0.8439, recall 0.8317, F1 0.8250; confusion matrix order High, Low, Medium: `[[8,0,4],[0,13,1],[1,0,9]]`.

All of the above metrics are synthetic development diagnostics only. The generated records are never shown in dashboard history, nor used in live training, analytics, or retrieval. The runtime fallback refits on the original six records; no real-data validation or production accuracy claim is available. Severity screening remains rules-based. Cosine similarity is lexical overlap and not prediction confidence.

## Preserved API and behavior

The existing `GET /health`, `/api/demo`, `/api/incidents`, `/api/analytics`, `POST /api/analyze`, and `POST /api/incidents/upload` routes remain. Existing response fields remain; `prediction.severity_indicators` and synthetic/original evaluation disclosure are additive. CSV uploads remain validation-only and are not persisted. Analyzer works without an LLM key.

## Remaining limitations

Only six original examples are available for runtime classifier fitting and retrieval. Severity rules can still miss context and unfamiliar negation. Similarity threshold 0.12 filters weak overlap but does not guarantee relevance. Recommendations require qualified site HSE review. Collect independently labeled, representative incidents and evaluate by site/time before operational accuracy claims.

## Railway deployment preparation checks

- Backend launched on `0.0.0.0:8017` using `PORT=8017`, custom `CORS_ORIGINS=https://ui.example.test`, and with `OPENAI_API_KEY` removed from the process environment.
- `GET /health` returned `{"status":"ok"}`. Analytics loaded the six original records and the 180-row synthetic evaluation disclosure.
- `POST /api/analyze` returned a local environment/medium result; `POST /api/incidents/upload` validated the original CSV (six rows/six usable narratives); the allowed-origin CORS preflight returned 200 and echoed the configured origin.
- Frontend built with test build-time `VITE_API_URL=https://greenko-api.example.test`; compiled JS contained that absolute base and did not contain the local Vite proxy host. This example domain was only a wiring test, not a deployed backend URL.
- Frontend production server started on `0.0.0.0:5182`; `/health`, `/`, and an extensionless SPA path returned 200.
- Railway JSON files parse successfully; `.gitignore` excludes `.venv`, `node_modules`, `.env`, and build/cache artifacts. Secret-pattern scan found no likely key/private-key material among files included in the refreshed ZIP.
- No Railway service was created or deployed from this task.
