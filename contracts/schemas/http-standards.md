# Internal HTTP standards

Every service must accept and propagate these headers:

| Header | Purpose |
| --- | --- |
| `Authorization` | Caller credential; never log its value or blindly forward end-user tokens beyond their intended audience. |
| `X-Request-Id` | Unique identifier for one HTTP request/hop; create when absent at a trusted edge. |
| `X-Correlation-Id` | Stable identifier joining calls and events for one business interaction. |
| `X-Conversation-Id` | Conversation state identifier, when relevant. |
| `traceparent` | W3C Trace Context propagated by instrumentation. |

Services validate identifier syntax and length, preserve correlation and trace context, and generate a new request ID for each outbound hop while linking it to the inbound context. Trust boundaries must prevent untrusted callers from forging privileged trace baggage or identity. The effective customer identity comes from verified authentication claims in production; the challenge's request `customer_id` is never sufficient authorization.

Errors use `error-response.schema.json`, map to suitable HTTP statuses, and contain only safe messages. Stack traces, internal hostnames, query text, credentials, and implementation details remain in access-controlled telemetry and never appear in an API response.

