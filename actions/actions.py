# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions

from typing import Any, Text, Dict, List, Optional

from rasa_sdk import Action, Tracker
from rasa_sdk.types import DomainDict
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import ActionExecuted
import requests
from .auth import get_auth_token
from ..common.identity import get_identity
from .forms import IntentBasedFormValidationAction


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


class OpenshiftCreateClusterAction(IntentBasedFormValidationAction):

    def name(self) -> Text:
        return "validate_form_openshift_clusters_create-cluster"

    def utter_not_extracted(self, slot_name: Text) -> Optional[Text]:
        return "Sorry. I did not understand your answer. Could you try again?"

    def form_finished(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict):
        slots = tracker.slots
        is_managed_and_hosted = slots.get("openshift_managed") == "yes" and slots.get("openshift_hosted") == "hosted"
        is_on_cloud = slots.get("openshift_where") == "cloud"
        provider = slots.get("openshift_provider")

        found = False

        if is_managed_and_hosted and is_on_cloud:
            if provider == "aws":
                dispatcher.utter_message(text="Based on your answers, we think you should install using Red Hat "
                                              "OpenShift Service on AWS (ROSA).")
                found = True
            elif provider == "azure":
                dispatcher.utter_message(text="Based on your answers, we think you should install using Azure Red Hat "
                                              "Openshift")
                found = True

        if not found:
            dispatcher.utter_message(text="Based on your answers, we don't know what you should install - whoops.")

        dispatcher.utter_message(text="Your answers:")
        dispatcher.utter_message(text=f" - Where: {slots.get('openshift_where')}")
        if is_on_cloud:
            dispatcher.utter_message(text=f" - Provider: {slots.get('openshift_provider')}")
        dispatcher.utter_message(text=f" - Managed by Red Hat: {slots.get('openshift_managed')}")
        dispatcher.utter_message(text=f" - Hosted or Standalone control plane?: {slots.get('openshift_hosted')}")

    async def extract_openshift_hosted(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict):
        next_slot = (await self.next_requested_slot(dispatcher, tracker, domain)).get("value")
        value = None

        if next_slot == "openshift_hosted":
            message = tracker.latest_message.get("text").lower()
            # Todo: Replace with embeddings
            if "standalone" in message:
                value = "standalone"
            elif "hosted" in message:
                value = "hosted"

        return {
            "openshift_hosted": value
        }

    async def required_slots(
            self,
            domain_slots: List[Text],
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict
    ) -> List[Text]:
        base_slots = [
            "openshift_where",
            "openshift_provider",
            "openshift_managed",
            "openshift_hosted"
        ]

        if tracker.slots.get("openshift_where") != "cloud":
            base_slots.remove("openshift_provider")

        return base_slots
