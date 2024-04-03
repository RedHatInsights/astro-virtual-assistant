# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions

from typing import Any, Text, Dict, List, Optional

from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, ActiveLoop
from rasa_sdk.types import DomainDict

from actions.slot_match import FuzzySlotMatch, FuzzySlotMatchOption, resolve_slot_match
from common import logging
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

advisor_system = FuzzySlotMatch(
    "insights_advisor_system_kind",
    [
        FuzzySlotMatchOption("rhel", ["rhel", "redhat"]),
        FuzzySlotMatchOption("openshift"),
    ],
)


async def all_required_slots_are_set(
    form: FormValidationAction,
    dispatcher: CollectingDispatcher,
    tracker: Tracker,
    domain: DomainDict,
    ignore: Optional[List[Text]] = None,
) -> bool:
    for slot in await form.required_slots(
        form.domain_slots(domain), dispatcher, tracker, domain
    ):
        if ignore is not None and slot in ignore:
            continue
        if tracker.get_slot(slot) is None:
            return False

    return True


class AdvisorRecommendationByCategoryInit(Action):

    def name(self) -> Text:
        return "form_insights_advisor_recommendation_by_category_init"

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[Dict[Text, Any]]:
        return [
            SlotSet("insights_advisor_system_kind"),
            SlotSet("insights_advisor_recommendation_category"),
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
            resolved = resolve_slot_match(user_input, advisor_system)
            if len(resolved) > 0:
                return resolved

        if (
            requested_slot is None
            and tracker.get_slot("insights_advisor_system_kind") is None
        ):
            resolved = {}
            for word in user_input.split(" "):
                resolved = resolve_slot_match(word, advisor_system)
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
            resolved = resolve_slot_match(user_input, advisor_categories)
            if len(resolved) > 0:
                return resolved

        if (
            requested_slot is None
            and tracker.get_slot("insights_advisor_recommendation_category") is None
        ):
            resolved = {}
            for word in user_input.split(" "):
                resolved = resolve_slot_match(word, advisor_categories)
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

    def error(self, dispatcher: CollectingDispatcher, events):
        dispatcher.utter_message(response="utter_advisor_recommendation_pathways_error")
        return events

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[Dict[Text, Any]]:
        events = await super().run(dispatcher, tracker, domain)

        if tracker.get_slot("insights_advisor_system_kind") == "openshift":
            dispatcher.utter_message(response="utter_advisor_for_openshift")
            return events + [ActiveLoop(None), SlotSet("requested_slot")]

        if await all_required_slots_are_set(self, dispatcher, tracker, domain):
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
                    return self.error(dispatcher, events)

                for category in content:
                    if (
                        category["name"].lower()
                        == insights_advisor_recommendation_category
                    ):
                        category_id = category["id"]
                        category_name = category["name"].lower()
                        break

                if category_id is None:
                    return self.error(dispatcher, events)

                extra_filter_params = f"category={category_id}&sort=-total_risk"

            response, content = await send_console_request(
                "advisor",
                f"/api/insights/v1/rule?{extra_filter_params}&{self.filter_query}&limit=3",
                tracker,
            )

            if not response.ok:
                return self.error(dispatcher, events)

            if len(content["data"]) > 0:
                category_text = f"top {category_name}"
                if category_name == CATEGORY_NEW:
                    category_text = "newest"

                message = (
                    f"Here are your {category_text} recommendations from Advisor.\n"
                )
                index = 1
                for rule in content["data"]:
                    message += f" {index}. [{rule['description']}](/insights/advisor/recommendations/{rule['rule_id']})\n"
                    index += 1

                dashboard_link = f"/insights/advisor/recommendations?category={category_id}&{self.filter_query}&limit=20&offset=0"
                if category_name == CATEGORY_NEW:
                    dashboard_link = (
                        f"/insights/advisor/recommendations?limit=20&offset=0"
                    )

                message += f"\nYou can see additional recommendations on the [Advisor dashboard]({dashboard_link})."
            else:
                message = (
                    f"You don't have any {category_name} recommendations right now."
                )

            dispatcher.utter_message(text=message)

        return events
