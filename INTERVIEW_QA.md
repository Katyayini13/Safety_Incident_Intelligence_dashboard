# Interview Q&A
1. **Why TF-IDF?** Sparse, inspectable word importance.
2. **What is IDF?** Downweights common terms.
3. **Why unigrams in the selected fallback?** Unigram and bigram TF-IDF candidates were compared; bigrams were selected by training-only grouped CV macro-F1 on synthetic examples.
4. **Cosine similarity?** Normalized vector dot product.
5. **Similarity confidence?** No, it ranks text overlap.
6. **Why LinearSVC?** It tied the best balanced Logistic Regression in mean CV macro-F1 on the synthetic development data; lower fold variance/stable order selected SVC. This is not proof of real-world superiority.
7. **Why class weights?** Mitigate imbalance.
8. **What is the validation split?** A seeded stratified group 80/20 synthetic holdout with no scenario shared across partitions; candidate selection uses 4-fold stratified group CV on training rows only.
9. **Why no real-data scores?** Six original records with a singleton class cannot support a reliable holdout estimate.
10. **What is macro F1?** Equal-weight mean across class F1.
11. **Confusion matrix?** True versus predicted label counts.
12. **Why no RMSE?** Outputs are categorical.
13. **How handle missing data?** Fill nulls and skip empty narratives.
14. **Duplicate handling?** Drop duplicate narrative strings.
15. **Extractive summary?** Reuses source words.
16. **Is this RAG?** No; retrieval is displayed, not grounded generation.
17. **Prevent hallucinations?** Constrain generation to evidence and review.
18. **API key practice?** Use environment variables.
19. **FastAPI benefit?** Typed validation and OpenAPI docs.
20. **Pydantic role?** Validates request schemas.
21. **Why services module?** Separates reusable logic from routes.
22. **React state?** State changes rerender UI.
23. **Why Vite?** Fast dev server and production bundling.
24. **Recharts?** React chart components.
25. **Upload behavior?** Validate schema only, no persistence.
26. **Health endpoint?** Readiness signal.
27. **What is 422?** Invalid request payload.
28. **Major limitation?** Only six original records power runtime training and retrieval; synthetic evaluation is not real-data validation.
29. **Production next step?** More reviewed data and temporal validation.
30. **Severity model?** An independent deterministic rules screen; triggered indicators are returned and negative injury mentions are excluded within configured negation scope.
31. **Can recommendation be fact?** No, it is a proposal for human review.
