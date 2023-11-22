from typing import Text, List

from rasa_sdk import Tracker, FormValidationAction, Action
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import EventType, SlotSet
from rasa_sdk.types import DomainDict

from actions.insights.notifications import send_rbac_request_admin
from common import logging
from common.rasa.tracker import get_decoded_user_identity

logger = logging.initialize_logging()

_SLOT_ACCESS_REQUEST_URL = "access_request_url"
_SLOT_LEAVE_REQUEST_MESSAGE = "access_leave_request_message"
_SLOT_REQUEST_MESSAGE = "access_request_message"


class ExecuteFormAccessRequestAccess(Action):
    def name(self) -> Text:
        return "execute_access_form_access_request"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> List[EventType]:
        try:
            identity = get_decoded_user_identity(tracker)
            email = identity["identity"]["user"]["email"]
            username = identity["identity"]["user"]["username"]
            org_id = identity["identity"]["org_id"]

            user_message = tracker.get_slot(_SLOT_REQUEST_MESSAGE)
            requested_url = tracker.get_slot(_SLOT_ACCESS_REQUEST_URL)

            send_rbac_request_admin(
                tracker,
                org_id,
                username,
                requested_url=requested_url,
                user_email=email,
                user_message=user_message,
            )

            dispatcher.utter_message(response="utter_access_request_access_submitted")
        finally:
            return [
                SlotSet(_SLOT_ACCESS_REQUEST_URL),
                SlotSet(_SLOT_LEAVE_REQUEST_MESSAGE),
                SlotSet(_SLOT_REQUEST_MESSAGE),
            ]


class ValidateFormAccessRequestAccess(FormValidationAction):
    def name(self) -> Text:
        return "validate_access_form_access_request"

    async def required_slots(
        self,
        domain_slots: List[Text],
        dispatcher: "CollectingDispatcher",
        tracker: "Tracker",
        domain: "DomainDict",
    ) -> List[Text]:
        if tracker.get_slot(_SLOT_LEAVE_REQUEST_MESSAGE) is False:
            updated_slots = domain_slots.copy()
            updated_slots.remove(_SLOT_REQUEST_MESSAGE)
            return updated_slots

        return domain_slots
