import io
import os

import pandas as pd
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from backend import services


def configured_cors_origins():
    """Read explicit origins from env; local Vite origins are dev-only defaults."""
    raw = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173")
    origins = [origin.strip().rstrip("/") for origin in raw.split(",") if origin.strip()]
    if "*" in origins:
        raise ValueError("CORS_ORIGINS must list trusted origins; wildcard origins are not allowed.")
    return origins


app = FastAPI(title="ESG / Safety Incident Intelligence Dashboard", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=configured_cors_origins(),
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


class Query(BaseModel):
    text: str = Field(min_length=1, max_length=10000)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/api/demo")
def demo():
    return {"case_study": "ESG / Safety Incident Intelligence Dashboard", "status": "ready", "records": len(services.DATA)}


@app.get("/api/incidents")
def incidents(q: str = "", category: str = "", severity: str = ""):
    data = services.DATA
    if q:
        data = data[data.narrative.str.contains(q, case=False, regex=False)]
    if category:
        data = data[data.target_category.str.lower() == category.lower()]
    if severity:
        data = data[data.target_severity.str.lower() == severity.lower()]
    return data.to_dict(orient="records")


@app.get("/api/analytics")
def analytics():
    return {"analytics": services.analytics(), "evaluation": services.evaluation()}


@app.post("/api/analyze")
def analyze(query: Query):
    try:
        return services.analyze(query.text)
    except ValueError as error:
        raise HTTPException(422, str(error)) from error


@app.post("/api/incidents/upload")
async def upload(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(400, "Upload a .csv file.")
    try:
        data = pd.read_csv(io.BytesIO(await file.read()))
    except Exception as error:
        raise HTTPException(400, f"Could not parse CSV: {error}") from error
    if "narrative" not in data.columns:
        raise HTTPException(422, "CSV must include a 'narrative' column.")
    return {
        "valid": True,
        "rows": len(data),
        "usable_narratives": int(data.narrative.fillna("").astype(str).str.strip().ne("").sum()),
        "columns": data.columns.tolist(),
        "message": "CSV validated; uploaded data is not persisted.",
    }
