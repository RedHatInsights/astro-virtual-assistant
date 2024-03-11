# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions

from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import ActionExecuted, UserUtteranceReverted

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

advisor_categories = FuzzySlotMatch("advisor_category", [
    FuzzySlotMatchOption(CATEGORY_PERFORMANCE),
    FuzzySlotMatchOption(CATEGORY_SECURITY),
    FuzzySlotMatchOption(CATEGORY_AVAILABILITY),
    FuzzySlotMatchOption(CATEGORY_STABILITY),
])


class AdvisorRecommendationByType(Action):

    filter_query = "impacting=true&rule_status=enabled&sort=-total_risk"

    def name(self) -> Text:
        return "action_advisor_recommendation_by_type"

    def cancel(self, dispatcher: CollectingDispatcher):
        dispatcher.utter_message(response="utter_unknown_topic")
        return [UserUtteranceReverted()]

    async def run(
            self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[Dict[Text, Any]]:
        user_input = tracker.latest_message["text"]

        resolved = []
        for word in user_input.split(" "):
            resolved = resolve_slot_match(
                word, advisor_categories
            )

            if len(resolved) > 0:
                break

        if len(resolved) == 0:
            return self.cancel(dispatcher)

        # Find the id of the category
        response, content = await send_console_request("advisor", "/api/insights/v1/rulecategory/", tracker)

        if not response.ok:
            return self.cancel(dispatcher)

        category_id = None
        category_name = None
        for category in content:
            if category["name"].lower() == resolved["advisor_category"]:
                category_id = category["id"]
                category_name = category["name"].lower()
                break

        if category_id is None:
            return self.cancel(dispatcher)

        response, content = await send_console_request("advisor", f"/api/insights/v1/rule?category={category_id}&{self.filter_query}&limit=3", tracker)

        if not response.ok:
            return self.cancel(dispatcher)

        if len(content["data"]) > 0:
            message = f"List of {category_name} recommendations\n"
            index = 1
            for rule in content["data"]:
                message += f" {index}. [{rule['description']}](/insights/advisor/recommendations/{rule['rule_id']})\n"
                index += 1

            message += f"\n[See more {category_name} recommendations here](/insights/advisor/recommendations?category={category_id}&{self.filter_query}&limit=20&offset=0)."
        else:
            message = f"You don't have any {category_name} recommendation right now."

        dispatcher.utter_message(text=message)
