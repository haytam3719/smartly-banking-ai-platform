# Transfer Agent

Read-only domain boundary for `transfer.status.read`. The word *agent* denotes capability ownership; this service has no LLM or autonomous authorization logic and exposes no transfer mutations.

## Trust and data flow

The caller supplies the canonical `AgentRequest` and an authenticated customer identity in `X-Authenticated-Customer-Id`. The two customer identifiers must match. The adapter then calls only:

`GET {CORE_BANKING_URL}/internal/v1/customers/{customer_id}/transfers/{transfer_id}`

There is no global transfer lookup. Core Banking returns the same 404 for an unknown transfer and a transfer belonging to another customer; this agent maps both to the safe `TRANSFER_NOT_FOUND` error and does not disclose existence or ownership.

Successful data is allowlisted to `transfer_id`, `amount`, `currency`, `beneficiary`, `created_at`, `status`, and `rejection_reason`. Backend-only fields are discarded. Amounts serialize as exact decimal strings.

## Hybrid Tool + RAG support

`TransferCapabilityService.policy_facts` creates a deliberately minimized representation:

```json
{"status":"REJECTED","rejection_reason":"PAYMENT_LIMIT_EXCEEDED"}
```

It excludes transfer ID, amount, currency, beneficiary, and timestamps. A future orchestrator may use these verified facts to select policy knowledge, but must not start RAG when this agent returns `success: false`. This agent itself performs no RAG and offers no banking-policy interpretation.

## API

- `POST /internal/v1/capabilities/transfer.status.read`
- `GET /internal/v1/capabilities`
- `GET /health`
- `GET /metrics`

```bash
curl -X POST http://localhost:8080/internal/v1/capabilities/transfer.status.read \
  -H 'Content-Type: application/json' \
  -H 'X-Authenticated-Customer-Id: C1024' \
  -d '{"request_id":"req-1","correlation_id":"corr-1","conversation_id":"conv-1","subject":"user-123","customer_id":"C1024","capability":"transfer.status.read","arguments":{"transfer_id":"TR4587"},"locale":"fr-FR"}'
```

## Resilience and observability

The adapter uses a strict `CORE_BANKING_TIMEOUT_SECONDS` timeout (default `0.8`) and at most three attempts for timeouts, transport failures, and HTTP 5xx. It never retries 4xx. Failures return structured safe errors with no uncertain transfer facts. Request, correlation, conversation, authorization, and W3C trace context are propagated. Logs are structured JSON without banking payloads. Prometheus metrics cover capability latency and categorized downstream errors; OTLP export is enabled by `OTEL_EXPORTER_OTLP_ENDPOINT`.

Configuration: `CORE_BANKING_URL` (default `http://core-banking:8090`), optional `CORE_BANKING_API_KEY`, `CORE_BANKING_TIMEOUT_SECONDS`, and standard OpenTelemetry variables.

## Run and test

```bash
python -m venv .venv
.venv/Scripts/pip install -e '.[test]'
.venv/Scripts/python -m pytest
docker build -t smartly-transfer-agent .
docker run --rm -p 8080:8080 -e CORE_BANKING_URL=http://host.docker.internal:8090 smartly-transfer-agent
```
