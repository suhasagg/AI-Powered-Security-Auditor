# AI-Powered Security Auditor — Principal+ Reference Architecture

> Defensive, authorization-first reference implementation. Scan only systems you own or are explicitly authorized to assess. The included ZAP integration defaults to passive/baseline-style operation and requires an allowlisted target. It is not an exploitation framework.

## Executive summary

This repository implements an agentic application-security assurance platform with four bounded agents:

1. **Vulnerability Scanner** — orchestrates authorized OWASP ZAP-style web assessment and normalizes findings.
2. **Code Security Analyzer** — performs deterministic source-pattern checks mapped to OWASP categories, then optionally uses an LLM to explain evidence and remediation.
3. **Log Analyzer** — detects operational/security anomalies from supplied logs without autonomous containment.
4. **Compliance Checker** — maps collected evidence to versioned controls and reports evidence gaps; it does not claim legal certification.

LangChain/OpenAI is used as a reasoning and explanation layer. Security authority remains deterministic: target authorization, tool permissions, scan profiles, compliance mappings, finding severity, workflow transitions and audit are not delegated to the model.

**Core principle**

`Authorize explicitly → collect evidence safely → normalize deterministically → reason probabilistically → validate → prioritize → human review → audit`

## Architecture

```text
                 Web / CLI / CI / SOC
                         |
                 API Gateway + OIDC
                         |
              Security Auditor API
                         |
        +----------------+----------------+
        |                                 |
 Authorization / Scope Gate          Audit Ledger
        |                                 |
        +----------- Orchestrator --------+
                    |
       +------------+------------+----------------+
       |            |            |                |
 Vulnerability   Code Agent   Log Agent     Compliance Agent
 Scanner Agent      |            |                |
       |          SAST rules   detectors       control catalog
  ZAP Adapter        |            |                |
       +-------------+------------+----------------+
                     |
               Evidence Store
                     |
              Retrieval / RAG
                     |
                LLM Gateway
                     |
             explanation/correlation
```

### Production data plane

```text
Ingress
  |
Tenant auth / RBAC / scan authorization
  |
Regional cell
  +-- API
  +-- workflow workers
  +-- scanner workers (network isolated)
  +-- code analyzers (sandboxed)
  +-- log detector workers
  +-- evidence DB / object store
  +-- tenant vector partition
  +-- queue + DLQ
  +-- audit shard
       |
Global control plane
  +-- policy registry
  +-- rule/signature registry
  +-- model/prompt registry
  +-- compliance catalog registry
```

Scanner workers should be isolated from the control plane, run with minimal network reachability, and receive short-lived scoped jobs.

## Why bounded agents?

A security product should not give an LLM arbitrary shell/network credentials. Each agent is a capability boundary with typed inputs and outputs. The orchestrator chooses a permitted operation; adapters enforce authorization and parameters. This makes workflows reproducible, testable and auditable.

The LLM **cannot**:
- expand scan scope,
- discover arbitrary internet targets,
- change ZAP from baseline/passive to active scanning,
- execute arbitrary shell commands,
- suppress deterministic findings,
- alter compliance control status,
- access secrets,
- perform remediation automatically.

## Repository

```text
app/
  api.py
  config.py
  models.py
  orchestrator.py
  agents/
    vulnerability.py
    code_security.py
    log_analyzer.py
    compliance.py
  scanners/
    zap.py
    code_rules.py
  detection/
    logs.py
  compliance/
    catalog.py
  llm/
    gateway.py
  audit/
    service.py
  security/
    authorization.py
tests/
docs/
deploy/
.github/workflows/
```

## Agent 1 — Vulnerability Scanner

The scanner accepts a target only after an explicit authorization token and host allowlist check. The demo adapter supports a mock mode and a safe external ZAP CLI seam.

Production flow:

```text
scan request
 -> authenticate actor
 -> validate authorization artifact
 -> canonicalize URL
 -> DNS/IP policy
 -> target allowlist
 -> scan profile policy
 -> enqueue
 -> isolated scanner worker
 -> normalize alerts
 -> deduplicate
 -> evidence store
 -> policy/LLM explanation
 -> review
```

### SSRF and scope controls

Target validation must occur after canonicalization and again at execution. Production systems should defend against DNS rebinding, redirects to disallowed networks, IPv6 normalization, credential-bearing URLs, localhost/link-local/private ranges unless explicitly authorized, cloud metadata endpoints, and protocol smuggling.

Never rely on a regex allowlist alone.

### ZAP policy

This repository demonstrates **baseline/passive** integration. Active scanning, fuzzing or attack modules are intentionally excluded. A production security team may implement stronger authorized profiles, but they should remain deterministic, pre-approved and isolated from LLM control.

## Agent 2 — Code Security Analyzer

The reference analyzer demonstrates rules for:
- hard-coded secret-like assignments,
- unsafe dynamic evaluation,
- weak TLS verification,
- suspicious SQL string construction,
- command execution patterns.

These are illustrative and not a replacement for Semgrep, CodeQL, Snyk, SonarQube or language-native analyzers. A production architecture should ingest results from multiple analyzers into a normalized finding schema.

The model receives small evidence snippets after secret redaction and may explain why a finding matters. It does not decide whether deterministic evidence exists.

## OWASP Top 10 mapping

Findings can be tagged to relevant OWASP categories. Keep the taxonomy version explicit. Do not label an application "OWASP compliant" merely because no scanner finding exists. OWASP Top 10 is a risk-awareness taxonomy, not a certification regime.

## Agent 3 — Log Analyzer

The log analyzer separates deterministic detection from LLM interpretation.

Examples:
- repeated authentication failures,
- bursts of 5xx responses,
- access-denied spikes,
- unusual event-rate changes,
- known high-risk event types.

Production detection may combine rules, robust statistics, seasonal baselines, streaming windows and approved ML. Never place raw secrets/tokens or unrestricted production logs into an external model.

A detected anomaly creates an evidence object; it does **not** autonomously block users, rotate credentials or alter infrastructure.

## Agent 4 — Compliance Checker

The compliance agent maps evidence to a versioned control catalog. The included catalog demonstrates generic controls inspired by common security frameworks. It intentionally does not claim certification.

Production catalogs should store:
- framework and version,
- control ID,
- requirement text,
- applicability,
- evidence requirements,
- test procedure,
- owner,
- review frequency,
- exceptions,
- effective dates.

LLMs can summarize evidence gaps but cannot turn missing evidence into a passing control.

## Evidence model

Every finding should be evidence-backed:

```json
{
  "finding_id": "f-...",
  "tenant_id": "t-...",
  "source": "zap",
  "rule_id": "10020",
  "title": "Missing security header",
  "severity": "medium",
  "asset": "https://authorized.example",
  "evidence_ref": "obj://...",
  "taxonomy": ["OWASP-A05"],
  "first_seen": "...",
  "last_seen": "...",
  "tool_version": "...",
  "policy_version": "..."
}
```

Do not use the LLM response itself as evidence.

## Finding lifecycle

```text
NEW -> TRIAGED -> CONFIRMED / FALSE_POSITIVE
                    |
                 ASSIGNED
                    |
                 FIXED
                    |
                VERIFIED
                    |
                 CLOSED
```

Exceptions require owner, justification, expiry and approval. Reopened findings preserve history.

## Deduplication

Use stable fingerprints over normalized asset, rule, location and evidence characteristics. Avoid title-only deduplication. Tool upgrades may alter identifiers, so maintain alias/migration logic.

## Risk prioritization

CVSS can be one input but should not be the entire priority function. Production prioritization can combine severity, exploitability evidence, asset criticality, internet exposure, reachability, data sensitivity, compensating controls and remediation age.

Do not let an LLM invent CVSS vectors. Parse authoritative scanner/advisory metadata or have a trained reviewer assign it.

## RAG

RAG can retrieve:
- secure-coding standards,
- internal security policies,
- approved remediation playbooks,
- framework control descriptions,
- prior accepted exceptions,
- service ownership metadata.

Documents are untrusted content. Retrieval is tenant/ACL scoped before similarity search. Metadata should include document ID/version, authority, effective dates, tenant, ACL, service, framework and content hash.

## Prompt-injection defense

Code, logs, HTML, scanner output and compliance documents are **untrusted data**. They may literally contain text such as "ignore previous instructions." The LLM gateway labels evidence as data, uses typed tools, strips/limits context, and has no privileged execution capability.

This is especially important for repository scanning because malicious prompt text can be committed intentionally.

## Security architecture

Expected production controls:
- OIDC/OAuth2 and MFA for workforce users.
- RBAC/ABAC by tenant, project, repository, environment and scan scope.
- Short-lived workload identity.
- Secret manager/KMS; never model context.
- Egress restrictions for scanner/model workers.
- Sandbox code analysis.
- Read-only repository tokens by default.
- Encryption in transit/at rest.
- Signed images and SBOM.
- Tamper-evident audit.
- Tenant isolation tests.
- Rate limits and quotas.
- Retention/deletion policy.
- Break-glass access with enhanced audit.

See `docs/threat-model.md`.

## Multi-tenancy

Tenant identity is propagated through API, workflow, queue, evidence, vector search and audit. Authorization must be enforced at every boundary, not only the UI. Consider separate data-plane cells or encryption keys for high-isolation tenants.

## Reliability

Security scanning is naturally asynchronous. Use durable queues and at-least-once workers. Every job needs an idempotency key. Scanner side effects must tolerate retry. Poison jobs move to a DLQ with controlled replay.

If the LLM is unavailable, deterministic scanning/detection should continue and findings remain visible without AI explanation.

If ZAP is unavailable, code/log/compliance workflows continue. Avoid a monolithic availability dependency.

## SLO examples

Illustrative engineering objectives:
- API availability >= 99.9%.
- accepted scan-job durability >= 99.99%.
- p95 API admission latency < 500 ms.
- 99% of queued baseline jobs begin within an agreed tenant tier window.
- audit event durability >= 99.99%.

Scanner completion latency depends on target size and profile, so measure queue wait separately from execution time.

## Capacity planning

At 1 million repository/log/scan assessments per day, average admission is ~11.6 jobs/s, but worker load is dominated by job duration. If a baseline scan averages 5 minutes and 10,000 run/day, it consumes ~50,000 worker-minutes/day. Capacity planning therefore models concurrent scanner-minutes, repository size, log bytes, LLM tokens and evidence writes—not only request RPS.

Use tenant quotas, bounded concurrency, fair queues and workload classes.

## Cell architecture

Large deployments can use cells. Each cell owns workers, queue, evidence partition and vector partition. A bad scanner workload or noisy tenant is contained within a cell. The global control plane stores policy/model/rule versions but not necessarily tenant evidence.

## Observability

Metrics:
- jobs accepted/completed/failed,
- queue age,
- scanner duration,
- findings by normalized severity and rule,
- false-positive/override rate,
- analyzer error rate,
- LLM latency/error/token usage,
- compliance evidence gaps,
- DLQ size,
- policy denials.

Do not put source code, log messages, secrets, URLs with credentials, user identifiers or raw evidence into metric labels.

Use OpenTelemetry traces with safe IDs joining API → workflow → scanner → evidence → model → audit.

## Model gateway

The gateway centralizes:
- approved model aliases,
- timeout/retry,
- temperature,
- token budgets,
- prompt versions,
- structured outputs,
- provider routing,
- redaction,
- tenant budgets,
- trace metadata.

Fallback must respect data residency and contractual constraints. Never silently route sensitive code/logs to an unapproved provider.

## Evaluation

Evaluate the **system**, not just the model.

### Scanner
Use intentionally vulnerable local test fixtures or sanctioned lab targets. Measure normalized finding ingestion and deduplication. Never run evaluation against arbitrary public targets.

### Code analyzer
Use labeled secure/insecure snippets. Track precision/recall by rule and language. Test secret-redaction and prompt injection in comments.

### Log analyzer
Use replayable synthetic incidents and benign baselines. Measure detection precision, recall, detection delay and alert volume.

### Compliance
Use evidence fixtures with known present/missing controls. Missing evidence must never become PASS due to persuasive text.

### LLM
Measure factual consistency with evidence, remediation usefulness, unsupported claims, citation correctness and refusal to follow instructions embedded in evidence.

LLM-as-judge is supplemental; deterministic ground truth and security-expert review are release gates.

## Change management

Treat this tuple as a release unit:

`scanner version + rules + normalizer + policy + model + prompt + RAG corpus + compliance catalog`

Run offline regression, shadow evaluation, limited canary and progressive rollout. Preserve prior versions for forensic reproducibility.

## Incident response

The auditor itself is security-critical. Prepare for:
- leaked repository token,
- compromised scanner worker,
- malicious evidence document,
- cross-tenant access bug,
- model provider incident,
- audit pipeline outage,
- false-positive storm,
- queue poisoning.

Containment should be deterministic and human-controlled. Preserve evidence and audit before destructive remediation where policy requires.

## Disaster recovery

Back up policy/rule catalogs, workflow state, evidence metadata and audit according to retention policy. Object evidence may require separate immutable storage. Test restoration. Multi-region failover must preserve tenant residency and authorization boundaries.

## CI/CD

A production pipeline should include:
- unit/integration tests,
- SAST,
- dependency/SCA,
- secret scanning,
- IaC scanning,
- SBOM generation,
- image vulnerability scanning,
- image signing/attestation,
- policy tests,
- model/prompt evaluation,
- progressive deployment.

The included GitHub Actions workflow runs compilation and tests.

## Local run

Python 3.11+:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.api:app --reload
```

Swagger: `http://localhost:8000/docs`

Default mode is fully local/mock and does not scan the internet.

## Optional OpenAI mode

```bash
export LLM_MODE=openai
export OPENAI_API_KEY=...
export OPENAI_MODEL=gpt-4.1-mini
```

Use only providers/models approved for the sensitivity of the analyzed code/log/evidence.

## Example: code analysis

```bash
curl -X POST http://localhost:8000/v1/code/analyze \
  -H 'Content-Type: application/json' \
  -d '{"tenant_id":"demo","repository":"sample","path":"app.py","content":"verify=False"}'
```

## Example: log analysis

```bash
curl -X POST http://localhost:8000/v1/logs/analyze \
  -H 'Content-Type: application/json' \
  -d '{"tenant_id":"demo","lines":["login failed","login failed","login failed","login failed","login failed"]}'
```

## Example: authorized baseline scan

Mock mode:

```bash
curl -X POST http://localhost:8000/v1/vulnerability/scan \
  -H 'Content-Type: application/json' \
  -d '{"tenant_id":"demo","target":"https://app.internal.example","authorization_id":"lab-authorization"}'
```

To wire real ZAP, configure an allowlist and adapter mode. The LLM cannot alter the target or scan profile.

## Docker

```bash
docker compose -f deploy/docker-compose.yml up --build
```

## Principal/Staff interview discussion

Be prepared to explain:
- why the model is not given shell/network credentials;
- how scan authorization survives redirects/DNS changes;
- how scanner workers are isolated;
- how cross-tenant vector/evidence leakage is prevented;
- how findings are deduplicated across tool versions;
- how you handle a false-positive storm after a rules update;
- why "no findings" does not imply compliance;
- how compliance evidence is versioned;
- how source-code prompt injection is neutralized;
- what happens during LLM outage;
- how you reproduce a finding six months later;
- how queue semantics and idempotency interact;
- how you prevent secrets from reaching model providers;
- how you calculate capacity from scanner-minutes rather than RPS;
- how cell architecture limits blast radius;
- how to canary scanner/rule changes;
- how to evaluate anomaly detection without drowning analysts;
- how to model accepted risk and expiring exceptions;
- how audit differs from observability;
- how to fail closed for authorization while degrading gracefully for explanation.

## Production roadmap

1. Deterministic SAST/SCA aggregation and evidence normalization.
2. Authorized baseline DAST workers.
3. Tenant-scoped secure-coding RAG and AI explanations.
4. Streaming log anomaly pipeline.
5. Versioned compliance evidence graph.
6. Human triage/workflow integrations.
7. Cell-based regional scale and advanced policy engine.

## Resume framing

> Designed and implemented an authorization-first agentic security assurance platform combining OWASP ZAP-style DAST, deterministic source-code security analysis, log anomaly detection, compliance evidence mapping, tenant-isolated RAG and LLM-assisted remediation. Architected strict trust boundaries between probabilistic AI reasoning and privileged security operations, with auditable workflows, scanner isolation, policy enforcement and production observability.

## Disclaimer

This project is for defensive security engineering and authorized assessment. Do not scan systems without permission.
