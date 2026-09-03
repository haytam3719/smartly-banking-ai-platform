from prometheus_client import Counter, Histogram
CAPABILITY_LATENCY = Histogram("transfer_agent_capability_duration_seconds", "Transfer capability latency", ["outcome"])
DOWNSTREAM_ERRORS = Counter("transfer_agent_downstream_errors_total", "Core banking errors", ["kind"])
