# Mobile BFF

Reactive Spring WebFlux Backend-for-Frontend for Android and iOS clients:

```text
Android / iOS -> Mobile BFF -> AI Orchestrator
```

It contains no AI routing, RAG, agent selection, or banking business logic. It authenticates the mobile request, binds the trusted customer context, adds minimal channel context, and maps the orchestrator response through a safe allowlist.

## APIs

- `POST /chat` — technical-challenge compatible
- `POST /api/mobile/v1/chat`
- `GET /actuator/health`
- `GET /actuator/prometheus`

```bash
curl -X POST http://localhost:8080/chat \
  -H 'Content-Type: application/json' \
  -H 'X-Request-Id: req-mobile-1' \
  -H 'X-Correlation-Id: corr-mobile-1' \
  -H 'X-Demo-Subject-Id: user-123' \
  -H 'X-Demo-Customer-Id: C1024' \
  -H 'X-App-Version: 2.4.1' \
  -H 'X-Device-Class: PHONE' \
  -d '{"customer_id":"C1024","message":"Quel est mon solde ?","locale":"fr-FR"}'
```

The BFF calls `POST {AI_ORCHESTRATOR_URL}/api/v1/chat`. It forwards the shared request body unchanged except for a default `fr-FR` locale. Channel and trust enrichment use headers: `X-Channel=MOBILE`, authenticated subject/customer, scopes, app version, coarse device class, request/correlation/conversation IDs, and W3C `traceparent`. It never forwards raw user-agent strings, device identifiers, advertising identifiers, or other device-sensitive data.

## Authentication boundary

`AuthenticationPort` separates channel authentication from request handling. Demo mode (`MOBILE_AUTH_DEMO_MODE=true`) accepts documented `X-Demo-*` headers and falls back to the challenge body customer ID. This is local development behavior only.

Production must set `MOBILE_AUTH_DEMO_MODE=false` and replace/place the header adapter behind a trusted token/session authentication gateway. The body `customer_id` is then only a compatibility claim and must match the authenticated session customer. Direct, untrusted clients must never be allowed to forge the upstream identity headers.

## Resilience and security

Netty enforces strict connection and response timeouts. Resilience4j permits at most the configured bounded attempts for the current read-only chat operation, transport failures, timeouts, and HTTP 5xx. It does not retry 4xx. Future mutation/workflow APIs must use a separate non-retrying client unless their idempotency contract is explicit.

Responses preserve `answer`, `source`, `sources`, `conversation_id`, and `request_id`. Unknown top-level fields and sensitive error/internal URL keys inside evidence are discarded. Downstream bodies and stack traces are never returned in errors.

Configuration:

- `AI_ORCHESTRATOR_URL`
- `ORCHESTRATOR_CONNECT_TIMEOUT` (default `500ms`)
- `ORCHESTRATOR_READ_TIMEOUT` (default `30s`)
- `ORCHESTRATOR_RETRY_ATTEMPTS` (default `2`)
- `MOBILE_AUTH_DEMO_MODE` (must be `false` in production)
- standard Micrometer/OpenTelemetry configuration

## Build and test

```bash
mvn test
mvn spring-boot:run
docker build -t smartly-mobile-bff .
```

Tests use WireMock and cover both routes, validation, timeouts, HTTP 500, bounded retries, request/authentication/trace context, minimal device enrichment, safe response mapping, error redaction, and cross-customer isolation. Testcontainers is not used because this stateless BFF has no database or container-dependent integration boundary.

Streaming is intentionally deferred. A future `/chat/stream` endpoint should define cancellation, backpressure, authentication lifetime, and partial-error semantics before implementation.
