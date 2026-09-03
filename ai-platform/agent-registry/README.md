# Agent Registry

A lightweight capability directory for the Smartly AI platform. It lets the AI Orchestrator resolve `transfer.status.read` to the enabled Transfer Agent without embedding service URLs in orchestration code.

This is capability discovery, not an AI component: it runs no model, prompt, embedding, RAG, routing inference, or authorization logic. It is also not a replacement for Kubernetes DNS, service meshes, or general-purpose service discovery. The resolved `base_url` is the stable platform endpoint supplied by local configuration; the runtime platform remains responsible for locating instances behind that endpoint.

## APIs

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/internal/v1/agents` | List complete registered definitions, including disabled entries |
| GET | `/internal/v1/agents/{agentId}` | Inspect one definition |
| GET | `/internal/v1/capabilities/{capability}` | Resolve an enabled owner for orchestration |
| GET | `/internal/v1/health/agents` | Report independent availability metadata |
| GET | `/health` | Registry process health |

Capability resolution returns only capability, agent ID, base URL, version, and timeout. Unknown capabilities and capabilities owned only by disabled agents return a safe `404 CAPABILITY_NOT_FOUND`.

## Configuration and validation

[config/agents.yaml](config/agents.yaml) registers Account, Card, Transfer, Customer, Knowledge, and Account Opening Workflow services. Configuration is loaded and validated atomically at startup. URLs must be HTTP(S), IDs and semantic versions are constrained, capabilities use the canonical enum, and timeouts are bounded.

Duplicate capability ownership is rejected unless `allow_duplicate_capabilities: true` is explicitly set. In that opt-in mode, the enabled agent with highest `priority` wins deterministically, with ID as a stable tie-breaker. This supports controlled migration/failover without making the registry a load balancer.

Set `AGENT_REGISTRY_CONFIG` to load a different YAML file. Configuration changes require a restart so every request sees one immutable validated snapshot.

## Health probing

Health probing is disabled by default. Enable it in YAML under `health_probing` with a bounded timeout and safe relative path. The registry checks enabled agents concurrently. A failed, timed-out, or non-2xx agent is marked `UNAVAILABLE`; other agents remain available and the endpoint returns HTTP 200 with overall `DEGRADED`. Disabled agents are reported as `DISABLED` without network traffic. This metadata is advisory—the orchestrator still needs deadlines and failure handling.

## Run

Python 3.12:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[test]'
uvicorn agent_registry.main:app --host 0.0.0.0 --port 8082
```

On Windows use `.venv\Scripts\Activate.ps1`. Docker:

```bash
docker build -t smartly-agent-registry .
docker run --rm -p 8082:8082 smartly-agent-registry
```

## Examples

```bash
curl http://localhost:8082/internal/v1/agents
curl http://localhost:8082/internal/v1/agents/transfer-agent
curl http://localhost:8082/internal/v1/capabilities/transfer.status.read
curl http://localhost:8082/internal/v1/health/agents
```

Logs are structured JSON and include request/correlation identifiers. Resolution logs contain capability and agent ID only, not prompts, customer data, or banking payloads.

Run tests with `pytest`. The suite covers capability resolution, unknown capabilities, disabled agents, duplicate ownership and explicit priority, malformed configuration/URLs, and isolated health-probe behavior.

