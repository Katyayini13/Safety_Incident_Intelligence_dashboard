# Synthetic development records

`synthetic_development_incidents.csv` contains 180 generated development examples (60 each for Safety, Environment, and ESG Compliance). Records are labeled Low, Medium, or High severity, with 20 examples per category/severity combination. Each distinct narrative has a unique `scenario_group` and `DEV###` synthetic ID; group-aware splits prevent examples from crossing evaluation partitions. Narratives are illustrative and are not original Greenko/company records.

The original six records remain separately stored in `safety_esg_incidents.csv`. Runtime dashboard analytics, training, and retrieval use only that original CSV. The synthetic file is used only by `python -m backend.evaluate_synthetic` for reproducible development evaluation. Uploading a CSV through the API still only validates it; it does not persist or train on records.

The development narratives are generated deterministically with `python -m backend.generate_synthetic_data`. The generation script and fixed random seed/evaluation procedure are included with the project.
