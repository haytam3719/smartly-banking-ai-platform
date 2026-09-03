from prometheus_client import Counter,Histogram
CAPABILITY_LATENCY=Histogram("card_agent_capability_latency_seconds","Card capability execution latency",["outcome"])
DOWNSTREAM_ERRORS=Counter("card_agent_downstream_errors_total","Core banking downstream failures",["kind"])

