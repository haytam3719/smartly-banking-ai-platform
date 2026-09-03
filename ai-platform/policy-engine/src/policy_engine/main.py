from __future__ import annotations

from uuid import uuid4

from fastapi import FastAPI, Request
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

from policy_engine.api import router
from policy_engine.logging_config import configure_logging, correlation_id_var, request_id_var
from policy_engine.telemetry import configure_tracing

configure_logging()
configure_tracing()

app = FastAPI(
    title="Smartly Policy Engine",
    version="1.0.0",
    description="Deterministic authorization boundary. This service contains no AI.",
)
app.include_router(router)


@app.middleware("http")
async def request_context(request: Request, call_next):
    request_id = _safe_id(request.headers.get("X-Request-Id")) or str(uuid4())
    correlation_id = _safe_id(request.headers.get("X-Correlation-Id")) or request_id
    request_token = request_id_var.set(request_id)
    correlation_token = correlation_id_var.set(correlation_id)
    try:
        response = await call_next(request)
        response.headers["X-Request-Id"] = request_id
        response.headers["X-Correlation-Id"] = correlation_id
        return response
    finally:
        request_id_var.reset(request_token)
        correlation_id_var.reset(correlation_token)


def _safe_id(value: str | None) -> str | None:
    if value and len(value) <= 128 and all(character.isalnum() or character in "._:-" for character in value):
        return value
    return None


FastAPIInstrumentor.instrument_app(app, excluded_urls="/health")

