from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import ActionExecuted, SlotSet, UserUtteranceReverted, ActionReverted
from rasa_sdk.types import DomainDict

from common import logging


logger = logging.initialize_logging()
RHEL_VERSION = "image_builder_rhel_version"
RHEL_VERSION_CONFIRM = "image_builder_rhel_version_confirmed"

class ValidateFormImageBuilderGettingStarted(FormValidationAction):
    def name(self) -> Text:
        return "validate_form_image_builder_getting_started"

    @staticmethod
    def break_form_if_not_extracted_requested_slot(
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
        slot: Text,
    ):
        if (
            tracker.slots.get("requested_slot") == slot
            and tracker.slots.get(slot) is None
        ):
            return {"core_break_form": True}

        return {slot: tracker.slots.get(slot)}

    @staticmethod
    def extract_image_builder_rhel_version(
        dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict
    ) -> Dict[Text, Any]:
        return ValidateFormImageBuilderGettingStarted.break_form_if_not_extracted_requested_slot(
            dispatcher, tracker, domain, RHEL_VERSION
        )

    @staticmethod
    def validate_image_builder_rhel_version(
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        if value in ["RHEL 8", "RHEL 9"]:
            return {RHEL_VERSION: value}
        return {RHEL_VERSION: None}

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[Dict[Text, Any]]:
        requested_slot = tracker.get_slot("requested_slot")

        if requested_slot == RHEL_VERSION:
            rhel_version = tracker.get_slot(RHEL_VERSION)
            if rhel_version == "RHEL 9":
                return [SlotSet(RHEL_VERSION_CONFIRM, True), SlotSet("requested_slot", None)]

        form_result = await super().run(dispatcher, tracker, domain)

        core_break_form = tracker.get_slot("core_break_form")

        if core_break_form is True:
            form_start = tracker.get_last_event_for("active_loop")
            form_start_index = tracker.events.index(form_start)
            user_utterances_count = 1
            for event in tracker.events[form_start_index:]:
                if event["event"] == "user":
                    user_utterances_count += 1

            return [UserUtteranceReverted()] * user_utterances_count + [
                SlotSet("requested_slot", None),
                ActionReverted(),
            ]

        return form_result

    async def required_slots(
        self,
        domain_slots: List[Text],
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> List[Text]:
        updated_slots = domain_slots.copy()

        if tracker.get_slot(RHEL_VERSION) == "RHEL 9":
            updated_slots.remove("image_builder_rhel_version_confirm")

        return updated_slots

class ImageBuilderGettingStarted(Action):
    def name(self) -> Text:
        return "action_image_builder_getting_started"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        # Need to find way to use the RHEL version to fill the proper form in wizard
        # rhel_version = tracker.get_slot(RHEL_VERSION)
        dispatcher.utter_message(response="utter_image_builder_redirect_1")
        dispatcher.utter_message(
            response="utter_image_builder_redirect_2",
            link="https://console.redhat.com/insights/image-builder/imagewizard#SIDs=&tags="
        )

        events = [ActionExecuted(self.name())]
        return events


class ImageBuilderLaunch(Action):
    def name(self) -> Text:
        return "action_image_builder_launch"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        provider = tracker.latest_message['entities'][0]['value'].lower()
        # The team does not have a generic quickstart for other providers, default to AWS
        logger.info(f"Provider: {provider}")
        quick_start = ""
        if provider == "aws" or provider == "azure" or provider == "gcp":
            quick_start = f"https://console.redhat.com/insights/image-builder?quickstart=insights-launch-{provider}"
            provider = provider.upper()
        else:
            provider = "your provider"
            quick_start = "https://console.redhat.com/insights/image-builder?quickstart=insights-launch-aws"

        dispatcher.utter_message(
            response="utter_image_builder_launch",
            provider=provider,
            quick_start=quick_start
        )

        events = [ActionExecuted(self.name())]
        return events
