from prometheus_client import Counter, Histogram
CAPABILITY_LATENCY = Histogram("customer_agent_capability_duration_seconds", "Customer capability latency", ["outcome"])
DOWNSTREAM_ERRORS = Counter("customer_agent_downstream_errors_total", "Core banking errors", ["kind"])
