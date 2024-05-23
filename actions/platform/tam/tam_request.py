from typing import List, Dict, Text, Any
from urllib.parse import urlparse


from rasa_sdk import FormValidationAction, Tracker, Action
from rasa_sdk.events import SlotSet, EventType
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict

from actions.slot_match import resolve_slot_match
from common.requests import send_console_request
from common.config import app

from actions.platform.tam import (
    _TAM_ACCOUNT_ID,
    _TAM_ORG_ID,
    _TAM_DURATION,
    _TAM_CONFIRMATION,
    _DURATIONS,
    durations_match,
    get_start_end_date_from_duration,
)


class AccessRequestTAM(FormValidationAction):
    def name(self) -> str:
        return "validate_form_access_request_tam"

    # if matched intent is not nlu_fallback, then break
    def check_for_break(self, tracker: Tracker) -> bool:
        last_intent = tracker.latest_message.get("intent", {}).get("name")
        return last_intent != "nlu_fallback"

    def extract_access_request_tam_account_id(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict
    ) -> Dict[Text, Any]:
        if tracker.get_slot(
            "requested_slot"
        ) != _TAM_ACCOUNT_ID or self.check_for_break(tracker):
            return {}

        return {_TAM_ACCOUNT_ID: tracker.latest_message.get("text")}

    def extract_access_request_tam_org_id(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict
    ) -> Dict[Text, Any]:
        if tracker.get_slot("requested_slot") != _TAM_ORG_ID or self.check_for_break(
            tracker
        ):
            return {}

        return {_TAM_ORG_ID: tracker.latest_message.get("text")}

    def extract_access_request_tam_duration(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict
    ) -> Dict[Text, Any]:
        if tracker.get_slot("requested_slot") != _TAM_DURATION or self.check_for_break(
            tracker
        ):
            return {}

        resolved = resolve_slot_match(tracker.latest_message["text"], durations_match)
        if len(resolved) > 0:
            return resolved

        return {}

    # validate functions for each of the slots
    async def validate_access_request_tam_account_id(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        return {_TAM_ACCOUNT_ID: slot_value}

    async def validate_access_request_tam_org_id(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        return {_TAM_ORG_ID: slot_value}

    async def validate_access_request_tam_duration(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        if slot_value in _DURATIONS:
            return {_TAM_DURATION: slot_value}
        return {}

    async def validate_access_request_tam_confirmation(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        return {_TAM_CONFIRMATION: slot_value}

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[Dict[Text, Any]]:
        events = await super().run(dispatcher, tracker, domain)
        requested_slot = tracker.get_slot("requested_slot")

        if requested_slot == _TAM_DURATION:
            dispatcher.utter_message(response="utter_access_request_tam_roles_note")

        return events


class ExecuteTAMRequest(Action):
    def name(self) -> Text:
        return "execute_form_access_request_tam"

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[Dict[Text, Any]]:
        account_id = tracker.get_slot(_TAM_ACCOUNT_ID)
        org_id = tracker.get_slot(_TAM_ORG_ID)
        duration = tracker.get_slot(_TAM_DURATION)
        confirmation = tracker.get_slot(_TAM_CONFIRMATION)

        if not confirmation:
            dispatcher.utter_message(response="utter_access_request_tam_stopped")
            return []

        start_date, end_date = get_start_end_date_from_duration(duration)

        response, content = await get_roles_for_tam(tracker)
        if not response.ok or "data" not in content:
            dispatcher.utter_message(response="utter_access_request_tam_error")
            return []

        roles = format_roles_list_for_tam(content["data"])

        body = format_access_request_tam(
            account_id, org_id, start_date, end_date, roles
        )

        response = await send_rbac_tam_request(tracker, body)
        if not response.ok:
            dispatcher.utter_message(response="utter_access_request_tam_error")
            return []

        dispatcher.utter_message(response="utter_access_request_tam_success")

        return []


async def get_roles_for_tam(tracker):
    return await send_console_request(
        "rbac",
        "/api/rbac/v1/roles/?system=true&limit=9999&order_by=display_name&add_fields=groups_in_count",
        tracker,
        method="get",
        fetch_content=True,
    )


def format_roles_list_for_tam(data: List[Dict[str, Any]]):
    names = []
    for role in data:
        names.append(role.get("name"))
    return names


def format_access_request_tam(
    account_id: str, org_id: str, start_date: str, end_date: str, roles: List[str]
):
    return {
        "target_account": account_id,
        "target_org": org_id,
        "start_date": start_date,
        "end_date": end_date,
        "roles": roles,
    }


async def send_rbac_tam_request(tracker: Tracker, body: Dict[str, Any]):
    if app.is_running_locally:
        print("called send_rbac_tam_request in local envionment with body: ", body)

        from unittest.mock import Mock

        mock_response = Mock()
        mock_response.ok = True

        return mock_response

    # POST https://console.stage.redhat.com/api/rbac/v1/cross-account-requests/
    return await send_console_request(
        "rbac",
        "/api/rbac/v1/cross-account-requests/",
        tracker,
        method="post",
        json=body,
        fetch_content=False,
    )
