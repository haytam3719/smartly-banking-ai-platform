# ADR-002: Prohibit direct LLM access to core banking APIs

- Status: Accepted
- Date: 2026-08-30

## Context

Model output is probabilistic and influenced by untrusted prompts and retrieved content. Core APIs expose high-impact customer data and operations.

## Decision

The LLM may propose only allowlisted capabilities and typed arguments. The Policy Engine authorizes the effective subject/customer/capability combination, and a least-privileged Domain Agent performs the core call. The LLM, model provider, and orchestrator receive no core-banking credentials.

## Consequences

Tool abuse, injection impact, and credential exposure are constrained. Validation and authorization are deterministic and independently auditable. Extra network hops add latency and implementation work, addressed through deadlines, telemetry, and narrow APIs. A fluent model response is never accepted as evidence of a banking fact.

