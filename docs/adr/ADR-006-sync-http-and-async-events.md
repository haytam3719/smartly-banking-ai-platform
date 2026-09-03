# ADR-006: Use synchronous HTTP and asynchronous events by purpose

- Status: Accepted
- Date: 2026-08-30

## Context

Interactive users need immediate answers, while auditing and business workflow notifications require decoupling, replay, and resilience.

## Decision

Use synchronous HTTP for user-facing, low-latency BFF, orchestration, policy, registry, and agent calls. Use versioned Kafka events for privacy-minimized audit facts and business workflow state changes. Propagate correlation and trace identifiers over both.

## Consequences

HTTP provides simple request/response semantics but requires strict timeouts, bounded retries, and failure handling. Events decouple producers and consumers but require idempotency, schema evolution, ordering assumptions, retention governance, and eventual-consistency-aware UX. Events are not used as disguised synchronous RPC.

