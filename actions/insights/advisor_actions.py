# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions

from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, ActiveLoop
from rasa_sdk.types import DomainDict

from actions.actions import all_required_slots_are_set
from actions.slot_match import FuzzySlotMatch, FuzzySlotMatchOption, resolve_slot_match
from common import logging
from common.metrics import flow_started_count, Flow, flow_finished_count
from common.requests import send_console_request

logger = logging.initialize_logging()

CATEGORY_PERFORMANCE = "performance"
CATEGORY_SECURITY = "security"
CATEGORY_AVAILABILITY = "availability"
CATEGORY_STABILITY = "stability"
CATEGORY_NEW = "new"
CATEGORY_CRITICAL = "critical"
CATEGORY_WORKLOADS = "workload"

advisor_categories = FuzzySlotMatch(
    "insights_advisor_recommendation_category",
    [
        FuzzySlotMatchOption(CATEGORY_PERFORMANCE),
        FuzzySlotMatchOption(CATEGORY_SECURITY),
        FuzzySlotMatchOption(CATEGORY_AVAILABILITY),
        FuzzySlotMatchOption(CATEGORY_STABILITY),
        FuzzySlotMatchOption(
            CATEGORY_NEW, [CATEGORY_NEW, "recent", "recently", "newest"]
        ),
        FuzzySlotMatchOption(CATEGORY_CRITICAL),
        FuzzySlotMatchOption(CATEGORY_WORKLOADS),
    ],
)

OPENSHIFT_CATEGORY_RECOMMENDATION = "recommendation"
OPENSHIFT_CATEGORY_CLUSTER = "cluster"
OPENSHIFT_CATEGORY_WORKLOAD = "workload"

advisor_openshift_categories = FuzzySlotMatch(
    "insights_openshift_advisor_category",
    [
        FuzzySlotMatchOption(OPENSHIFT_CATEGORY_RECOMMENDATION),
        FuzzySlotMatchOption(OPENSHIFT_CATEGORY_CLUSTER),
        FuzzySlotMatchOption(OPENSHIFT_CATEGORY_WORKLOAD),
    ],
)

advisor_system = FuzzySlotMatch(
    "insights_advisor_system_kind",
    [
        FuzzySlotMatchOption("rhel", ["rhel", "enterprise", "linux"]),
        FuzzySlotMatchOption("openshift"),
    ],
)


class AdvisorRecommendationByCategoryInit(Action):

    def name(self) -> Text:
        return "form_insights_advisor_recommendation_by_category_init"

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[Dict[Text, Any]]:
        flow_started_count(Flow.ADVISOR)
        return [
            SlotSet("insights_advisor_system_kind"),
            SlotSet("insights_advisor_recommendation_category"),
            SlotSet("insights_openshift_advisor_category"),
        ]


class AdvisorUpdateRisk(Action):

    def name(self) -> Text:
        return "form_insights_advisor_update_risk"

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[Dict[Text, Any]]:
        flow_started_count(Flow.ADVISOR)
        return [
            SlotSet("insights_advisor_system_kind", "openshift"),
            SlotSet("insights_advisor_recommendation_category"),
            SlotSet("insights_openshift_advisor_category", OPENSHIFT_CATEGORY_CLUSTER),
        ]


class AdvisorRecommendationByType(FormValidationAction):

    filter_query = "impacting=true&rule_status=enabled"

    def name(self) -> Text:
        return "validate_form_insights_advisor_recommendation_by_category"

    async def extract_insights_advisor_system_kind(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict
    ) -> Dict[Text, Any]:
        requested_slot = tracker.get_slot("requested_slot")
        user_input = tracker.latest_message["text"]

        if requested_slot == "insights_advisor_system_kind":
            resolved = self.resolve_advisor_system_kind(user_input)
            if len(resolved) > 0:
                return resolved

        if (
            requested_slot is None
            and tracker.get_slot("insights_advisor_system_kind") is None
        ):
            resolved = self.resolve_advisor_system_kind(user_input)
            if len(resolved) > 0:
                return resolved

        return {}

    async def validate_insights_advisor_system_kind(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        return {"insights_advisor_system_kind": slot_value}

    async def extract_insights_advisor_recommendation_category(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict
    ) -> Dict[Text, Any]:
        requested_slot = tracker.get_slot("requested_slot")
        user_input = tracker.latest_message["text"]

        if requested_slot == "insights_advisor_recommendation_category":
            resolved = self.resolve_recommendation_category(user_input)
            if len(resolved) > 0:
                return resolved

        if (
            requested_slot is None
            and tracker.get_slot("insights_advisor_recommendation_category") is None
        ):
            resolved = self.resolve_recommendation_category(user_input)
            if len(resolved) > 0:
                return resolved

        return {}

    async def validate_insights_advisor_recommendation_category(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        return {"insights_advisor_recommendation_category": slot_value}

    async def extract_insights_openshift_advisor_category(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict
    ) -> Dict[Text, Any]:
        requested_slot = tracker.get_slot("requested_slot")
        user_input = tracker.latest_message["text"]

        if requested_slot == "insights_openshift_advisor_category":
            resolved = self.resolve_openshift_category(user_input)
            if len(resolved) > 0:
                return resolved

        if (
            requested_slot is None
            and tracker.get_slot("insights_openshift_advisor_category") is None
        ):
            resolved = self.resolve_openshift_category(user_input)
            if len(resolved) > 0:
                return resolved

        return {}

    async def validate_insights_openshift_advisor_category(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        return {"insights_advisor_recommendation_category": slot_value}

    def rhel_error(self, dispatcher: CollectingDispatcher, events):
        flow_finished_count(Flow.ADVISOR, "rhel/error")
        dispatcher.utter_message(response="utter_advisor_recommendation_pathways_error")
        return events

    def resolve_recommendation_category(self, user_input):
        for word in user_input.split(" "):
            resolved = resolve_slot_match(word, advisor_categories)
            if len(resolved) > 0:
                return resolved

        return {}

    def resolve_openshift_category(self, user_input):
        for word in user_input.split(" "):
            resolved = resolve_slot_match(word, advisor_openshift_categories)
            if len(resolved) > 0:
                return resolved

        return {}

    def resolve_advisor_system_kind(self, user_input):
        for word in user_input.split(" "):
            resolved = resolve_slot_match(word, advisor_system)
            if len(resolved) > 0:
                return resolved

        return {}

    def openshift_error(self, dispatcher: CollectingDispatcher, events):
        flow_finished_count(Flow.ADVISOR, "openshift/error")
        dispatcher.utter_message(
            response="utter_advisor_openshift_recommendation_error"
        )
        return events

    async def process_rhel_advisor(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict, events
    ) -> List[Dict[Text, Any]]:
        insights_advisor_recommendation_category = tracker.get_slot(
            "insights_advisor_recommendation_category"
        )

        category_id = None
        category_name = None

        if insights_advisor_recommendation_category == CATEGORY_NEW:
            extra_filter_params = "sort=-publish_date"
            category_name = CATEGORY_NEW
        elif insights_advisor_recommendation_category == CATEGORY_CRITICAL:
            extra_filter_params = "total_risk=4"
            category_name = CATEGORY_CRITICAL
        elif insights_advisor_recommendation_category == CATEGORY_WORKLOADS:
            extra_filter_params = "filter[system_profile][sap_system]=true"
            category_name = CATEGORY_WORKLOADS
        else:
            # Find the id of the category
            response, content = await send_console_request(
                "advisor", "/api/insights/v1/rulecategory/", tracker
            )

            if not response.ok:
                return self.rhel_error(dispatcher, events)

            for category in content:
                if category["name"].lower() == insights_advisor_recommendation_category:
                    category_id = category["id"]
                    category_name = category["name"].lower()
                    break

            if category_id is None:
                return self.rhel_error(dispatcher, events)

            extra_filter_params = f"category={category_id}&sort=-total_risk"

        response, content = await send_console_request(
            "advisor",
            f"/api/insights/v1/rule?{extra_filter_params}&{self.filter_query}&limit=3",
            tracker,
        )

        if not response.ok:
            return self.rhel_error(dispatcher, events)

        if len(content["data"]) > 0:
            category_text = f"top {category_name}"
            if category_name == CATEGORY_NEW:
                category_text = "newest"

            message = f"Here are your {category_text} recommendations from Advisor.\n"
            index = 1
            for rule in content["data"]:
                message += f" {index}. [{rule['description']}](/insights/advisor/recommendations/{rule['rule_id']})\n"
                index += 1

            dashboard_link = f"/insights/advisor/recommendations?category={category_id}&{self.filter_query}&limit=20&offset=0"
            if category_name == CATEGORY_NEW:
                dashboard_link = f"/insights/advisor/recommendations?limit=20&offset=0"

            message += f"\nYou can see additional recommendations on the [Advisor dashboard]({dashboard_link})."
        else:
            message = f"You don't have any {category_name} recommendations right now."

        flow_finished_count(Flow.ADVISOR, "rhel")
        dispatcher.utter_message(text=message)
        return events

    async def process_openshift_advisor(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict, events
    ) -> List[Dict[Text, Any]]:
        category = tracker.get_slot("insights_openshift_advisor_category")

        if category == "recommendation":
            return await self.openshift_recommendation(
                dispatcher, tracker, domain, events
            )
        elif category == OPENSHIFT_CATEGORY_CLUSTER:
            return await self.openshift_clusters(dispatcher, tracker, domain, events)
        elif category == OPENSHIFT_CATEGORY_WORKLOAD:
            return await self.openshift_workload(dispatcher, tracker, domain, events)

        flow_finished_count(Flow.ADVISOR, "openshift")

    async def openshift_clusters(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict, events
    ) -> List[Dict[Text, Any]]:

        response, content = await send_console_request(
            "advisor-openshift",
            f"/api/insights-results-aggregator/v2/clusters",
            tracker,
        )

        if not response.ok:
            return self.openshift_error(dispatcher, events)

        if len(content["data"]) > 0:
            clusters = content["data"]
            clusters.sort(
                key=lambda r: [r["last_checked_at"]] if "last_checked_at" in r else [],
                reverse=True,
            )

            message = (
                f"Here are your most recent clusters from OpenShift for Advisor.\n"
            )
            index = 1
            for cluster in clusters[0:3]:
                message += f" {index}. [{cluster['cluster_name']}](/openshift/insights/advisor/clusters/{cluster['cluster_id']})\n"
                index += 1

            dashboard_link = f"/openshift/insights/advisor/clusters"
            message += f"\nYou can see additional clusters on the [OpenShift for Advisor dashboard]({dashboard_link})."
        else:
            message = f"You don't have any cluster data right now."

        dispatcher.utter_message(text=message)
        return events

    async def openshift_workload(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict, events
    ) -> List[Dict[Text, Any]]:

        response, content = await send_console_request(
            "advisor-openshift",
            f"/api/insights-results-aggregator/v2/namespaces/dvo",
            tracker,
        )

        if not response.ok and content["status"] != "ok":
            return self.openshift_error(dispatcher, events)

        if len(content["workloads"]) > 0:
            workloads = content["workloads"]
            workloads.sort(
                key=lambda r: r.get("metadata", {}).get("last_checked_at"),
                reverse=True,
            )

            message = (
                f"Here are your most recent workloads from OpenShift for Advisor.\n"
            )
            index = 1
            for workload in workloads[0:3]:
                message += f" {index}. [{workload['cluster']['display_name']}](/openshift/insights/advisor/workloads/{workload['cluster']['uuid']}/{workload['namespace']['uuid']})\n"
                index += 1

            dashboard_link = f"/openshift/insights/advisor/workloads"
            message += f"\nYou can see additional workloads on the [OpenShift for Advisor dashboard]({dashboard_link})."
        else:
            message = f"You don't have any workload data right now."

        dispatcher.utter_message(text=message)
        return events

    async def openshift_recommendation(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict, events
    ) -> List[Dict[Text, Any]]:

        response, content = await send_console_request(
            "advisor-openshift",
            f"/api/insights-results-aggregator/v2/rule?impacting=true",
            tracker,
        )

        if not response.ok:
            return self.openshift_error(dispatcher, events)

        if len(content["recommendations"]) > 0:
            rules = content["recommendations"]
            rules.sort(key=lambda r: r["total_risk"], reverse=True)
            message = f"Here are your top recommendations from OpenShift for Advisor.\n"
            index = 1
            for rule in rules[0:3]:
                message += f" {index}. [{rule['description']}](/openshift/insights/advisor/recommendations/{rule['rule_id']})\n"
                index += 1

            dashboard_link = f"/openshift/insights/advisor/recommendations"
            message += f"\nYou can see additional recommendations on the [OpenShift for Advisor dashboard]({dashboard_link})."
        else:
            message = f"You don't have any recommendations right now."

        dispatcher.utter_message(text=message)

        return events

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[Dict[Text, Any]]:
        events = await super().run(dispatcher, tracker, domain)

        if await all_required_slots_are_set(self, dispatcher, tracker, domain):
            if tracker.get_slot("insights_advisor_system_kind") == "rhel":
                return await self.process_rhel_advisor(
                    dispatcher, tracker, domain, events
                )
            else:
                return await self.process_openshift_advisor(
                    dispatcher, tracker, domain, events
                )

        return events

    async def required_slots(
        self,
        domain_slots: List[Text],
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> List[Text]:
        insights_advisor_system_kind = tracker.get_slot("insights_advisor_system_kind")
        if insights_advisor_system_kind == "openshift":
            updated_slots = domain_slots.copy()
            updated_slots.remove("insights_advisor_recommendation_category")
            return updated_slots
        elif insights_advisor_system_kind == "rhel":
            updated_slots = domain_slots.copy()
            updated_slots.remove("insights_openshift_advisor_category")
            return updated_slots

        return domain_slots
