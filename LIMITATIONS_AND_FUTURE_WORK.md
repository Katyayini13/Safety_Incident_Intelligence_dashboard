# Limitations and future work

- The live dashboard continues to use six original bundled examples. Category labels are imbalanced with one ESG Compliance record; they cannot establish generalization.
- The 180-row development set is generated and clearly labeled synthetic. It exists for repeatable feature/model selection only, is not company data, and never enters runtime training, retrieval, analytics, or frontend incident history.
- Synthetic cross-validation and holdout metrics are not real-world performance estimates. They are likely optimistic because the narratives follow controlled templates.
- The selected LinearSVC is fit on the six original records for runtime fallback inference. A transparent keyword prior runs first and can override the classifier. The reported candidate metrics do not validate this entire combined behavior.
- Severity is an explicit independent rules screen; simple text matching can miss context, ambiguity, negation forms outside the configured scope, and site-specific consequence.
- Retrieval is lexical TF-IDF cosine similarity against the six original incidents. The 0.12 threshold suppresses weak overlap but is not a relevance guarantee. Similarity is not confidence.
- No calibrated prediction confidence exists. Uploaded CSVs are validated only; they are not persisted or used for training.
- Recommendations require qualified HSE review. The application is not emergency guidance, a risk assessment, or a regulatory determination.

Future work requires a larger, representative, independently labeled corpus and site/time-aware evaluation; review of rules by qualified HSE practitioners; and separate monitoring and access controls before operational use.
