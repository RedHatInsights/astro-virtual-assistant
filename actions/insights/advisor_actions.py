# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions

from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import ActionExecuted

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
