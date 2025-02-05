import enum

from pydantic import BaseModel

from quart import Blueprint, render_template
from quart_schema import validate_response, validate_querystring

blueprint = Blueprint("advisor", __name__, url_prefix="/advisor")

class RecommendationCategory(enum.Enum):
    """
    Categories to group different searching queries for rhel advisor recommendations
    """
    PERFORMANCE = "performance"
    SECURITY = "security"
    AVAILABILITY = "availability"
    STABILITY = "stability"
    NEW = "new"
    CRITICAL = "critical"
    WORKLOAD = "workload"


class RecommendationsRequestQuery(BaseModel):
    category: RecommendationCategory

class RecommendationsResponse(BaseModel):
    response: str

@blueprint.get("/recommendations")
@validate_querystring(RecommendationsRequestQuery)
@validate_response(RecommendationsResponse)
async def recommendations(query_args: RecommendationsRequestQuery) -> RecommendationsResponse:
    try:
        res = RecommendationsResponse(
            response=await render_template('insights/advisor/recommendations.txt')
        )
    except Exception as e:
        print(e)

    return res
