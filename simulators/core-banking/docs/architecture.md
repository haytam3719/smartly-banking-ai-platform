# Architecture

```text
Future Domain Agents / Account Opening Workflow
                    ↓ internal HTTP
 Authentication → request/trace context → fault hook (disabled by default)
                    ↓
             REST controllers
                    ↓
       transactional domain service
                    ↓
        Spring Data JPA repositories
                    ↓
       PostgreSQL schema owned by Flyway
```

The simulator is an internal deterministic system adapter, not an AI service. Controllers handle transport and validation. `CoreBankingService` enforces customer existence, ownership, date boundaries, supported provisioning inputs, and idempotency. Repositories express customer-scoped queries rather than loading an object first and checking ownership later. Flyway owns both schema and deterministic seed revisions; Hibernate validates but never mutates the schema.

The account-opening endpoint is intentionally narrow. Its trusted path customer is recorded with the opening ID, idempotency key, type, currency, and resulting account. Either unique identifier can safely locate a retry; every recorded input must match before the same account is returned. It has no loan or credit decision behavior.

Security is represented by a replaceable `InternalAuthenticator`. Local development can explicitly bypass it; normal mode uses a configured bearer secret as a lightweight stand-in for platform service identity. Real deployments should substitute their existing workload identity validation, encrypted transport, network policy, and secret management rather than extending this simulator with fake OAuth infrastructure.

Micrometer instruments request duration/status and provisioning outcomes. The OpenTelemetry tracing bridge consumes and propagates W3C trace context. Logs contain operational identifiers and exception classes, not indiscriminate serialized banking entities or stack traces in API responses.

