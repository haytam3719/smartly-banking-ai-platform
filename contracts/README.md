# Shared contracts

This directory is the source of truth for inter-service shapes. `schemas/` contains Draft 2020-12 JSON Schemas, `events/` contains versioned event schemas, and `openapi/` is reserved for future service API descriptions.

Changes require consumer review and contract tests. Do not weaken capability enums to arbitrary strings. Public examples containing `customer_id` are challenge compatibility only; production gateways must derive the effective customer from authenticated claims.

