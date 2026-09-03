from __future__ import annotations

import contextvars
import logging
import sys

from opentelemetry import trace
from pythonjsonlogger.json import JsonFormatter

request_id_var: contextvars.ContextVar[str] = contextvars.ContextVar("request_id", default="")
correlation_id_var: contextvars.ContextVar[str] = contextvars.ContextVar("correlation_id", default="")


class ContextFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.service = "policy-engine"
        record.request_id = request_id_var.get()
        record.correlation_id = correlation_id_var.get()
        span_context = trace.get_current_span().get_span_context()
        record.trace_id = f"{span_context.trace_id:032x}" if span_context.is_valid else ""
        return True


def configure_logging() -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.addFilter(ContextFilter())
    handler.setFormatter(
        JsonFormatter(
            "%(asctime)s %(levelname)s %(service)s %(name)s %(message)s %(request_id)s %(correlation_id)s %(trace_id)s",
            rename_fields={"asctime": "timestamp", "levelname": "level", "name": "logger"},
        )
    )
    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(logging.INFO)

