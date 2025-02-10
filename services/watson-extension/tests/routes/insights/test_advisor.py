from unittest.mock import MagicMock

import injector
import pytest
from quart.typing import TestClientProtocol

from watson_extension.clients.insights.advisor import RuleCategory, AdvisorClient, FindRulesResponse, Rule
from ..common import app_with_blueprint

from watson_extension.routes.insights.advisor import blueprint
from ... import async_value, get_test_template


@pytest.fixture
async def advisor_client() -> MagicMock:
    return MagicMock(AdvisorClient)


@pytest.fixture
async def test_client(advisor_client) -> TestClientProtocol:
    def injector_binder(binder: injector.Binder):
        binder.bind(AdvisorClient, advisor_client)

    return app_with_blueprint(blueprint, injector_binder).test_client()

async def test_recommendations(test_client, advisor_client) -> None:
    advisor_client.find_rule_category_by_name = MagicMock(return_value=async_value(RuleCategory(id="4", name="performance")))
    advisor_client.find_rules = MagicMock(return_value=async_value(FindRulesResponse(
        rules=[
            Rule(
                id="3",
                description="I am a rule",
                link="I am link",
            ),
        ],
        link="i-am-not-zelda"
    )))


    response = await test_client.get("/advisor/recommendations", query_string={"category": "performance"})
    assert response.status == "200 OK"
    data = await response.get_json()
    assert data["response"] == get_test_template("insights/advisor/recommendations.txt")

async def test_recommendations_none(test_client, advisor_client) -> None:
    advisor_client.find_rule_category_by_name = MagicMock(return_value=async_value(RuleCategory(id="4", name="performance")))
    advisor_client.find_rules = MagicMock(return_value=async_value(FindRulesResponse(
        rules=[],
        link="i-am-not-zelda"
    )))

    response = await test_client.get("/advisor/recommendations", query_string={"category": "performance"})
    assert response.status == "200 OK"
    data = await response.get_json()
    assert data["response"] == get_test_template("insights/advisor/recommendations-not-found.txt")
