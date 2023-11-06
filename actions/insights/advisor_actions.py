# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions

from typing import Any, Text, Dict, List
from os import getenv

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import ActionExecuted
import requests

from common import Header, get_auth_header
from ..utils import show_more


CONSOLEDOT_BASE_URL = "https://console.redhat.com"

class AdvisorAPIPathway(Action):

    def name(self) -> Text:
        return 'action_advisor_api_pathway'

    async def run(self,
                  dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        base_url = getenv("CONSOLEDOT_BASE_URL", CONSOLEDOT_BASE_URL)

        header = Header()
        try:
            get_auth_header(tracker, header)
        except Exception as e:
            print(f"An Exception occured while handling retrieving auth credentials: {e}")
            dispatcher.utter_message(response="utter_advisor_recommendation_pathways_error")
            return []

        result = None
        try:
            result = requests.get(
                base_url+"/api/insights/v1/pathway/?&sort=-recommendation_level&limit=3",
                headers=header.build_headers()
            ).json()
        except Exception as e:
            print(f"An Exception occured while handling response from the Advisor API: {e}")

        if not result or not result['meta']:
            dispatcher.utter_message(response="utter_advisor_recommendation_pathways_error")
        
        dispatcher.utter_message(response="utter_advisor_recommendation_pathways_total", total=result['meta']['count'], displayed=len(result['data']))

        for i, rec in enumerate(result['data']):
            bot_response = "{}. {}\n Impacted Systems:{}\n {}".format(i+1, rec['name'], rec['impacted_systems_count'], rec['description'])
            if len(rec['categories']) > 0:
                bot_response += "\n Categories: "
                bot_response += ",".join([c['name'] for c in rec['categories']])

            dispatcher.utter_message(text=bot_response)

        dispatcher.utter_message(response="utter_advisor_recommendation_pathways_closing", link=base_url+"/openshift/insights/advisor/recommendations")

        events = [ActionExecuted(self.name())]
        return events
