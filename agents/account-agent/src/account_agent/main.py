from __future__ import annotations

import os
from contextlib import asynccontextmanager
from uuid import uuid4

import httpx
from fastapi import FastAPI, Request
from fastapi.responses import Response
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from account_agent.adapters import CoreBankingAccountAdapter
from account_agent.api import router
from account_agent.logging_config import configure_logging, correlation_id_var, request_id_var
from account_agent.service import AccountCapabilityService
from account_agent.telemetry import configure_tracing

configure_logging()
configure_tracing()
HTTPXClientInstrumentor().instrument()


@asynccontextmanager
async def lifespan(app: FastAPI):
    timeout_seconds = float(os.getenv("CORE_BANKING_TIMEOUT_SECONDS", "0.8"))
    timeout = httpx.Timeout(timeout_seconds, connect=timeout_seconds, read=timeout_seconds, write=timeout_seconds, pool=timeout_seconds)
    async with httpx.AsyncClient(timeout=timeout) as client:
        adapter = CoreBankingAccountAdapter(client, os.getenv("CORE_BANKING_URL", "http://core-banking:8090"), os.getenv("CORE_BANKING_API_KEY"))
        app.state.service = AccountCapabilityService(adapter)
        yield


app = FastAPI(title="Smartly Account Agent", version="1.0.0", description="Account capability boundary; no AI decisions.", lifespan=lifespan)
app.include_router(router)


@app.middleware("http")
async def request_context(request: Request, call_next):
    request_id = _safe_id(request.headers.get("X-Request-Id")) or str(uuid4())
    correlation_id = _safe_id(request.headers.get("X-Correlation-Id")) or request_id
    request_token = request_id_var.set(request_id); correlation_token = correlation_id_var.set(correlation_id)
    try:
        response = await call_next(request)
        response.headers["X-Request-Id"] = request_id; response.headers["X-Correlation-Id"] = correlation_id
        return response
    finally:
        request_id_var.reset(request_token); correlation_id_var.reset(correlation_token)


@app.get("/metrics", include_in_schema=False)
async def metrics() -> Response:
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


def _safe_id(value: str | None) -> str | None:
    return value if value and len(value) <= 128 and all(character.isalnum() or character in "._:-" for character in value) else None


FastAPIInstrumentor.instrument_app(app, excluded_urls="/health,/metrics")

