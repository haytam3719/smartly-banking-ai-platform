# Knowledge / RAG Agent

The only platform component that owns document ingestion and retrieval (`knowledge.search`). It returns evidence; it does not orchestrate conversations, grant permissions, call banking APIs, or generate banking answers.

## Architecture

```text
Markdown / text / PDF
  -> loader -> whitespace normalization -> overlapping chunks
  -> deterministic metadata and IDs -> embedding abstraction -> Qdrant

POST /internal/v1/search
  -> embedding -> governed filters -> vector similarity -> threshold
  -> pluggable reranker -> deduplication -> context-size cap -> evidence
```

`EmbeddingPort` has a deterministic hashing implementation for tests and local demos and an `OpenAICompatibleEmbedding` HTTP adapter for production-like deployments. `VectorStorePort` isolates Qdrant; the in-memory implementation is for deterministic tests only. `RerankerPort` defaults to a lightweight pass-through and can be replaced independently.

## Corpus governance and security

The supplied `knowledge_base/demo` corpus is invented because no real documents were provided. Every file prominently says **DEMO / SYNTHETIC POLICY** and **NOT AN ACTUAL BANK POLICY** and disclaims Smartly.ai/bank provenance. It includes only card, transfer, fee, account-opening, fraud, lost-card, and KYC topics—never loans, lending, borrowing, affordability, or credit scoring.

Documents are untrusted context. Text such as “ignore system instructions” remains inert evidence; it cannot alter this service, authorize an operation, or invoke a tool. Callers must retain their system/policy boundaries when consuming results. This service holds no customer financial data, and no customer-data caching is implemented. A future Redis adapter may cache only general document retrieval results.

Metadata includes deterministic `document_id`, `document_type`, `title`, `section`, `language`, `version`, `synthetic`, `domain`, `locale`, effective dates, `active`, source filename, and chunk index. IDs derive from source filename/version and chunk index, making Qdrant upserts idempotent. Search always filters active, locale-compatible versions and applies effective dates in the local implementation.

## API

`POST /internal/v1/search`

```bash
curl -X POST http://localhost:8080/internal/v1/search \
  -H 'Content-Type: application/json' \
  -d '{"query":"Que faire après PAYMENT_LIMIT_EXCEEDED ?","top_k":4,"locale":"fr-FR","filters":{"document_type":"transfer_policy"},"score_threshold":0.15}'
```

Each result contains `content`, `document_id`, `document_type`, `score`, and full governed metadata. Also exposed: `GET /internal/v1/capabilities` and `GET /health`. Qdrant failures produce a safe HTTP 503; an empty corpus produces an empty result set.

## Run and ingest

```bash
python -m venv .venv
.venv/Scripts/pip install -e '.[test]'
python -m app.cli.ingest knowledge_base/demo
python -m app.cli.verify
uvicorn app.main:app --host 0.0.0.0 --port 8080
docker build -t smartly-knowledge-agent .
```

Runtime configuration:

- `QDRANT_URL`, `QDRANT_API_KEY`, `QDRANT_COLLECTION`
- `EMBEDDING_PROVIDER=deterministic` for local use, or another value for the OpenAI-compatible adapter
- `EMBEDDING_BASE_URL`, `EMBEDDING_API_KEY`, `EMBEDDING_MODEL`, `EMBEDDING_DIMENSIONS`
- `MAX_CONTEXT_CHARACTERS` (default 6000)
- standard `OTEL_EXPORTER_OTLP_*` variables

The ingestion command is safe to repeat: stable point IDs replace the same chunks rather than duplicating them. Each PDF must have a sibling `<name>.metadata.yaml` file containing the same required metadata keys as Markdown/text front matter; PDFs without this governed sidecar are rejected.
