from __future__ import annotations

import os
from contextlib import asynccontextmanager
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from agent_registry.api import RegistryNotFound, router
from agent_registry.health import AgentHealthService
from agent_registry.logging_config import configure_logging, correlation_id_var, request_id_var
from agent_registry.models import ErrorResponse
from agent_registry.repository import YamlAgentRepository

configure_logging()


def create_app(config_path: Path | None = None) -> FastAPI:
    resolved_path = config_path or Path(os.getenv("AGENT_REGISTRY_CONFIG", "config/agents.yaml"))

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        repo = YamlAgentRepository.load(resolved_path)
        app.state.repository = repo
        app.state.health_service = AgentHealthService(repo.config.health_probing)
        yield

    application = FastAPI(title="Smartly Agent Registry", version="1.0.0", description="Capability discovery for domain agents; contains no AI.", lifespan=lifespan)
    application.include_router(router)

    @application.middleware("http")
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

    @application.exception_handler(RegistryNotFound)
    async def not_found(request: Request, exc: RegistryNotFound) -> JSONResponse:
        body = ErrorResponse(code=exc.code, message=exc.message, request_id=request_id_var.get(), retryable=False)
        return JSONResponse(status_code=404, content=body.model_dump())

    @application.get("/health", include_in_schema=False)
    async def health() -> dict[str, str]:
        return {"status": "UP"}

    return application


def _safe_id(value: str | None) -> str | None:
    if value and len(value) <= 128 and all(character.isalnum() or character in "._:-" for character in value):
        return value
    return None


app = create_app()

