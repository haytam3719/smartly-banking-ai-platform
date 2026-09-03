# Event contracts

Events use a common envelope and an event-name version suffix. Producers set UTC RFC 3339 timestamps and globally unique event IDs. Consumers validate schemas, deduplicate by `event_id`, and tolerate additive compatible changes. Breaking changes require a new event version.

`conversation_id` is required on conversational AI events. Payloads contain opaque identifiers, controlled enums/codes, counts, and timings—not raw prompts, model answers, credentials, unnecessary customer attributes, or document excerpts. Access to event topics is least-privilege and retention is purpose-limited.
