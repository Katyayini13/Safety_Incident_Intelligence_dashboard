"""Reproducible model selection and holdout report on synthetic records only."""
from collections import Counter
import json
from pathlib import Path

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix, precision_recall_fscore_support
from sklearn.model_selection import StratifiedGroupKFold, cross_val_score
from sklearn.pipeline import make_pipeline
from sklearn.svm import LinearSVC

from backend.generate_synthetic_data import OUT as DATA_PATH
from backend.services import severity_screen

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "synthetic_evaluation.json"
SEED = 42
LABELS = ["environment", "esg_compliance", "safety"]
SEVERITIES = ["high", "low", "medium"]


def vectorizer(ngram_range, min_df, sublinear_tf):
    return TfidfVectorizer(
        strip_accents="unicode", lowercase=True, ngram_range=ngram_range,
        min_df=min_df, max_df=1.0, sublinear_tf=sublinear_tf, norm="l2",
        token_pattern=r"(?u)\b\w\w+\b",
    )


def candidates():
    for ngrams in ((1, 1), (1, 2)):
        for min_df in (1, 2):
            for sublinear in (False, True):
                for c_value in (0.5, 1.0, 2.0):
                    config = {"ngram_range": list(ngrams), "min_df": min_df, "sublinear_tf": sublinear, "C": c_value, "class_weight": "balanced"}
                    yield ("LinearSVC", config, make_pipeline(vectorizer(ngrams, min_df, sublinear), LinearSVC(class_weight="balanced", C=c_value, random_state=SEED)))
                    config_log = {**config, "solver": "lbfgs"}
                    yield ("LogisticRegression", config_log, make_pipeline(vectorizer(ngrams, min_df, sublinear), LogisticRegression(class_weight="balanced", C=c_value, solver="lbfgs", max_iter=2000, random_state=SEED)))


def score_dict(y_true, y_pred, labels):
    precision, recall, f1, _ = precision_recall_fscore_support(y_true, y_pred, labels=labels, average="macro", zero_division=0)
    return {"precision_macro": round(float(precision), 4), "recall_macro": round(float(recall), 4), "f1_macro": round(float(f1), 4), "confusion_matrix_labels": labels, "confusion_matrix": confusion_matrix(y_true, y_pred, labels=labels).tolist()}


def evaluate():
    frame = pd.read_csv(DATA_PATH)
    texts = frame.narrative.astype(str).tolist()
    labels = frame.target_category.astype(str).tolist()
    groups = frame.scenario_group.astype(str).tolist()
    outer_folds = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=SEED)
    train_indices, test_indices = next(outer_folds.split(texts, labels, groups))
    x_train = [texts[index] for index in train_indices]
    y_train = [labels[index] for index in train_indices]
    x_test = [texts[index] for index in test_indices]
    y_test = [labels[index] for index in test_indices]
    train_groups = [groups[index] for index in train_indices]
    folds = list(StratifiedGroupKFold(n_splits=4, shuffle=True, random_state=SEED).split(x_train, y_train, train_groups))
    inner_group_isolation = all(
        not {train_groups[index] for index in fold_train}.intersection(train_groups[index] for index in fold_validation)
        for fold_train, fold_validation in folds
    )
    comparisons = []
    for name, config, estimator in candidates():
        fold_scores = cross_val_score(estimator, x_train, y_train, cv=folds, scoring="f1_macro", n_jobs=1)
        comparisons.append({"model": name, "config": config, "cv_f1_macro_mean": round(float(fold_scores.mean()), 4), "cv_f1_macro_std": round(float(fold_scores.std()), 4)})
    # Stable tie-break: highest mean F1, then lower variance, then simpler/earlier candidate.
    best = max(range(len(comparisons)), key=lambda i: (comparisons[i]["cv_f1_macro_mean"], -comparisons[i]["cv_f1_macro_std"], -i))
    chosen = comparisons[best]
    estimator = next(model for name, config, model in candidates() if name == chosen["model"] and config == chosen["config"])
    estimator.fit(x_train, y_train)
    predicted = estimator.predict(x_test)
    family_comparison = []
    for family in ("LinearSVC", "LogisticRegression"):
        family_best = max((row for row in comparisons if row["model"] == family), key=lambda row: (row["cv_f1_macro_mean"], -row["cv_f1_macro_std"]))
        family_estimator = next(model for name, config, model in candidates() if name == family_best["model"] and config == family_best["config"])
        family_estimator.fit(x_train, y_train)
        family_best = {**family_best, "heldout_metrics": score_dict(y_test, family_estimator.predict(x_test), LABELS)}
        family_comparison.append(family_best)

    # The separate rule screen is evaluated on the exact same held-out synthetic rows.
    severity_truth = frame.iloc[test_indices].target_severity.astype(str).tolist()
    severity_predicted = [severity_screen(texts[index])[0] for index in test_indices]
    severity_score = score_dict(severity_truth, severity_predicted, SEVERITIES)

    report = {
        "dataset": "synthetic_development_incidents.csv",
        "data_disclosure": "All records are synthetic development examples; none are Greenko/company incidents. These scores do not estimate production performance.",
        "records": int(len(frame)),
        "unique_narratives": int(frame.narrative.nunique()),
        "scenario_groups": int(frame.scenario_group.nunique()),
        "category_class_counts": {str(k): int(v) for k, v in sorted(frame.target_category.value_counts().items())},
        "severity_class_counts": {str(k): int(v) for k, v in sorted(frame.target_severity.value_counts().items())},
        "category_severity_counts": {f"{category}/{severity}": int(count) for (category, severity), count in sorted(frame.groupby(["target_category", "target_severity"]).size().items())},
        "random_seed": SEED,
        "split": {"strategy": "stratified group 80/20 holdout by scenario_group; model candidates selected by 4-fold stratified group CV within training partition", "group_isolation": len(set(train_groups).intersection(groups[index] for index in test_indices)) == 0, "inner_cv_group_isolation": inner_group_isolation, "train_groups": len(set(train_groups)), "test_groups": len({groups[index] for index in test_indices}), "train_records": len(train_indices), "test_records": len(test_indices), "train_class_counts": dict(sorted(Counter(y_train).items())), "test_class_counts": dict(sorted(Counter(y_test).items()))},
        "category_model_selection": {"selection_metric": "mean macro F1 across 4-fold CV on training partition", "tie_break": "lower fold-score standard deviation, then stable candidate order", "selected_model": chosen["model"], "selected_config": chosen["config"], "cv_f1_macro_mean": chosen["cv_f1_macro_mean"], "cv_f1_macro_std": chosen["cv_f1_macro_std"], "best_by_model_family": family_comparison, "candidates": comparisons, "heldout_metrics": score_dict(y_test, predicted, LABELS)},
        "severity_rules": {"method": "independent deterministic severity_screen rules; not a trained classifier", "heldout_metrics": severity_score, "test_class_counts": dict(sorted(Counter(severity_truth).items()))},
        "limitations": ["Generated synthetic narratives have patterned vocabulary; results measure this development set only.", "Do not describe these metrics as production accuracy or independent real-incident validation.", "The live category model remains trained on the six original bundled rows; synthetic records are excluded from runtime training and retrieval.", "The rule-based severity test is a synthetic-set diagnostic, not a risk assessment."],
    }
    OUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


if __name__ == "__main__":
    result = evaluate()
    selected = result["category_model_selection"]
    print(f"Synthetic records: {result['records']} ({result['split']['train_records']} train / {result['split']['test_records']} holdout)")
    print(f"Selected: {selected['selected_model']} {selected['selected_config']} CV macro-F1={selected['cv_f1_macro_mean']} ± {selected['cv_f1_macro_std']}")
    print(f"Category heldout: {selected['heldout_metrics']}")
    print(f"Severity rules heldout: {result['severity_rules']['heldout_metrics']}")
    print(f"Report: {OUT}")
