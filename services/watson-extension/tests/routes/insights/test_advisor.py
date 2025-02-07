import pytest
from quart.typing import TestClientProtocol
from ..common import app_with_blueprint

from watson_extension.routes.insights.advisor import blueprint

@pytest.fixture
async def test_client() -> TestClientProtocol:
    return app_with_blueprint(blueprint).test_client()


async def test_recommendations(test_client) -> None:
    response = await test_client.get("/advisor/recommendations", query_string={"category": "performance"})
    assert response.status == "200 OK"
    data = await response.get_json()
    assert data["response"].startswith("Here are your top recommendations from advisor")
