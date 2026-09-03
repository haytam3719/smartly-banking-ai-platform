# AI Orchestrator

Central conversational coordinator for the Smartly Banking AI Platform. It uses LangGraph for short-lived request orchestration. It never calls Core Banking directly: an LLM may propose only a strict capability plan, and application code validates, resolves, authorizes, and executes that plan.

## Architecture and trust boundary

```text
Channel -> POST /chat -> authenticated principal
                          |
START -> normalize_request -> llm.route -> validate_plan
  -> registry.resolve -> policy.authorize
  -> execute_tools (independent reads use asyncio.gather)
  -> evaluate_tool_results
       | failure ------------------------------> grounded answer -> END
       | TOOLS_ONLY --------------------------> evidence gate ---^
       | RAG_ONLY/HYBRID -> build safe query -> knowledge.search -^

WORKFLOW: LangGraph starts/queries -> Account Opening Workflow -> Temporal
          response returns immediately; LangGraph never waits for durable review/input
```

Registry resolution prevents hardcoded agent URLs. Policy authorization is performed for every capability, including knowledge retrieval, before execution. Customer-scoped requests propagate independently authenticated subject/customer headers. Production must set `DEV_AUTH_MODE=false`; development mode defaults on only for challenge-compatible body-only `/chat` calls.

## Routing and unnecessary-call prevention

`RoutingPlan` permits only `RAG_ONLY`, `TOOLS_ONLY`, `HYBRID`, `WORKFLOW`, `CLARIFY`, or `UNSUPPORTED`, with canonical capability enums and at most six unique actions. Coherence validation prevents RAG in tool-only plans, tools in RAG-only plans, arbitrary names, and invalid workflow actions.

- Balance, transactions, cards, and transfer status use tools only.
- General fees/policy use Knowledge Search only.
- Rejected-transfer explanations fetch transfer facts first, then search policy only after success.
- Independent tools run concurrently; dependent Tool → RAG stages never do.
- Account-opening starts require explicit intent, type, and currency; missing values produce `CLARIFY`.
- Workflow starts use a stable conversation/argument-derived idempotency key and are never automatically retried.

The local heuristic router is deterministic. `LLM_PROVIDER=openai-compatible` selects strict JSON-schema structured routing and answer generation. In either mode, the model cannot execute HTTP clients.

## Grounding and data minimization

The answer generator sees only the question, validated TOOL/RAG/WORKFLOW evidence, and safe answer instructions. Workflow results retain `metadata.evidence_kind=WORKFLOW` but use public type `TOOL` to remain compatible with the shared Evidence schema. It must answer in the user language, avoid invented balances/statuses/fees/rules, distinguish dynamic customer facts from general policy, report unavailable information, ignore instructions embedded in documents, and reveal no system details.

For rejected transfers, the RAG query contains only verified `status` and `rejection_reason`. Amount, beneficiary, transfer ID, customer ID, and raw prompt are excluded. If transfer retrieval fails, RAG is not called. Financial tool results are never stored in Redis; optional Redis conversation state contains only locale and an expiry timestamp.

## Exact challenge scenarios

| Request | Route | Calls | Reported source |
| --- | --- | --- | --- |
| `Quel est mon solde ?` | TOOLS_ONLY | `account.balance.read` | `get_account_balance` |
| `Montrez mes transactions` | TOOLS_ONLY | `account.transactions.read` | `get_account_transactions` |
| `Quel est le statut de ma carte ?` | TOOLS_ONLY | `card.info.read` | `get_card_info` |
| `Quel est le statut de mon virement TR4587 ?` | TOOLS_ONLY | `transfer.status.read` | `get_transfer_status` |
| `Mon virement TR4587 a été refusé. Pourquoi ?` | HYBRID | transfer, then minimized `knowledge.search` | `get_transfer_status + RAG` |
| `Quels sont les frais d'un virement international ?` | RAG_ONLY | `knowledge.search` | `RAG` |
| `Je veux ouvrir un compte épargne en EUR.` | WORKFLOW | idempotent `account.opening.start` | `start_account_opening` |
| `Où en est mon ouverture de compte AO-123 ?` | WORKFLOW | `account.opening.status` | `get_account_opening_status` |

## Fail-safe behavior

LLM timeouts/invalid output, unknown capabilities, unavailable registry/policy, denial, agent timeouts/4xx/5xx, unavailable Knowledge Agent, empty retrieval, malformed requests, and missing workflow fields terminate safely. Unknown or denied capabilities are never invoked. Uncertain tool facts never trigger guessed policy RAG. The response does not contain stack traces.

## Observability and audit

OpenTelemetry spans: `chat.request`, `llm.route`, `registry.resolve`, `policy.authorize`, `agent.execute`, `rag.search`, and `llm.answer`. W3C trace context plus request/correlation/conversation IDs propagate downstream.

Privacy-minimized Kafka-compatible audit events are emitted through an adapter: `ai.route.selected.v1`, `ai.agent.call.started.v1`, `ai.agent.call.completed.v1`, `ai.agent.call.failed.v1`, `ai.rag.search.completed.v1`, and `ai.response.generated.v1`. Events contain capability/outcome metadata, never full prompts or banking payloads. The default publisher emits structured JSON; `KafkaCompatibleAuditPublisher` accepts an async Kafka producer.

Example event sequence:

```text
ai.route.selected.v1 {mode: HYBRID, capabilities: [transfer.status.read, knowledge.search]}
ai.agent.call.started.v1 {capability: transfer.status.read, agent_id: transfer-agent}
ai.agent.call.completed.v1 {capability: transfer.status.read, success: true, latency_ms: 18}
ai.rag.search.completed.v1 {result_count: 2, document_types: [transfer_policy]}
ai.response.generated.v1 {source: get_transfer_status + RAG, evidence_count: 3}
```

## API and local run

```bash
curl -X POST http://localhost:8080/chat \
  -H 'Content-Type: application/json' \
  -H 'X-Request-Id: req-1' -H 'X-Correlation-Id: corr-1' \
  -d '{"customer_id":"C1024","message":"Quel est le statut de mon virement TR4587 ?","locale":"fr-FR"}'
```

Also exposed: `POST /api/v1/chat`, `GET /health/live`, and `GET /health/ready`.

Configuration: `AGENT_REGISTRY_URL`, `POLICY_ENGINE_URL`, optional `REDIS_URL`, `DEV_AUTH_MODE`, `LLM_PROVIDER`, `LLM_BASE_URL`, `LLM_API_KEY`, `LLM_MODEL`, and standard OTLP variables.

```bash
python -m venv .venv
.venv/Scripts/pip install -e '.[test]'
.venv/Scripts/python -m pytest -m 'not live_llm'
docker build -t smartly-ai-orchestrator .
```

## Architectural assumptions and production gaps

- Channel authentication supplies trusted subject/customer headers; development body fallback is never suitable for production.
- Account Opening Workflow will implement canonical AgentRequest/AgentResponse endpoints and idempotent starts.
- Agent Registry health is advisory; an agent can fail after resolution. The short in-process registry cache is not distributed and should add invalidation in production.
- Redis is optional and deliberately stores no financial truth. Conversation history/summarization is not yet implemented.
- The Kafka publisher boundary is present, but production producer lifecycle, delivery guarantees, schema-registry integration, and dead-letter handling remain infrastructure work.
- The OpenAI-compatible adapters need production rate limiting, model evaluation, secret management, regional/privacy review, and circuit breakers.
- Deterministic local answers are intentionally conservative. They demonstrate grounding rather than full natural-language quality.
- Readiness checks registry and policy; deeper dependency readiness and Kubernetes probes remain infrastructure work.
- No financial evidence cache validity policy exists, so current facts are always fetched again.
