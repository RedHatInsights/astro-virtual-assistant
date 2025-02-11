import pytest
from quart.typing import TestClientProtocol
from tests.routes.common import app_with_blueprint

from virtual_assistant.routes.health import blueprint


@pytest.fixture
async def test_client() -> TestClientProtocol:
    return app_with_blueprint(blueprint).test_client()


async def test_status(test_client) -> None:
    response = await test_client.get("/health/status")
    assert response.status == "200 OK"
    data = await response.get_json()
    assert data == {"status": "ok"}
