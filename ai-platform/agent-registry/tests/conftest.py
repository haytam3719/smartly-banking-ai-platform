from __future__ import annotations

from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient

from agent_registry.main import create_app


@pytest.fixture
async def app_client():
    app = create_app(Path("config/agents.yaml"))
    async with app.router.lifespan_context(app):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            yield app, client

