import enum
from typing import Optional

import injector
from pydantic import BaseModel

from quart import Blueprint, render_template
from quart_schema import validate_response, validate_querystring

from watson_extension.clients.insights.advisor import AdvisorClient, FindRuleSort

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
async def recommendations(query_args: RecommendationsRequestQuery, advisor_client: injector.Inject[AdvisorClient]) -> RecommendationsResponse:
    category_id: Optional[str] = None
    sort: Optional[FindRuleSort] = None
    total_risk: Optional[int] = None
    only_workloads: Optional[bool] = None
    if query_args.category in {RecommendationCategory.SECURITY, RecommendationCategory.STABILITY, RecommendationCategory.AVAILABILITY, RecommendationCategory.PERFORMANCE}:
        category = await advisor_client.find_rule_category_by_name(query_args.category.value)
        category_id = category.id
        sort = FindRuleSort.TotalRisk
    elif query_args.category is RecommendationCategory.NEW:
        sort = FindRuleSort.PublishDate
    elif query_args.category is RecommendationCategory.CRITICAL:
        total_risk = 4
    elif query_args.category is RecommendationCategory.WORKLOAD:
        only_workloads = True

    rules_response = await advisor_client.find_rules(category_id=category_id, total_risk=total_risk, sort=sort, only_workloads=only_workloads)
    return RecommendationsResponse(
        response=await render_template(
            'insights/advisor/recommendations.txt.jinja',
            rules=rules_response.rules,
            dashboard_link=rules_response.link,
            category=query_args.category.value
        )
    )
