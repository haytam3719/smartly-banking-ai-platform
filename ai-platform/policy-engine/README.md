# Policy Engine

Deterministic ABAC-style authorization service for actions proposed by the AI Orchestrator. This service contains no AI, model calls, prompt handling, LangChain, or LangGraph. The LLM can propose a canonical capability and arguments, but only this service decides whether execution is allowed.

## Why deterministic enforcement

Authorization must be repeatable, explainable, testable, and fail closed. Model output is probabilistic and can be affected by prompt injection, so it is treated only as an untrusted action proposal. The evaluator uses a small human-readable rule table covering canonical capability, required scope, customer scoping, and reason code. Unknown capabilities, missing identity, malformed context, scope failures, and identity mismatches are denied.

No output from an LLM can bypass this boundary: the orchestrator must obtain an `allowed: true` decision before calling an agent, while the downstream agent must still enforce ownership and authorization at its own data boundary. A policy decision is necessary but is not a substitute for domain authorization.

## Trust boundaries

The JSON `subject` and `customer_id` describe what the caller proposes; they do not authenticate anyone. A trusted gateway or workload-identity adapter supplies:

- `X-Authenticated-Subject-Id`: verified caller subject;
- `X-Authenticated-Customer-Id`: verified customer binding, required for customer-scoped capabilities.

The proposed subject ID must match the trusted subject header, and customer-scoped requests must match the trusted customer header. In deployment these headers must be stripped from external traffic and set only by an authenticated trusted proxy over protected service-to-service transport. A future integration can replace the header dependency with validated workload/JWT claims without changing policy evaluation.

Knowledge search requires an authenticated subject and `knowledge:search`, but it does not require a customer binding. All calls require a valid channel context: `MOBILE`, `WEB`, or `INTERNAL`.

## Supported policy rules

| Capability | Required scope | Customer scoped |
| --- | --- | --- |
| `account.balance.read` | `account:read` | yes |
| `account.transactions.read` | `account:read` | yes |
| `card.info.read` | `card:read` | yes |
| `transfer.status.read` | `transfer:read` | yes |
| `customer.info.read` | `customer:read` | yes |
| `knowledge.search` | `knowledge:search` | no |
| `account.opening.start` | `account:open` | yes |
| `account.opening.status` | `account:open` | yes |

## Run locally

Python 3.12 is required:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[test]'
uvicorn policy_engine.main:app --host 0.0.0.0 --port 8081
```

On Windows, activate with `.venv\Scripts\Activate.ps1`. Health is available at `GET /health`; generated OpenAPI is at `/openapi.json` and Swagger UI at `/docs`.

Docker:

```bash
docker build -t smartly-policy-engine .
docker run --rm -p 8081:8081 smartly-policy-engine
```

## Example

```bash
curl -X POST http://localhost:8081/internal/v1/authorize \
  -H 'Content-Type: application/json' \
  -H 'X-Authenticated-Subject-Id: user-123' \
  -H 'X-Authenticated-Customer-Id: C1024' \
  -H 'X-Request-Id: req-123' \
  -H 'X-Correlation-Id: corr-123' \
  -d '{
    "subject":{"id":"user-123","roles":["CUSTOMER"],"scopes":["transfer:read"]},
    "customer_id":"C1024",
    "capability":"transfer.status.read",
    "resource":{"transfer_id":"TR4587"},
    "context":{"channel":"MOBILE"}
  }'
```

The response includes `allowed`, a unique `decision_id`, stable `reason_code`, and `obligations`. Decision audit logs contain capability, outcome, reason, decision ID, and a non-reversible truncated subject fingerprint—never banking resources or request payloads.

## Observability and audit

Logs are JSON and include request, correlation, and active trace identifiers. FastAPI is instrumented with OpenTelemetry-compatible middleware and honors W3C trace context. Set `OTEL_EXPORTER_OTLP_TRACES_ENDPOINT` to export spans over OTLP/HTTP. No exporter is required for local operation.

Run tests with `pytest`. They cover permitted reads, missing scopes, unknown capabilities, anonymous access, customer-independent knowledge search, subject/customer mismatch, malformed inputs, and evaluation failure.

## Future OPA integration

`PolicyEvaluator` is an adapter boundary. A later deployment may implement it with OPA/Rego while preserving the HTTP and audit contracts. The in-process rules remain the local default: no OPA sidecar or network dependency is required. Migration should use parity tests against the current rule repository and retain fail-closed behavior.

