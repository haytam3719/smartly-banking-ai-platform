# Account Agent

A deterministic domain capability boundary for account balances and transactions. “Agent” describes ownership and isolation—not autonomous behavior. This service contains no LLM, prompt routing, card logic, transfer logic, customer-profile logic, or RAG.

## Owned capabilities

- `account.balance.read`
- `account.transactions.read`

The service accepts the canonical shared `AgentRequest` and returns the canonical shared `AgentResponse`. The capability in the request must exactly match the fixed endpoint. The supplied `customer_id` is only a claim: it must match `X-Authenticated-Customer-Id`, which a trusted internal authentication boundary sets after policy authorization. External callers must not be allowed to forge this header.

Balance data is normalized as `data.accounts[]` with `available_balance`, `currency`, `account_type`, and `status`. Transaction data is normalized as `data.transactions[]`. Transaction arguments accept optional ISO dates `start_date` and `end_date`, plus `limit` from 1 through the server-enforced maximum of 100.

## APIs

| Method | Path |
| --- | --- |
| POST | `/internal/v1/capabilities/account.balance.read` |
| POST | `/internal/v1/capabilities/account.transactions.read` |
| GET | `/internal/v1/capabilities` |
| GET | `/health` |
| GET | `/metrics` |

## Core Banking downstream contract

`AccountPort` isolates account use cases from transport. `CoreBankingAccountAdapter` implements it against:

- `GET /internal/v1/customers/{customerId}/accounts/balance`
- `GET /internal/v1/customers/{customerId}/transactions`

Configure `CORE_BANKING_URL` (default `http://core-banking:8090`), `CORE_BANKING_TIMEOUT_SECONDS` (default `0.8`), and optionally `CORE_BANKING_API_KEY`. Request, correlation, conversation, and W3C trace context are propagated.

Timeouts, transport failures, and 5xx responses receive at most three attempts with short bounded exponential delays. No 4xx response is retried. Errors are mapped to safe canonical responses without downstream bodies or stack traces.

## Run

Python 3.12:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[test]'
uvicorn account_agent.main:app --host 0.0.0.0 --port 8080
```

On Windows use `.venv\Scripts\Activate.ps1`. Docker:

```bash
docker build -t smartly-account-agent .
docker run --rm -p 8080:8080 -e CORE_BANKING_URL=http://host.docker.internal:8090 smartly-account-agent
```

## Examples

```bash
curl -X POST http://localhost:8080/internal/v1/capabilities/account.balance.read \
  -H 'Content-Type: application/json' \
  -H 'X-Authenticated-Customer-Id: C1024' \
  -d '{"request_id":"req-1","correlation_id":"corr-1","conversation_id":"conv-1","subject":"user-123","customer_id":"C1024","capability":"account.balance.read","arguments":{},"locale":"fr-FR"}'

curl -X POST http://localhost:8080/internal/v1/capabilities/account.transactions.read \
  -H 'Content-Type: application/json' \
  -H 'X-Authenticated-Customer-Id: C1024' \
  -d '{"request_id":"req-2","correlation_id":"corr-1","conversation_id":"conv-1","subject":"user-123","customer_id":"C1024","capability":"account.transactions.read","arguments":{"start_date":"2026-08-01","end_date":"2026-08-31","limit":25},"locale":"fr-FR"}'
```

Logs are structured JSON and avoid banking payloads. Prometheus metrics expose capability latency and categorized downstream errors. FastAPI and HTTPX use OpenTelemetry-compatible instrumentation; configure `OTEL_EXPORTER_OTLP_TRACES_ENDPOINT` for OTLP/HTTP export.

