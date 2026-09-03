# Smartly Banking AI Platform

Production-oriented monorepo for a distributed, AI-assisted banking challenge. It includes canonical contracts, independently deployable banking agents, policy enforcement, service discovery, LangGraph orchestration, grounded knowledge retrieval, a mobile BFF, and a deterministic core-banking simulator. All local customer data and banking behavior are synthetic. Examples and challenge rules must not be represented as real-bank policy.

## Challenge context and scenarios

The platform is designed to support these exact challenge scenarios:

- answer a customer's account-balance question;
- retrieve recent account transactions;
- retrieve card information;
- check a transfer's status;
- retrieve customer information;
- answer grounded knowledge questions from a controlled document corpus;

The supplied `customer_id` exists to satisfy the technical challenge. In production, customer identity must normally be derived from validated authentication claims, not trusted from request input.

## Architecture

Mobile and web clients call their Channel BFF. The BFF authenticates and forwards a normalized request to the AI Orchestrator. The orchestrator uses conversational state and asks the Policy Engine to authorize a canonical capability. The Agent Registry resolves an eligible Domain Agent, and that agent alone talks to the relevant Core Banking API. Knowledge retrieval is isolated in the Knowledge Agent.

LangGraph is for short-lived conversational orchestration. Temporal is for durable, retryable, long-running business processes. See [the system overview](docs/architecture/system-overview.md) and [ADRs](docs/adr/README.md).

## Ownership model

| Area | Hypothetical owner | Responsibility |
| --- | --- | --- |
| `channels/` | Digital Channels squad | Mobile/web APIs and authentication edge |
| `ai-platform/` | AI Platform squad | Orchestration, policy enforcement, agent discovery |
| `agents/` | Domain AI squads | Narrow capability adapters and evidence |
| `workflows/` | Business Process Automation squad | Durable business processes |
| `simulators/` | Developer Experience squad | Synthetic core-banking behavior |
| `contracts/` | Architecture Enablement | Canonical APIs, schemas, and events |
| `infrastructure/` | Platform Engineering | Runtime, messaging, deployment, telemetry |
| `tests/` | Quality Engineering | Cross-service contract and end-to-end tests |
| `docs/` | All squads, governed by Architecture | Decisions, diagrams, threats, platform design |

## Technology map

| Concern | Intended technology |
| --- | --- |
| Channel and internal APIs | HTTP/JSON with OpenAPI and JSON Schema |
| Conversational orchestration | LangGraph |
| Durable workflows | Temporal |
| Asynchronous events | Kafka |
| Knowledge retrieval | Qdrant plus a governed document corpus |
| Local composition | Docker Compose |
| Deployment | Kubernetes |
| Observability | OpenTelemetry-compatible traces, metrics, and structured logs |

Implemented services pin their runtime dependencies independently; workflow, messaging, and deployment technologies remain architectural targets until their corresponding components are added.

## Local development

Prerequisites are Git, Docker with Compose, GNU Make, and Python 3 for lightweight contract parsing. Copy `.env.example` to `.env`, keep secrets local, and run `make validate-contracts`. Run `docker compose up --build` (or `make up`) to build and start the local platform.

Each service should eventually be independently buildable and deployable. Local defaults must use synthetic identities and data. Contract changes should be backward compatible or explicitly versioned and validated in `tests/contract/` before consumers adopt them.

## Security principles

- Derive customer identity from verified authentication context in production; reject mismatches with any compatibility request field.
- Apply least privilege, explicit capability allowlists, and policy checks before every tool call.
- Never allow an LLM to call a core banking API directly.
- Treat prompts, retrieved documents, model output, and tool arguments as untrusted data.
- Minimize PII in transit, logs, traces, and events; never publish raw prompts by default.
- Return safe canonical errors and never API stack traces.
- Use authenticated, authorized, encrypted service-to-service communication in deployed environments.

See the [threat model](docs/threat-model/platform-threat-model.md).

## Observability

Every request receives a request ID and participates in a correlation and distributed trace. Services propagate `X-Request-Id`, `X-Correlation-Id`, `X-Conversation-Id` when applicable, and W3C `traceparent`. Structured logs and metrics use identifiers rather than prompt or PII content. Versioned lifecycle events provide an auditable, privacy-minimized record of routing, agent calls, RAG completion, and generated responses.

## Communication model

User-facing, low-latency calls use synchronous HTTP with bounded timeouts. Auditing and business workflow notifications use versioned Kafka events. HTTP contracts use canonical capabilities and errors in `contracts/schemas/`; event envelopes live in `contracts/events/`. Correlation and trace identifiers must cross both transports. Events are facts, not remote procedure calls, and consumers must be idempotent.
