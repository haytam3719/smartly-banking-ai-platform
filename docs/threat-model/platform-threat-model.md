# Platform threat model

## Scope and assets

This architecture protects customer identity and banking data, authentication and service credentials, capability authorization, conversation/workflow integrity, governed knowledge, and audit evidence. Trust boundaries exist at clients, BFFs, every service identity, model providers, Kafka, Qdrant/document ingestion, Temporal, and core-banking adapters. This is an architecture-level baseline; each implementation still requires service-specific threat modeling and testing.

| Threat | Example impact | Architecture mitigations |
| --- | --- | --- |
| Prompt injection | User or retrieved text instructs the model to ignore policy or exfiltrate data. | Treat all content as untrusted; separate instructions from data; allowlist typed capabilities; independently authorize every call; scan and delimit retrieval; test adversarial prompts. |
| Tool abuse | Model loops, selects a high-impact tool, or supplies manipulated arguments. | Capability enums; typed schemas; Policy Engine gate; per-turn/tool budgets; deadlines and rate limits; read/write separation; audit lifecycle events. |
| Cross-customer data access | One subject reads another customer's accounts. | Derive effective customer from validated claims; object-level authorization in policy and Domain Agent; tenant-scoped credentials/queries; negative isolation tests. |
| Forged customer IDs | Client alters the challenge-compatible `customer_id`. | Never treat the field as identity; BFF derives identity from authentication context; reject mismatches; signed audience-bound credentials between services. |
| PII leakage | Prompts, model providers, logs, traces, or events expose customer data. | Data minimization/redaction; provider data controls; purpose-bound fields; encrypted transport/storage; access and retention controls; no raw prompts/events by default. |
| Excessive tool calls | Cost/availability exhaustion or repeated data access. | Per-user and per-conversation quotas; graph step limits; circuit breakers; concurrency limits; caching only where safe; anomaly metrics. |
| RAG poisoning | Malicious corpus content changes answers or triggers tools. | Authenticated ingestion; source allowlists; review/provenance/versioning; malware/content checks; tenant filters; retrieval never grants authority; citations and rollback. |
| Sensitive logging | Tokens, prompts, account data, or stack traces enter telemetry. | Structured allowlist logging; centralized redaction; secret scanning; access-controlled telemetry; retention limits; safe API errors. |
| Compromised internal service | Attacker moves laterally or calls capabilities directly. | Zero-trust service identity, mTLS, audience-bound tokens, least privilege, network policy, secret rotation, egress controls, independent authorization, detection and revocation. |
| Hallucinated banking information | Fabricated balance, transfer status, eligibility, or policy harms a customer. | Ground factual claims in current tool/RAG evidence; label source; fail closed when evidence is absent/stale; deterministic formatting/checks; evaluation suites; escalation paths. |

## Security invariants

No model output can authorize itself, choose an arbitrary internal capability, or supply customer identity without deterministic verification. Domain Agents authorize again at the data boundary. Core-banking credentials never reach the LLM. Responses do not state transactional facts without successful current evidence. Event and telemetry payloads exclude raw prompts and unnecessary PII. API errors never expose stack traces.

## Residual risk and validation

Models and documents remain probabilistic/untrusted, and authorized insiders or compromised dependencies remain possible. Before production, teams must perform data-flow reviews, dependency and image scanning, penetration tests, prompt/tool red-team tests, cross-customer contract tests, recovery exercises, model/RAG evaluations, and applicable regulatory/privacy assessment. Synthetic challenge rules must not be presented as actual bank policy.

