import enum
from typing import Optional

import injector

from watson_extension.clients.insights.advisor import AdvisorClient, FindRuleSort


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


class AdvisorCore:
    def __init__(self, advisor_client: injector.Inject[AdvisorClient]):
        self.advisor_client = advisor_client

    async def get_recommendations(self, category_type: RecommendationCategory):
        category_name = category_type.value
        category_id: Optional[str] = None
        sort: Optional[FindRuleSort] = None
        total_risk: Optional[int] = None
        only_workloads: Optional[bool] = None

        if category_type in {
            RecommendationCategory.SECURITY,
            RecommendationCategory.STABILITY,
            RecommendationCategory.AVAILABILITY,
            RecommendationCategory.PERFORMANCE,
        }:
            category = await self.advisor_client.find_rule_category_by_name(
                category_name
            )
            category_id = category.id
            sort = FindRuleSort.TotalRisk
        elif category_type is RecommendationCategory.NEW:
            sort = FindRuleSort.PublishDate
        elif category_type is RecommendationCategory.CRITICAL:
            total_risk = 4
        elif category_type is RecommendationCategory.WORKLOAD:
            only_workloads = True

        return await self.advisor_client.find_rules(
            category_id=category_id,
            total_risk=total_risk,
            sort=sort,
            only_workloads=only_workloads,
        )
