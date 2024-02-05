from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import ActionExecuted
from rasa_sdk.types import DomainDict

from common import logging


logger = logging.initialize_logging()
RHEL_VERSION = "image_builder_rhel_version"

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

        feedback_type = tracker.get_slot()
        if requested_slot == TYPE:
            if feedback_type == "bug":
                dispatcher.utter_message(response="utter_feedback_type_bug")
                dispatcher.utter_message(response="utter_bug_where")
            elif feedback_type == "general":
                dispatcher.utter_message(response="utter_ask_feedback_where_general")

        if requested_slot == WHERE:
            feedback_where = tracker.get_slot(WHERE)
            reset_slots = [SlotSet(key, None) for key in FEEDBACK_SLOTS]
            if feedback_where == "console" and feedback_type == "bug":
                dispatcher.utter_message(response="utter_bug_redirect")
                return [SlotSet("requested_slot", None)] + reset_slots

            elif feedback_where == "conversation":
                return reset_slots + [
                    SlotSet("requested_slot", None),
                    SlotSet("feedback_form_to_closing_form", True),
                    SlotSet("closing_skip_got_help", True),
                    SlotSet("closing_leave_feedback", True),
                    SlotSet("closing_feedback_type", "this_conversation"),
                ]

        if requested_slot == COLLECTION:
            feedback_collection = tracker.get_slot(COLLECTION)
            if feedback_collection == "pendo":
                reset_slots = [SlotSet(key, None) for key in FEEDBACK_SLOTS]
                dispatcher.utter_message(response="utter_feedback_collection_pendo")
                return [SlotSet("requested_slot", None)] + reset_slots

        if requested_slot == RESPONSE:
            dispatcher.utter_message(response="utter_feedback_transparency")

        if requested_slot == USABILITY_STUDY:
            if tracker.get_slot(USABILITY_STUDY) is True:
                dispatcher.utter_message(response="utter_feedback_usability_study_yes")
            else:
                dispatcher.utter_message(response="utter_feedback_usability_study_no")

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

        if (
            tracker.get_slot(TYPE) == "general"
            and tracker.get_slot("feedback_where") == "conversation"
        ):
            updated_slots.remove(COLLECTION)
            updated_slots.remove(RESPONSE)
            updated_slots.remove(USABILITY_STUDY)

        if tracker.get_slot(COLLECTION) == "pendo":
            updated_slots.remove(RESPONSE)
            updated_slots.remove(USABILITY_STUDY)

        return updated_slots


class ImageBuilderLaunch(Action):
    def name(self) -> Text:
        return "action_image_builder_launch"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        provider = tracker.latest_message['entities'][0]['value']
        # The team does not have a generic quickstart for other providers, default to AWS
        logger.info(f"Provider: {provider}")
        quick_start = ""
        if provider == "aws":
            quick_start = "https://console.redhat.com/insights/image-builder?quickstart=insights-launch-aws"
        elif provider == "azure":
            quick_start = "https://console.redhat.com/insights/image-builder?quickstart=insights-launch-azure"
        elif provider == "gcp":
            quick_start = "https://console.redhat.com/insights/image-builder?quickstart=insights-launch-gcp"
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
