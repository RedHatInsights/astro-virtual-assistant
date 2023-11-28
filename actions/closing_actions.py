from typing import Text, Dict, List, Any

from rasa_sdk import Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import Action
from rasa_sdk.events import SlotSet, SessionStarted
from rasa_sdk.types import DomainDict


class ValidateFormClosing(FormValidationAction):
    def name(self) -> Text:
        return "validate_form_closing"

    async def should_ask_closing_feedback(self, dispatcher, tracker, domain):
        requested_slot = tracker.get_slot("requested_slot")

        if (
            requested_slot == "closing_leave_feedback"
            and tracker.get_slot("closing_leave_feedback") is True
        ):
            return True

        next_requested_slot = await self.next_requested_slot(
            dispatcher, tracker, domain
        )
        if (
            next_requested_slot is not None
            and next_requested_slot.get("value") == "closing_feedback"
        ):
            return True

        return False

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[Dict[Text, Any]]:
        requested_slot = tracker.get_slot("requested_slot")

        if requested_slot == "closing_got_help":
            closing_got_help = tracker.get_slot("closing_got_help")
            if closing_got_help is True:
                dispatcher.utter_message(response="utter_closing_got_help_yes")
            elif closing_got_help is False:
                dispatcher.utter_message(response="utter_closing_got_help_no")

        if await self.should_ask_closing_feedback(dispatcher, tracker, domain):
            closing_feedback_type = tracker.get_slot("closing_feedback_type")
            if closing_feedback_type == "general":
                dispatcher.utter_message(response="utter_closing_feedback_general")
            elif closing_feedback_type == "bad_experience":
                dispatcher.utter_message(
                    response="utter_closing_feedback_bad_experience"
                )
            else:
                dispatcher.utter_message(response="utter_closing_feedback_general")

        return await super().run(dispatcher, tracker, domain)

    async def required_slots(
        self,
        domain_slots: List[Text],
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> List[Text]:
        updated_slots = domain_slots.copy()

        if tracker.get_slot("closing_skip_got_help") is True:
            updated_slots.remove("closing_got_help")

        if tracker.get_slot("closing_feedback_type") is not None:
            updated_slots.remove("closing_leave_feedback")

        if tracker.get_slot("closing_leave_feedback") is False:
            updated_slots.remove("closing_feedback")

        return updated_slots


class ExecuteFormClosing(Action):
    def name(self) -> Text:
        return "execute_form_closing"

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[Dict[Text, Any]]:
        # Todo: Insert logic to send feedback
        if tracker.get_slot("closing_leave_feedback") is True:
            dispatcher.utter_message(response="utter_closing_share_feedback")
            print(
                f"Should send the following feedback:{tracker.get_slot('closing_feedback')}"
            )

        dispatcher.utter_message(response="utter_closing_finally")
        return [
            SlotSet(key, None)
            for key in [
                "closing_got_help",
                "closing_leave_feedback",
                "closing_feedback",
                "closing_skip_got_help",
                "closing_feedback_type",
            ]
        ]


class ExecuteFormClosingAnythingElse(Action):
    def name(self) -> Text:
        return "execute_form_closing_anything_else"

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[Dict[Text, Any]]:
        closing_anything_else = tracker.get_slot("closing_anything_else")
        if closing_anything_else is True:
            dispatcher.utter_message(response="utter_core_how_can_i_help")
        elif closing_anything_else is False:
            dispatcher.utter_message(response="utter_closing_bye")
        else:
            return []

        return [SlotSet(key, None) for key in ["closing_anything_else"]] + [
            SessionStarted()
        ]


class ActionSkipGotHelp(Action):
    def name(self) -> Text:
        return "action_skip_got_help"

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[Dict[Text, Any]]:
        return [SlotSet("closing_skip_got_help", True)]


class ActionClosingFeedbackTypeBadExperience(Action):
    def name(self) -> Text:
        return "action_closing_feedback_type_bad_experience"

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[Dict[Text, Any]]:
        return [SlotSet("closing_feedback_type", "bad_experience")]


class ActionClosingFeedbackTypeGeneral(Action):
    def name(self) -> Text:
        return "action_closing_feedback_type_general"

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[Dict[Text, Any]]:
        return [SlotSet("closing_feedback_type", "general")]
