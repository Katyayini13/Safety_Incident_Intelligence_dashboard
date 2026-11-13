# Architecture

React/Vite frontend → existing FastAPI routes → `backend.services` → preserved `data/safety_esg_incidents.csv`.

The original six records alone power live analytics, training of the category fallback, and historical retrieval. For a new narrative, the existing `POST /api/analyze` contract returns the keyword-prior/TF-IDF+LinearSVC category prediction, separate rule-based severity and indicator evidence, thresholded top-three TF-IDF cosine matches, input-derived summary, local recommendations and limitations. `prediction_confidence` stays null/unavailable.

`data/synthetic_development_incidents.csv` is a separate generated 180-row development corpus. Offline scripts compare category candidates and evaluate severity rules using stratified train/CV/holdout partitions. It is excluded from running dashboard analytics, training, retrieval and incident history. The existing upload route validates a CSV only; it does not persist it or use it to update a model. No LLM or generated RAG response is used.
