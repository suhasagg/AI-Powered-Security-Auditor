# ADR-001 — LLMs do not own security authority

## Decision
Models can classify, correlate and explain evidence but cannot expand scan scope, execute arbitrary tools, alter deterministic findings or mark controls compliant.

## Rationale
Security inputs are adversarial by nature. Code, HTML and logs can contain prompt injection. Privileged model autonomy creates unacceptable lateral-movement and audit risk.

## Consequence
More orchestration code is required, but permission boundaries are explicit and independently testable.
