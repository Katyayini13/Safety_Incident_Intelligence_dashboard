# Model selection and evaluation

## Data boundaries

The original dashboard dataset remains `data/safety_esg_incidents.csv` (six records). It alone powers live analytics, classifier fitting, and retrieval. Its category counts are Safety 3, Environment 2, ESG Compliance 1; it cannot support reliable independent validation.

`data/synthetic_development_incidents.csv` is a separate deterministic development set with 180 unique narratives: 60 per category and 20 per category/severity pair. Every row has a unique `scenario_group`, so no synthetic example is duplicated or shared across splits. The records are illustrative, synthetic, and not Greenko/company data. They are excluded from live analytics, model fitting, and retrieval. See `data/SYNTHETIC_DATA_NOTICE.md`.

## Reproducible model comparison

From the project root:

```powershell
python -m backend.generate_synthetic_data
python -m backend.evaluate_synthetic
```

With scikit-learn 1.7.2 and seed 42, evaluation uses a stratified grouped 80/20 holdout by `scenario_group` (144 train, 36 test), followed by 4-fold stratified group CV within the training partition for candidate selection. The train/test groups and inner CV groups are disjoint. Category distribution was 49/48/47 in train and 11/12/13 in test (Environment/ESG Compliance/Safety).

The candidate grid compares LinearSVC with balanced Logistic Regression, unigram/bigram word TF-IDF, `min_df` 1/2, sublinear TF on/off, and `C` 0.5/1/2. All share lowercase, Unicode accent normalization, L2 normalization, and the same token pattern. Candidates are selected on mean training-only CV macro-F1, with fold standard deviation and stable candidate order as tie-breaks. The holdout is not used to select hyperparameters.

**LinearSVC was selected:** word unigrams+bigrams, `min_df=1`, `sublinear_tf=False`, `C=2.0`, `class_weight='balanced'`. It scored CV macro-F1 0.9721 (SD 0.0198), compared with best Logistic Regression at 0.9368 (SD 0.0236). On the held-out synthetic rows, LinearSVC scored macro precision 1.0000, recall 1.0000 and F1 1.0000; Logistic Regression scored 0.9556, 0.9394 and 0.9429 respectively. The complete comparison is in `data/synthetic_evaluation.json`.

Selected LinearSVC confusion matrix (actual rows, predicted columns; Environment, ESG Compliance, Safety):

```text
[[11, 0, 0],
 [ 0,12, 0],
 [ 0, 0,13]]
```

These high scores apply only to generated examples with controlled templates and vocabulary. They are likely optimistic and do not establish production accuracy. The selected estimator settings are refit at runtime only on the six original rows, and transparent keyword rules still take precedence; the synthetic classifier metric does not evaluate this full combined pipeline. No prediction confidence is calibrated.

## Severity rules diagnostic

Severity is independent and rule-based, not learned. High-consequence signals (fatal/life-threatening harm, fire, electrical hazard/shock/exposed energized equipment, major uncontrolled releases, immediate danger) take precedence; injury, routine leaks/spills, near misses/unsafe conditions, and compliance breaches are medium; observations/minor documentation/PPE signals are low, with low as the default. Short explicit negations such as “no injury reported” do not count as positive triggers. Matched terms are returned in `prediction.severity_indicators`; the existing `risk_indicators` field remains.

On the same synthetic holdout, severity rules produced macro precision 0.8439, recall 0.8317 and F1 0.8250. Confusion matrix order: High, Low, Medium.

```text
[[8, 0, 4],
 [0,13, 1],
 [1, 0, 9]]
```

This is only a synthetic rules diagnostic, not a site risk assessment, emergency triage, or production estimate.

## Retrieval

Retrieval searches the original six narratives only, using word/bigram TF-IDF cosine similarity. It returns up to three records at or above 0.12. This lexical filter does not guarantee relevance and is not prediction confidence or probability. Category confidence remains unavailable and uncalibrated.

## Limits

Even leakage-safe synthetic evaluation is not independent real-incident validation. Controlled generated templates can inflate scores. The six-row original dataset cannot support a real stratified holdout. Collect a larger, representative, independently labeled corpus and validate by site/time before making generalization claims. HSE review remains mandatory; the dashboard is not emergency response or a regulatory determination.
