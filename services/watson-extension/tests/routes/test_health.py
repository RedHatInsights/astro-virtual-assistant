import pytest
from quart import Quart
from quart_schema import QuartSchema

from routes.health import blueprint

@pytest.fixture
async def app() -> Quart:
    app = Quart(__name__)
    app.register_blueprint(blueprint)
    QuartSchema(app)
    return app

async def test_status(app) -> None:
    test_client = app.test_client()
    response = await test_client.get("/health/status")
    assert response.status == '200 OK'
    data = await response.get_json()
    assert data == {"status": "ok"}
