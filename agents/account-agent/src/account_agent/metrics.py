from prometheus_client import Counter, Histogram

CAPABILITY_LATENCY = Histogram(
    "account_agent_capability_latency_seconds",
    "Account capability execution latency",
    ["capability", "outcome"],
)
DOWNSTREAM_ERRORS = Counter(
    "account_agent_downstream_errors_total",
    "Core banking downstream failures",
    ["kind"],
)

