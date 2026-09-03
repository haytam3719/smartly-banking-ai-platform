# Customer Agent

Read-only domain boundary for `customer.info.read`. The term *agent* identifies capability ownership; this service contains no LLM logic and makes no autonomous decisions.

## Minimal profile contract

The response deliberately contains only the banking-profile attributes required by current conversational workflows:

```json
{"customer_id":"C1024","segment":"RETAIL","kyc_status":"VERIFIED","country":"MA"}
```

The Core Banking adapter uses an explicit allowlist. First/last names, passwords, credentials, addresses, sensitive identifiers, internal risk notes, and all unknown backend fields are discarded. Adding profile fields requires a future capability justification and corresponding contract/security review.

## Trust boundary and downstream API

The caller provides a canonical `AgentRequest` and the authenticated identity separately in `X-Authenticated-Customer-Id`. They must match before any downstream request occurs. The adapter calls only:

`GET {CORE_BANKING_URL}/internal/v1/customers/{customer_id}`

It verifies the returned `customer_id` matches the trusted scoped ID. Configure `CORE_BANKING_URL` (default `http://core-banking:8090`), optional `CORE_BANKING_API_KEY`, and `CORE_BANKING_TIMEOUT_SECONDS` (default `0.8`).

## API

- `POST /internal/v1/capabilities/customer.info.read`
- `GET /internal/v1/capabilities`
- `GET /health`
- `GET /metrics`

```bash
curl -X POST http://localhost:8080/internal/v1/capabilities/customer.info.read \
  -H 'Content-Type: application/json' \
  -H 'X-Authenticated-Customer-Id: C1024' \
  -d '{"request_id":"req-1","correlation_id":"corr-1","conversation_id":"conv-1","subject":"user-123","customer_id":"C1024","capability":"customer.info.read","arguments":{},"locale":"fr-FR"}'
```

## Resilience and observability

Timeouts, transport failures, and HTTP 5xx receive at most three attempts; 4xx responses are never retried. Unknown customers and unreliable results map to safe structured errors without profile data. Request, correlation, conversation, authorization, and validated W3C trace context are propagated. Logs are structured JSON and never log profile payloads. Prometheus metrics cover latency and downstream errors. Set `OTEL_EXPORTER_OTLP_ENDPOINT` to export traces.

## Run and test

```bash
python -m venv .venv
.venv/Scripts/pip install -e '.[test]'
.venv/Scripts/python -m pytest
docker build -t smartly-customer-agent .
docker run --rm -p 8080:8080 -e CORE_BANKING_URL=http://host.docker.internal:8090 smartly-customer-agent
```
