"""Local incident screening services. Runtime training uses original records only."""
from pathlib import Path
import json
import re

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import make_pipeline
from sklearn.svm import LinearSVC

ROOT = Path(__file__).resolve().parents[1]
CSV = ROOT / "data" / "safety_esg_incidents.csv"
SYNTHETIC_EVALUATION = ROOT / "data" / "synthetic_evaluation.json"


def clean(text):
    """Normalize whitespace and casing while retaining meaningful punctuation/words."""
    return re.sub(r"\s+", " ", str(text or "").strip().lower())


DATA = pd.read_csv(CSV).fillna("")
DATA["narrative"] = DATA.narrative.astype(str).map(lambda value: clean(value))
DATA = DATA.drop_duplicates("narrative").reset_index(drop=True)
CATS = ["safety", "environment", "esg_compliance"]
SEVS = ["low", "medium", "high"]


_NEGATION = re.compile(r"\b(?:no|not|never|without|absence of|free of)\b(?:\W+\w+){0,3}\W*$", re.I)


def _term_matches(text, term):
    """Return True when a term occurs outside a short, explicit negation scope."""
    for match in re.finditer(r"(?<!\w)" + re.escape(term) + r"(?!\w)", text, flags=re.I):
        prefix = text[max(0, match.start() - 42):match.start()]
        if not _NEGATION.search(prefix):
            return True
    return False


RISK_TERMS = {
    "injury": ("injury", "injured", "hurt", "wound", "fracture"),
    "equipment damage": ("damage", "damaged", "fractured", "broken"),
    "chemical or oil release": ("chemical spill", "chemical release", "oil spill", "oil leak", "oil seepage", "chemical leak", "hydraulic fluid leak", "chemical release", "spill", "spilled", "leak", "leaking", "seepage", "release"),
    "electrical hazard": ("electrical", "electric shock", "live wire", "exposed wire", "arc flash", "electrocution"),
    "fire hazard": ("fire", "smoke", "flame", "burning"),
    "unsafe conditions": ("unsafe", "near miss", "slip", "trip", "ppe non-compliance", "vehicle movement", "hazard", "unprotected", "unguarded"),
    "environmental impact": ("water contamination", "water leak", "waste", "emission", "pollution", "environmental impact", "spill", "seepage", "chemical release"),
}


def indicators(text):
    normalized = clean(text)
    return [name for name, terms in RISK_TERMS.items() if any(_term_matches(normalized, term) for term in terms)]


CATEGORY_TERMS = {
    "safety": ("injury", "injured", "slip", "ppe", "near miss", "vehicle", "hazard", "worker", "fire", "electrical", "unsafe", "fall", "collision"),
    "environment": ("oil", "spill", "leak", "leakage", "leaking", "fluid", "hydraulic", "water", "waste", "chemical", "emission", "pollution", "seepage", "effluent"),
    "esg_compliance": ("compliance", "segregation", "deviation", "audit", "regulatory", "permit", "reporting", "disclosure", "governance"),
}

# Severity is an independent, transparent screening ruleset, not a learned model.
SEVERITY_RULES = {
    "high": {
        "fatality or life-threatening harm": ("fatal", "fatality", "death", "life threatening", "life-threatening", "critical injury", "serious injury", "hospitalized", "hospitalised"),
        "fire or active combustion": ("fire", "flames", "flame", "burning", "explosion"),
        "electrical shock or exposed energized equipment": ("electric shock", "electrical shock", "electrocution", "arc flash", "live wire", "exposed energized", "exposed energised"),
        "electrical hazard": ("electrical hazard", "electrical fault", "energized equipment", "energised equipment", "exposed conductor", "short circuit", "high voltage"),
        "major or uncontrolled hazardous release": ("major spill", "uncontrolled spill", "large chemical release", "toxic release", "uncontained chemical", "large oil spill"),
        "immediate high-risk exposure": ("immediate danger", "imminent danger", "high risk exposure", "high-risk exposure"),
    },
    "medium": {
        "reported injury": ("injury", "injured", "hurt", "wound", "fracture"),
        "contained or unspecified leak or spill": ("spill", "spilled", "leak", "leaking", "seepage", "release"),
        "near miss or unsafe condition": ("near miss", "unsafe", "unprotected", "unguarded", "vehicle movement", "slip", "trip"),
        "compliance breach": ("non-compliance", "noncompliance", "non compliance", "regulatory breach", "permit breach"),
    },
    "low": {
        "observation or minor process deviation": ("observation", "deviation", "housekeeping", "minor paperwork", "documentation gap", "labeling issue", "labelling issue"),
        "PPE or routine control observation": ("ppe", "personal protective equipment", "routine inspection"),
    },
}


def severity_screen(text):
    normalized = clean(text)
    triggered = [
        f"{label}: {term}"
        for severity, rules in SEVERITY_RULES.items()
        for label, terms in rules.items()
        for term in terms
        if _term_matches(normalized, term)
    ]
    # High-consequence signals take precedence over lower-level terms in the same report.
    if any(item.startswith(tuple(f"{label}:" for label in SEVERITY_RULES["high"])) for item in triggered):
        result = "high"
    elif any(item.startswith(tuple(f"{label}:" for label in SEVERITY_RULES["medium"])) for item in triggered):
        result = "medium"
    else:
        result = "low"
    return result, triggered


def _category_model():
    # Configuration selected using the reproducible synthetic development evaluation.
    # Refit only on the six preserved original records at runtime; synthetic rows never
    # enter production inference or historical retrieval.
    vectorizer = TfidfVectorizer(
        strip_accents="unicode", lowercase=True, ngram_range=(1, 2),
        min_df=1, max_df=1.0, sublinear_tf=False, norm="l2",
        token_pattern=r"(?u)\b\w\w+\b",
    )
    model = make_pipeline(vectorizer, LinearSVC(class_weight="balanced", C=2.0, random_state=42))
    return model.fit(DATA.narrative, DATA.target_category.str.lower())


_MODEL = _category_model()


def predict(text):
    normalized = clean(text)
    if not normalized:
        raise ValueError("Incident narrative must not be empty.")
    scores = {category: sum(_term_matches(normalized, term) for term in terms) for category, terms in CATEGORY_TERMS.items()}
    category = max(scores, key=scores.get) if max(scores.values()) else str(_MODEL.predict([normalized])[0])
    severity, severity_indicators = severity_screen(normalized)
    return {
        "category": category,
        "severity": severity,
        "risk_indicators": indicators(normalized),
        "severity_indicators": severity_indicators,
        "prediction_confidence": None,
        "confidence_note": "Not calibrated; similarity scores are not prediction confidence. Original labeled sample has six records.",
    }


def retrieve(text, k=3, threshold=0.12):
    """Return only relevant original records; the threshold is a lexical screen, not confidence."""
    query = clean(text)
    if not query or not len(DATA):
        return []
    vectorizer = TfidfVectorizer(
        strip_accents="unicode", ngram_range=(1, 2), sublinear_tf=True,
        token_pattern=r"(?u)\b\w\w+\b",
    )
    historical = vectorizer.fit_transform(DATA.narrative)
    query_vector = vectorizer.transform([query])
    scores = (historical @ query_vector.T).toarray().ravel()
    ordered = sorted(range(len(scores)), key=lambda index: (-scores[index], index))
    return [
        {
            "incident_id": str(DATA.iloc[index].incident_id),
            "narrative": str(DATA.iloc[index].narrative),
            "category": str(DATA.iloc[index].target_category),
            "severity": str(DATA.iloc[index].target_severity),
            "similarity": round(float(scores[index]), 3),
        }
        for index in ordered if scores[index] >= threshold
    ][:max(0, min(int(k), 3))]


def analyze(text):
    prediction = predict(text)
    recommendations = []
    if "unsafe conditions" in prediction["risk_indicators"]:
        recommendations.append("Correct the unsafe condition and verify controls before restarting work.")
    if "chemical or oil release" in prediction["risk_indicators"] or "environmental impact" in prediction["risk_indicators"]:
        recommendations.append("Verify containment, protect drains, and document cleanup and disposal.")
    if "electrical hazard" in prediction["risk_indicators"]:
        recommendations.append("Isolate under approved lockout/tagout controls and obtain competent inspection.")
    if prediction["category"] == "environment":
        recommendations.append("Inspect the source and document impact and corrective action.")
    if prediction["category"] == "esg_compliance":
        recommendations.append("Assign a corrective action owner and verify evidence at next audit.")
    if not recommendations:
        recommendations = ["Have a site supervisor validate the report and assign corrective actions."]
    if prediction["severity"] == "high":
        recommendations.insert(0, "Escalate promptly to the site HSE lead; automated screening is not a risk assessment.")
    trimmed = text.strip()
    return {
        "input": text,
        "summary": trimmed[:177] + ("…" if len(trimmed) > 180 else ""),
        "prediction": prediction,
        "similar_incidents": retrieve(text),
        "recommendations": recommendations,
        "explanation_source": "local",
        "explanation": "Category uses a transparent keyword prior and a TF-IDF/LinearSVC fallback trained on the six original records. Severity uses independent rules. Similarity is lexical overlap, not confidence; recommendations need site review.",
        "limitations": ["Only six original labeled records; predictions are unstable.", "Not for emergency response or regulatory determination."],
    }


def analytics():
    categories = DATA.target_category.str.lower().value_counts().reindex(CATS, fill_value=0)
    severities = DATA.target_severity.str.lower().value_counts().reindex(SEVS, fill_value=0)
    return {
        "total": len(DATA),
        "categories": [{"name": key, "count": int(value)} for key, value in categories.items()],
        "severities": [{"name": key, "count": int(value)} for key, value in severities.items()],
        "high_severity": int(severities["high"]),
        "patterns": [{"name": key, "count": int(value)} for key, value in categories.items()],
        "risk_indicators": [{"name": key, "count": sum(key in indicators(text) for text in DATA.narrative)} for key in RISK_TERMS],
    }


def evaluation():
    """Expose synthetic-only metrics without conflating them with company data."""
    try:
        report = json.loads(SYNTHETIC_EVALUATION.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        report = None
    original_counts = DATA.target_category.str.lower().value_counts().to_dict()
    original_severity = DATA.target_severity.str.lower().value_counts().to_dict()
    legacy_metrics = {
        key: {
            "method": "not meaningfully estimable",
            "accuracy": None,
            "precision_macro": None,
            "recall_macro": None,
            "f1_macro": None,
            "confusion_matrix": None,
            "class_counts": {str(label): int(count) for label, count in counts.items()},
            "note": "Six original records and a singleton class do not support reliable validation scores.",
        }
        for key, counts in (("target_category", original_counts), ("target_severity", original_severity))
    }
    return {
        # Retain the original evaluation response keys for existing API consumers.
        **legacy_metrics,
        "original_data": {
            "source": "bundled original dataset; not independently representative",
            "records": int(len(DATA)),
            "category_class_counts": {str(k): int(v) for k, v in original_counts.items()},
            "severity_class_counts": {str(k): int(v) for k, v in original_severity.items()},
            "metrics": None,
            "note": "Six original records are insufficient for reliable or production accuracy claims.",
        },
        "synthetic_development": report,
    }
