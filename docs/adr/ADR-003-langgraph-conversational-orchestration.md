# ADR-003: Use LangGraph for conversational orchestration

- Status: Accepted
- Date: 2026-08-30

## Context

Chat requires explicit routing, bounded tool loops, policy gates, evidence collection, conversational context, and observable state transitions.

## Decision

Use LangGraph inside the AI Orchestrator for short-lived conversational graphs. Nodes and edges represent deterministic gates and model-assisted decisions; state is typed, checkpointed as appropriate, and bounded by call/time budgets.

## Consequences

Conversation flow becomes inspectable and testable, with controlled retries and human-readable topology. The platform assumes a framework dependency and must manage graph/schema evolution. LangGraph checkpoints are not the authoritative state for durable business processes; those go to Temporal.

