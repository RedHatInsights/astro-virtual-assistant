# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions

from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import ActionExecuted
import requests
from .auth import get_auth_token
from .identity import get_identity


class ConsoleAPIAction(Action):

    def name(self) -> Text:
        return 'action_console_api'

    async def run(self,
                  dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        token = get_auth_token()
        identity = get_identity(tracker)

        result = requests.get(
            "https://console.redhat.com/api/vulnerability/v1/systems",
            headers={"Authorization": "Bearer " + token}
        ).json()

        if not result or not result['meta']:
            dispatcher.utter_message(text=":robot_face: Unable to retrieve systems.")
            return []

        dispatcher.utter_message(text=":robot_face: You have {} systems, listing first {}:".format(result['meta']['total_items'], len(result['data'])))

        for system in result['data']:
            dispatcher.utter_message(text=":computer: {} ({}) with {} CVEs. <{}|See in Vulnerability>".format(
                system['attributes']['display_name'],
                system['attributes']['os'],
                system['attributes']['cve_count'],
                "https://console.redhat.com/insights/vulnerability/systems/{}".format(system['id'])
            ))

        events = [ActionExecuted(self.name())]
        return events
