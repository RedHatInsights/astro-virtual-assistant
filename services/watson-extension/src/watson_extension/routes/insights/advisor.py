import injector
from pydantic import BaseModel

from quart import Blueprint, render_template
from quart_schema import validate_response, validate_querystring

from watson_extension.core.insights.advisor import (
    RecommendationCategory,
    AdvisorCore,
)

blueprint = Blueprint("advisor", __name__, url_prefix="/advisor")

class RecommendationsRequestQuery(BaseModel):
    category: RecommendationCategory

class RecommendationsResponse(BaseModel):
    response: str

@blueprint.get("/recommendations")
@validate_querystring(RecommendationsRequestQuery)
@validate_response(RecommendationsResponse)
async def recommendations(query_args: RecommendationsRequestQuery, advisor_service: injector.Inject[AdvisorCore]) -> RecommendationsResponse:
    rules_response = await advisor_service.get_recommendations(query_args.category)

    return RecommendationsResponse(
        response=await render_template(
            'insights/advisor/recommendations.txt.jinja',
            rules=rules_response.rules,
            dashboard_link=rules_response.link,
            category=query_args.category.value
        )
    )
