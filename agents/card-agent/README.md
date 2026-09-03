# Card Agent

Read-only domain boundary for `card.info.read`. “Agent” means isolated capability ownership, not autonomy: this service contains no LLM and makes no model-driven decisions. It deliberately implements no block, unblock, limit change, payment, account, transfer, customer-profile, or knowledge behavior.

## Contract and trust boundary

`POST /internal/v1/capabilities/card.info.read` accepts the shared `AgentRequest` and returns the shared `AgentResponse`. The request capability must be exactly `card.info.read`, arguments must be empty, and its customer ID must match the trusted `X-Authenticated-Customer-Id` set by the internal authenticated boundary. A client-supplied customer ID alone never grants access.

The successful `data` object contains only:

```json
{
  "card_type": "GOLD",
  "status": "ACTIVE",
  "expiration_date": "2028-05",
  "payment_limit": "2500",
  "amount_used": "1800",
  "available_limit": "700",
  "currency": "EUR"
}
```

Amounts are decimal strings to preserve precision. `available_limit` is always computed in application code as `max(payment_limit - amount_used, 0)`. Blocked, frozen, and expired statuses are reported read-only; the agent never changes them. Card ID, PAN, CVV, cardholder name, and other unnecessary fields are excluded even if supplied downstream.

## Downstream

`CardPort` isolates domain use from HTTP. `CoreBankingCardAdapter` calls `GET /internal/v1/customers/{customerId}/cards/primary`. Configure `CORE_BANKING_URL`, optional `CORE_BANKING_API_KEY`, and `CORE_BANKING_TIMEOUT_SECONDS` (default `0.8`). Timeouts, transport failures, and 5xx responses receive no more than three attempts; 4xx responses are never retried. All failures use safe canonical errors.

Request, correlation, conversation, and W3C trace context propagate downstream. JSON logs avoid card data. `/metrics` exposes capability latency and categorized downstream errors; OTLP/HTTP export is enabled with `OTEL_EXPORTER_OTLP_TRACES_ENDPOINT`.

## APIs and operation

- `POST /internal/v1/capabilities/card.info.read`
- `GET /internal/v1/capabilities`
- `GET /health`
- `GET /metrics`

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[test]'
pytest
uvicorn card_agent.main:app --host 0.0.0.0 --port 8080
```

Windows activation is `.venv\Scripts\Activate.ps1`. Docker:

```bash
docker build -t smartly-card-agent .
docker run --rm -p 8080:8080 -e CORE_BANKING_URL=http://host.docker.internal:8090 smartly-card-agent
```

Example:

```bash
curl -X POST http://localhost:8080/internal/v1/capabilities/card.info.read \
  -H 'Content-Type: application/json' \
  -H 'X-Authenticated-Customer-Id: C1024' \
  -d '{"request_id":"req-1","correlation_id":"corr-1","conversation_id":"conv-1","subject":"user-123","customer_id":"C1024","capability":"card.info.read","arguments":{},"locale":"fr-FR"}'
```

