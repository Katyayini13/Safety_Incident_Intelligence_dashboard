# Project explanation

FastAPI serves computed analytics, filtering, analysis and CSV validation. React/Vite consumes those API contracts. Live data remains the six original rows. Category screening first uses readable domain keyword counts; if those do not match, TF-IDF with a class-weighted LinearSVC uses the same six original narratives. Candidate parameters were compared offline against a separately labeled synthetic development dataset; synthetic rows are never used by the live service.

Severity is a separate deterministic rules layer, with severity trigger explanations in the API response. Similar historical records are retrieved only from the original six rows using TF-IDF cosine similarity with a 0.12 minimum threshold and at most three results. Similarity is not confidence. The summary reuses input text; recommendations are proposed controls. No LLM is connected, upload validation does not persist data, and HSE review is required.

See `MODEL_EVALUATION.md` for the reproducible synthetic-only metrics and their limitations.
