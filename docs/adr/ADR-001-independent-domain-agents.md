# ADR-001: Separate domain capabilities into independent agents

- Status: Accepted
- Date: 2026-08-30

## Context

Accounts, cards, transfers, customers, and knowledge have different data owners, authorization rules, failure modes, and release cadences. A general-purpose agent would accumulate excessive privileges and couple squads.

## Decision

Expose narrow canonical capabilities through independently owned domain agents. Each agent validates arguments, enforces domain safeguards, owns its downstream adapter, and returns a canonical `AgentResponse` with evidence. Registry metadata maps capabilities to compatible instances.

## Consequences

Teams deploy and scale independently, blast radius and credentials are narrower, and capability policy is auditable. The platform accepts more services, cross-service contracts, discovery, and operational overhead. Cross-domain answers are composed by the orchestrator, not by allowing agents to bypass boundaries.

