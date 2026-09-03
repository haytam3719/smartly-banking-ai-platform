# Core Banking Simulator

Internal Spring Boot service that replaces unavailable real banking APIs with deterministic synthetic data for development and automated testing. It contains no AI, LLM, lending, affordability, loan, or credit-scoring logic. Its demo rules and data are not real-bank policies.

## APIs

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/internal/v1/customers/{customerId}` | Customer profile |
| GET | `/internal/v1/customers/{customerId}/accounts/balance` | Customer-scoped account balances |
| GET | `/internal/v1/customers/{customerId}/transactions` | Transactions filtered by optional `start_date`, `end_date`, and `limit` |
| GET | `/internal/v1/customers/{customerId}/cards/primary` | Primary active card |
| GET | `/internal/v1/customers/{customerId}/transfers/{transferId}` | Customer-owned transfer only |
| POST | `/internal/v1/customers/{customerId}/accounts` | Idempotent account provisioning for the future Account Opening Workflow |

The exact API is documented in [OpenAPI](docs/openapi.yaml). Responses use snake_case JSON. Transfer lookup always scopes by both customer and transfer ID, so cross-customer attempts receive the same safe `TRANSFER_NOT_FOUND` response as unknown transfers.

## Run locally

Requirements: Java 21, Maven 3.9+, and PostgreSQL 16. Set `DB_URL`, `DB_USERNAME`, and `DB_PASSWORD`, then:

```bash
export INTERNAL_AUTH_DEV_MODE=true
mvn spring-boot:run
```

Development mode bypasses the lightweight internal API-key abstraction and must never be enabled in a shared or production environment. With development mode disabled (the default), set `INTERNAL_AUTH_API_KEY` and send it as `Authorization: Bearer <key>`. This deliberately avoids pretending to be a full OAuth deployment; a real environment should replace the `InternalAuthenticator` implementation with its platform service-identity verifier.

Run the complete stack independently through Docker:

```bash
docker compose -f compose.yml up --build
```

The Compose credentials are local-only defaults. The API listens on `8090`; health is at `/actuator/health`, Prometheus metrics at `/actuator/prometheus`.

## Examples

```bash
curl -H 'X-Request-Id: req-demo-1' -H 'X-Correlation-Id: corr-demo-1' \
  http://localhost:8090/internal/v1/customers/C1024

curl 'http://localhost:8090/internal/v1/customers/C1024/transactions?start_date=2026-08-01&end_date=2026-08-31&limit=20'

curl http://localhost:8090/internal/v1/customers/C1024/transfers/TR4587

curl -X POST http://localhost:8090/internal/v1/customers/C1024/accounts \
  -H 'Content-Type: application/json' \
  -d '{"account_type":"CHECKING","currency":"EUR","opening_id":"OPEN-10001","idempotency_key":"idem-open-10001"}'
```

A safe retry must use the identical path and payload and returns the same account. Reusing either identifier for different customer, type, currency, or companion identifier returns `409 IDEMPOTENCY_KEY_CONFLICT`. Supported demo account types are `CHECKING` and `SAVINGS`; supported currencies are `EUR`, `USD`, and `GBP`.

## Request context, telemetry, and safe logging

The service accepts `X-Request-Id` and `X-Correlation-Id`, generates safe values when missing/invalid, echoes them in response headers, and accepts W3C `traceparent` through Micrometer Tracing/OpenTelemetry. Actuator exposes health and useful HTTP/account-provisioning metrics. Console logs are structured and include identifiers, but application code never logs full customer, account, card, transaction, or transfer objects.

## Development fault injection

Faults are disabled by default. Set `SIMULATOR_FAULTS_ENABLED=true` only in isolated development, then send `X-Simulator-Fault` as `latency`, `error`, `unavailable`, or `malformed`. Latency accepts `X-Simulator-Latency-Ms` and is capped by `SIMULATOR_MAX_LATENCY_MS`. Never enable this mechanism in a shared/production deployment.

## Tests

```bash
mvn test
```

The suite includes JPA repository tests, isolated service tests, MVC controller tests, H2 application integration tests, and a PostgreSQL Testcontainers test (automatically skipped when Docker is unavailable). Coverage includes customer/transfer absence, cross-customer transfer isolation, inclusive transaction date filtering, provisioning success, retry idempotency, conflicting keys, and unsupported types/currencies.

See [architecture](docs/architecture.md) and [seed data](docs/seed-data.md).

