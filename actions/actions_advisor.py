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

from common import get_auth_header
from .utils import show_more


CONSOLEDOT_BASE_URL = "https://console.redhat.com"

class AdvisorAPIPathway(Action):

    def name(self) -> Text:
        return 'action_advisor_api-pathway'

    async def run(self,
                  dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        base_url = getenv("CONSOLEDOT_BASE_URL", CONSOLEDOT_BASE_URL)

        auth_header = None
        try:
            auth_header = get_auth_header(tracker)
        except Exception as e:
            print(f"An Exception occured while handling retrieving auth credentials: {e}")
            dispatcher.utter_message(id="utter_fallback_message")
            return []

        result = None
        try:
            result = requests.get(
                base_url+"/api/insights/v1/pathway/?&sort=-recommendation_level&limit=3",
                headers={auth_header['key']: auth_header['value']}
            ).json()
        except Exception as e:
            print(f"An Exception occured while handling response from the Advisor API: {e}")

        if not result or not result['meta']:
            dispatcher.utter_message(text="I was unable to talk with Advisor to fulfill your request. :(")

        rec_count = result['meta']['count']
        message_string = "You have {} recommended pathways from Advisor.".format(rec_count)
        if rec_count > 3:
            message_string += " Here are the first 3."

        dispatcher.utter_message(text=message_string)

        for i, rec in enumerate(result['data']):
            bot_response = "{}. {}\n Impacted Systems:{}\n {}".format(i+1, rec['name'], rec['impacted_systems_count'], rec['description'])
            if len(rec['categories']) > 0:
                bot_response += "\n Categories: "
                bot_response += ",".join([c['name'] for c in rec['categories']])

            dispatcher.utter_message(text=bot_response)

        dispatcher.utter_message(json_data = show_more(name="Advisor", url_prefix="/insights/advisor/recommendations"))

        events = [ActionExecuted(self.name())]
        return events
