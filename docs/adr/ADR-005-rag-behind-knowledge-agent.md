# ADR-005: Isolate RAG behind a Knowledge Agent

- Status: Accepted
- Date: 2026-08-30

## Context

Retrieval needs corpus governance, access control, provenance, ranking, injection defenses, and vector-store evolution. Embedding these concerns in every consumer duplicates risk and implementation.

## Decision

Only the Knowledge Agent exposes `knowledge.search`. It owns Qdrant access, corpus ingestion policy, tenant/security filtering, retrieval quality controls, and canonical RAG evidence. Other agents and the orchestrator do not query the vector store directly.

## Consequences

Governance and defenses are centralized, and vector technology can change behind a contract. The agent is a scaling and availability dependency and needs strong tenancy tests. Retrieved documents remain untrusted and cannot authorize tools or override system policy.

