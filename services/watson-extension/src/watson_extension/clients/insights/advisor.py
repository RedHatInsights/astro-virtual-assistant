import abc
import enum
from dataclasses import dataclass
from typing import Optional, List

import injector

from watson_extension.clients import AdvisorURL
from watson_extension.clients.identity import UserIdentity
from watson_extension.clients.platform_request import PlatformRequest

@dataclass
class RuleCategory:
    id: str
    name: str

@dataclass
class Rule:
    id: str
    description: str
    link: str

@dataclass
class FindRulesResponse:
    rules: List[Rule]
    link: str

class FindRuleSort(enum.Enum):
    PublishDate = "-publish_date"
    TotalRisk = "-total_risk"

class AdvisorClient(abc.ABC):
    @abc.abstractmethod
    async def find_rule_category_by_name(self, category_name: str) -> RuleCategory: ...

    @abc.abstractmethod
    async def find_rules(self, category_id: Optional[str] = None, total_risk: Optional[int] = None, sort: Optional[FindRuleSort] = None, only_workloads: Optional[bool] = None) -> FindRulesResponse: ...


class AdvisorClientHttp(AdvisorClient):
    def __init__(self, advisor_url: injector.Inject[AdvisorURL], user_identity: injector.Inject[UserIdentity], platform_request: injector.Inject[PlatformRequest]):
        super().__init__()
        self.advisor_url = advisor_url
        self.user_identity = user_identity
        self.platform_request = platform_request

    async def find_rule_category_by_name(self, category_name: str) -> RuleCategory:
        response = await self.platform_request.get(self.advisor_url, "/api/insights/v1/rulecategory/", user_identity=self.user_identity)
        response.raise_for_status()

        content = await response.json()

        for category in content:
            if category["name"].lower() == category_name.lower():
                return RuleCategory(
                    id=category["id"],
                    name=category["name"]
                )

        raise ValueError(f"{category_name} was not found in advisor rules.")

    async def find_rules(self, category_id: Optional[str] = None, total_risk: Optional[int] = None, sort: Optional[FindRuleSort] = None,
                         only_workloads: Optional[bool] = None) -> FindRulesResponse:
        query = "impacting=true&rule_status=enabled"
        if category_id is not None:
            query += f"&category={category_id}"

        if total_risk is not None:
            query += f"&total_risk={total_risk}"

        if sort is not None:
            query += f"&sort={sort.value}"

        if only_workloads is not None:
            query += f"&filter[system_profile][sap_system]={str(only_workloads).lower()}"

        request = f"/api/insights/v1/rule?{query}&limit=3"
        response = await self.platform_request.get(self.advisor_url, request, user_identity=self.user_identity)
        response.raise_for_status()

        content = await response.json()

        rules = [Rule(
            id=r["rule_id"],
            description=r["description"],
            link=f"/insights/advisor/recommendations/{r['rule_id']}"
        ) for r in content["data"]]

        dashboard_link = f"/insights/advisor/recommendations?{query}"

        return FindRulesResponse(
            rules=rules,
            link=dashboard_link,
        )
