# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions

from typing import Any, Text, Dict, List, Optional

from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import ActionExecuted, UserUtteranceReverted, SlotSet, ActiveLoop
from rasa_sdk.types import DomainDict

from actions.slot_match import FuzzySlotMatch, FuzzySlotMatchOption, resolve_slot_match
from common import logging
from common.requests import send_console_request

logger = logging.initialize_logging()


class AdvisorAPIPathway(Action):
    def name(self) -> Text:
        return "action_advisor_api_pathway"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        response, result = await send_console_request(
            "advisor",
            "/api/insights/v1/pathway/?&sort=-recommendation_level&limit=3",
            tracker,
        )

        if not response.ok or not result or not result["meta"]:
            dispatcher.utter_message(
                response="utter_advisor_recommendation_pathways_error"
            )
            logger.debug(
                "Failed to get a response from the advisor API: status {}; result {}".format(
                    response.status, result
                )
            )
            return []

        total = None
        displayed = None
        try:
            total = result["meta"]["count"]
            displayed = len(result["data"])
        except KeyError:
            logger.debug(
                "Failed to parse the response from the advisor API - KeyError: {}".format(
                    result
                )
            )
            dispatcher.utter_message(
                response="utter_advisor_recommendation_pathways_error"
            )
            return []
        except Exception as e:
            logger.debug(
                "Failed to parse the response from the advisor API: error {}; status {}; result {}".format(
                    e, response.status, result
                )
            )
            dispatcher.utter_message(
                response="utter_advisor_recommendation_pathways_error"
            )
            return []

        dispatcher.utter_message(
            response="utter_advisor_recommendation_pathways_total",
            total=total,
            displayed=displayed,
        )

        for i, rec in enumerate(result["data"]):
            bot_response = "{}. {}\n Impacted Systems:{}\n {}".format(
                i + 1, rec["name"], rec["impacted_systems_count"], rec["description"]
            )
            if len(rec["categories"]) > 0:
                bot_response += "\n Categories: "
                bot_response += ",".join([c["name"] for c in rec["categories"]])

            dispatcher.utter_message(text=bot_response)

        dispatcher.utter_message(
            response="utter_advisor_recommendation_pathways_closing",
            link="/openshift/insights/advisor/recommendations",
        )

        events = [ActionExecuted(self.name())]
        return events


CATEGORY_PERFORMANCE = "performance"
CATEGORY_SECURITY = "security"
CATEGORY_AVAILABILITY = "availability"
CATEGORY_STABILITY = "stability"

advisor_categories = FuzzySlotMatch(
    "insights_advisor_recommendation_category",
    [
        FuzzySlotMatchOption(CATEGORY_PERFORMANCE),
        FuzzySlotMatchOption(CATEGORY_SECURITY),
        FuzzySlotMatchOption(CATEGORY_AVAILABILITY),
        FuzzySlotMatchOption(CATEGORY_STABILITY),
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

    filter_query = "impacting=true&rule_status=enabled&sort=-total_risk"

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
            # Find the id of the category
            response, content = await send_console_request(
                "advisor", "/api/insights/v1/rulecategory/", tracker
            )

            if not response.ok:
                return self.error(dispatcher, events)

            category_id = None
            category_name = None
            insights_advisor_recommendation_category = tracker.get_slot(
                "insights_advisor_recommendation_category"
            )

            for category in content:
                if category["name"].lower() == insights_advisor_recommendation_category:
                    category_id = category["id"]
                    category_name = category["name"].lower()
                    break

            if category_id is None:
                return self.error(dispatcher, events)

            response, content = await send_console_request(
                "advisor",
                f"/api/insights/v1/rule?category={category_id}&{self.filter_query}&limit=3",
                tracker,
            )

            if not response.ok:
                return self.error(dispatcher, events)

            if len(content["data"]) > 0:
                message = (
                    f"Here are your top {category_name} recommendations from Advisor.\n"
                )
                index = 1
                for rule in content["data"]:
                    message += f" {index}. [{rule['description']}](/insights/advisor/recommendations/{rule['rule_id']})\n"
                    index += 1

                message += f"\nYou can see additional recommendations on the [Advisor dashboard](/insights/advisor/recommendations?category={category_id}&{self.filter_query}&limit=20&offset=0)."
            else:
                message = (
                    f"You don't have any {category_name} recommendations right now."
                )

            dispatcher.utter_message(text=message)

        return events
