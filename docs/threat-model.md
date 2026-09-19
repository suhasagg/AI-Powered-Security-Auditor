# Threat model

## Assets
Source code, security findings, logs, scan authorization, repository tokens, model prompts, compliance evidence, tenant metadata and audit records.

## Major threats

### Unauthorized scanning
Controls: explicit authorization artifact, target allowlist, canonicalization, isolated scanner workers, restricted profiles, immutable audit.

### SSRF / network pivot
Controls: scheme restrictions, host/IP policy, DNS rebinding defenses, redirect validation, metadata/link-local denial, egress firewall.

### Prompt injection from code/log/HTML
Controls: all evidence marked untrusted, no privileged model tools, typed adapters, no secrets in prompts, bounded context.

### Cross-tenant leakage
Controls: tenant-aware authorization at every service, partitioned retrieval/evidence, scoped encryption, automated isolation tests.

### Secret leakage
Controls: secret detection/redaction before model calls, approved providers, short-lived credentials, safe telemetry.

### Scanner compromise
Controls: ephemeral sandboxed workers, non-root, read-only filesystem where possible, seccomp/AppArmor, network segmentation, short-lived job credentials, image signing.

### Supply-chain compromise
Controls: locked dependencies, SBOM, SCA, provenance attestations, signed containers, controlled rule updates.

### Compliance hallucination
Controls: deterministic evidence state; model may summarize but cannot change PASS/GAP.

### Audit loss/tampering
Controls: durable append-oriented sink, integrity controls, restricted writers, monitored pipeline, tested recovery.
