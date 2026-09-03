# System overview

## Request path

```text
Mobile / Web
     ↓
Channel BFF
     ↓
AI Orchestrator
     ↓
Policy Engine
     ↓
Agent Registry
     ↓
Domain Agents
     ↓
Core Banking APIs
```

The Channel BFF is the trust boundary for its client: it authenticates the caller, derives the effective customer identity from validated claims, normalizes requests, and applies channel controls. The client-provided `customer_id` retained for this challenge cannot grant access in production.

The AI Orchestrator maintains conversational state, proposes only canonical capabilities, and coordinates results. Before execution, the Policy Engine independently decides whether the authenticated subject may use that capability for that customer and arguments. The Agent Registry maps an allowed capability to a healthy, compatible agent endpoint. Domain Agents validate typed arguments, enforce domain safeguards, and translate calls to narrowly scoped Core Banking APIs. Neither the orchestrator nor an LLM receives core-banking credentials.

## Grounded knowledge path

```text
AI Orchestrator
     ↓
Knowledge Agent
     ↓
Qdrant / governed document corpus
```

The Knowledge Agent owns retrieval, corpus access control, document provenance, ranking, and evidence formatting. Retrieved text remains untrusted input. It is screened for injection and returned with citations and confidence where applicable. The orchestrator must distinguish retrieved policy-like content from authoritative transactional tool data and must not turn synthetic challenge material into claims about real banking policy.

## Long-running workflows

```text
AI Orchestrator
     ↓
Durable Workflow Service
     ↓
Temporal
```

The orchestrator starts or queries a workflow through a stable service API and returns promptly. Temporal persists workflow state, timers, retries, compensation, and human-wait steps across process restarts. Status-change events let other systems react without coupling them to workflow internals.

The boundary is deliberate:

- **LangGraph is conversational orchestration:** seconds-to-minutes interaction graphs, routing, tool coordination, conversational checkpoints, and response synthesis.
- **Temporal is durable business processing:** hours-to-days processes, reliable timers, retries, signals, human review, and recoverable state transitions.

LangGraph must not become the system of record for a durable business process. A workflow engine must not be used to model token-by-token conversational reasoning.

## Trust, communication, and failure boundaries

Synchronous HTTP serves low-latency user interactions with authentication, explicit deadlines, bounded retries, circuit breakers, and canonical errors. Versioned asynchronous events serve audit trails and workflow/domain notifications. They carry correlation and trace identifiers across boundaries and no raw prompts or unnecessary PII.

Each service is independently deployable and owns its runtime and data. Contracts, not shared databases, connect squads. Agent responses provide structured data and evidence; the orchestrator never invents transactional facts when a tool fails. It returns a safe limitation or requests clarification. All hops propagate request, correlation, conversation, and trace context according to `contracts/schemas/http-standards.md`.
