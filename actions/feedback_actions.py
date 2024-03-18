from typing import Text, Dict, List, Any

from rasa_sdk import Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import Action
from rasa_sdk.events import (
    SlotSet,
    SessionStarted,
    UserUtteranceReverted,
    ActionReverted,
)
from rasa_sdk.types import DomainDict
from rasa_sdk.events import FollowupAction

from actions.slot_match import FuzzySlotMatch, FuzzySlotMatchOption, resolve_slot_match

from common.rasa.tracker import get_email

TYPE = "feedback_type"
WHERE = "feedback_where"
COLLECTION = "feedback_collection"
RESPONSE = "feedback_response"
USABILITY_STUDY = "feedback_usability_study"

FEEDBACK_SLOTS = [
    TYPE,
    WHERE,
    COLLECTION,
    RESPONSE,
    USABILITY_STUDY,
]

RESET_SLOTS = [SlotSet(key, None) for key in FEEDBACK_SLOTS]

type_slot_match = FuzzySlotMatch(
    TYPE,
    [
        FuzzySlotMatchOption(
            "bug",
            [
                "a bug",
                "it's about a bug",
                "an error",
                "it's about an error",
                "issue",
                "it's about an issue",
            ],
        ),
        FuzzySlotMatchOption(
            "general",
            [
                "it's a feature",
                "it's a suggestion",
                "something else",
                "it's about something else",
            ],
        ),
    ],
)

where_slot_match = FuzzySlotMatch(
    WHERE,
    [
        FuzzySlotMatchOption(
            "conversation",
            ["this conversation", "our conversation", "conversation", "this assistant"],
        ),
        FuzzySlotMatchOption(
            "console",
            [
                "the console",
                "it's with the console",
                "the platform",
                "platform",
                "console",
            ],
        ),
    ],
)

collection_slot_match = FuzzySlotMatch(
    COLLECTION,
    [
        FuzzySlotMatchOption(
            "pendo", ["pendo", "I'd prefer to use pendo", "form please", "your form"]
        ),
        FuzzySlotMatchOption(
            "assistant",
            [
                "assistant",
                "this assistant",
                "with you",
                "right here",
                "this conversation",
                "chat",
                "conversation",
                "I'll let you collect the details.",
                "I'd prefer to use the assistant",
            ],
        ),
    ],
)


class ValidateFormFeedback(FormValidationAction):
    def name(self) -> Text:
        return "validate_form_feedback"

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
    def extract_feedback_type(
        dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict
    ) -> Dict[Text, Any]:
        if tracker.get_slot("requested_slot") == TYPE:
            resolved = resolve_slot_match(
                tracker.latest_message["text"], type_slot_match
            )
            if len(resolved) > 0:
                return resolved

        return {}

    @staticmethod
    def extract_feedback_where(
        dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict
    ) -> Dict[Text, Any]:
        if tracker.get_slot("requested_slot") == WHERE:
            resolved = resolve_slot_match(
                tracker.latest_message["text"], where_slot_match
            )
            if len(resolved) > 0:
                return resolved

        return {}

    @staticmethod
    def extract_feedback_collection(
        dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict
    ) -> Dict[Text, Any]:
        if tracker.get_slot("requested_slot") == COLLECTION:
            resolved = resolve_slot_match(
                tracker.latest_message["text"], collection_slot_match
            )
            if len(resolved) > 0:
                return resolved

        return {}

    @staticmethod
    def extract_feedback_response(
        dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict
    ) -> Dict[Text, Any]:
        return ValidateFormFeedback.break_form_if_not_extracted_requested_slot(
            dispatcher, tracker, domain, RESPONSE
        )

    @staticmethod
    def extract_feedback_usability_study(
        dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict
    ) -> Dict[Text, Any]:
        return ValidateFormFeedback.break_form_if_not_extracted_requested_slot(
            dispatcher, tracker, domain, USABILITY_STUDY
        )

    @staticmethod
    def validate_feedback_type(
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        if value in ["bug", "general"]:
            return {TYPE: value}
        return {TYPE: None}

    @staticmethod
    def validate_feedback_where(
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        if value in ["conversation", "console"]:
            return {WHERE: value}
        return {WHERE: None}

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[Dict[Text, Any]]:
        events = await super().run(dispatcher, tracker, domain)
        requested_slot = tracker.get_slot("requested_slot")

        feedback_type = tracker.get_slot(TYPE)
        if requested_slot == TYPE:
            if feedback_type == "bug":
                dispatcher.utter_message(response="utter_feedback_type_bug")
                dispatcher.utter_message(response="utter_bug_where")
            elif feedback_type == "general":
                dispatcher.utter_message(response="utter_ask_feedback_where_general")

        if requested_slot == WHERE:
            feedback_where = tracker.get_slot(WHERE)
            if feedback_where == "console" and feedback_type == "bug":
                dispatcher.utter_message(response="utter_bug_redirect")
                events.append(SlotSet("requested_slot", None))
                return events + RESET_SLOTS

            elif feedback_where == "conversation":
                return (
                    events
                    + RESET_SLOTS
                    + [
                        SlotSet("requested_slot", None),
                        SlotSet("feedback_form_to_closing_form", True),
                        SlotSet("closing_skip_got_help", True),
                        SlotSet("closing_leave_feedback", True),
                        SlotSet("closing_feedback_type", "this_conversation"),
                    ]
                )

        if requested_slot == COLLECTION:
            feedback_collection = tracker.get_slot(COLLECTION)
            if feedback_collection == "pendo":
                dispatcher.utter_message(response="utter_feedback_collection_pendo")
                return events + [SlotSet("requested_slot", None)] + RESET_SLOTS

        if requested_slot == RESPONSE:
            dispatcher.utter_message(response="utter_feedback_transparency")

        if requested_slot == USABILITY_STUDY:
            if tracker.get_slot(USABILITY_STUDY) is True:
                dispatcher.utter_message(response="utter_feedback_usability_study_yes")
            else:
                dispatcher.utter_message(response="utter_feedback_usability_study_no")

        core_break_form = tracker.get_slot("core_break_form")

        if core_break_form is True:
            form_start = tracker.get_last_event_for("active_loop")
            form_start_index = tracker.events.index(form_start)
            user_utterances_count = 1
            for event in tracker.events[form_start_index:]:
                if event["event"] == "user":
                    user_utterances_count += 1

            return (
                events
                + [UserUtteranceReverted()] * user_utterances_count
                + [
                    SlotSet("requested_slot", None),
                    ActionReverted(),
                ]
            )

        return events

    async def required_slots(
        self,
        domain_slots: List[Text],
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> List[Text]:
        updated_slots = domain_slots.copy()

        if tracker.get_slot(TYPE) == "bug":
            updated_slots.remove(COLLECTION)
            updated_slots.remove(RESPONSE)
            updated_slots.remove(USABILITY_STUDY)

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


class ExecuteFormFeedback(Action):
    def name(self) -> Text:
        return "execute_form_feedback"

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[Dict[Text, Any]]:
        feedback_where = tracker.get_slot(WHERE)
        if feedback_where == "conversation":
            # Don't submit to the platform_feedback tool
            return [SlotSet(key, None) for key in FEEDBACK_SLOTS] + [
                SlotSet("requested_slot", None)
            ]

        if tracker.get_slot(COLLECTION) == "assistant":
            feedback_type = tracker.get_slot(TYPE) or "general"

            feedback_type_label = "-".join(feedback_type.split("_")) + "-feedback"

            feedback_response = tracker.get_slot(RESPONSE)
            feedback_usability_study = (
                "The user DOES NOT want to participate in our usability studies."
            )
            if tracker.get_slot(USABILITY_STUDY) is True:
                feedback_usability_study = "The user wants to participate in a usability study. Email: {}".format(
                    get_email(tracker)
                )

            feedback_type_label = "-".join(feedback_type.split("_")) + "-feedback"

            dispatcher.utter_message(
                json_message={
                    "type": "command",
                    "command": "feedback",
                    "params": {
                        "summary": f"Platform feedback from the assistant",
                        "description": f"""
                        Feedback type: {feedback_type}
                        Feedback: {feedback_response}
                        
                        {feedback_usability_study}
                        """,
                        "labels": ["virtual-assistant", feedback_type_label],
                    },
                },
            )

            dispatcher.utter_message(response="utter_feedback_thanks")

        dispatcher.utter_message(response="utter_core_how_can_i_help")

        return [SlotSet(key, None) for key in FEEDBACK_SLOTS] + [
            SlotSet("requested_slot", None)
        ]


class ActionFeedbackTypeBug(Action):
    def name(self) -> Text:
        return "action_feedback_type_bug"

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[Dict[Text, Any]]:
        return [
            SlotSet("feedback_type", "bug"),
            SlotSet("requested_slot", "feedback_type"),
        ]


class ActionFeedbackFormToClosingForm(Action):
    def name(self) -> Text:
        return "action_feedback_form_to_closing_form"

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[Dict[Text, Any]]:
        return [
            FollowupAction("form_closing"),
            SlotSet("feedback_form_to_closing_form", None),
        ]
