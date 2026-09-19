# Evaluation

Release the system as a versioned bundle: scanner + rules + normalizer + detector + compliance catalog + model + prompt + retrieval corpus + policy.

Use sanctioned local vulnerable applications/labs for DAST regression, labeled code fixtures for SAST rules, synthetic/replayed logs for anomaly detection, and known evidence fixtures for compliance.

Metrics include precision/recall, dedup stability, alert volume, time-to-detect, evidence-grounded explanation rate, unsupported-claim rate, prompt-injection resistance and cross-tenant isolation.

Security-expert review and deterministic tests are primary gates. LLM-as-judge is supplemental.
