import os
from contextlib import asynccontextmanager
from uuid import uuid4
import httpx
from fastapi import FastAPI, Request
from fastapi.responses import Response
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from transfer_agent.adapters import CoreBankingTransferAdapter
from transfer_agent.api import router
from transfer_agent.logging_config import configure_logging, correlation_id_var, request_id_var
from transfer_agent.service import TransferCapabilityService
from transfer_agent.telemetry import configure_tracing

configure_logging(); configure_tracing(); HTTPXClientInstrumentor().instrument()
@asynccontextmanager
async def lifespan(app: FastAPI):
    seconds = float(os.getenv("CORE_BANKING_TIMEOUT_SECONDS", "0.8"))
    timeout = httpx.Timeout(seconds, connect=seconds, read=seconds, write=seconds, pool=seconds)
    async with httpx.AsyncClient(timeout=timeout) as client:
        app.state.service = TransferCapabilityService(CoreBankingTransferAdapter(client, os.getenv("CORE_BANKING_URL", "http://core-banking:8090"), os.getenv("CORE_BANKING_API_KEY")))
        yield
app = FastAPI(title="Smartly Transfer Agent", version="1.0.0", description="Customer-scoped transfer status boundary; no AI decisions.", lifespan=lifespan)
app.include_router(router)
@app.middleware("http")
async def context(request: Request, call_next):
    request_id = _safe(request.headers.get("X-Request-Id")) or str(uuid4())
    correlation_id = _safe(request.headers.get("X-Correlation-Id")) or request_id
    a = request_id_var.set(request_id); b = correlation_id_var.set(correlation_id)
    try:
        response = await call_next(request); response.headers["X-Request-Id"] = request_id; response.headers["X-Correlation-Id"] = correlation_id; return response
    finally: request_id_var.reset(a); correlation_id_var.reset(b)
@app.get("/metrics", include_in_schema=False)
async def metrics() -> Response: return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
def _safe(value): return value if value and len(value) <= 128 and all(c.isalnum() or c in "._:-" for c in value) else None
FastAPIInstrumentor.instrument_app(app, excluded_urls="/health,/metrics")
