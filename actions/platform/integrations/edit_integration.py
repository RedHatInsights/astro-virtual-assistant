import json
from abc import abstractmethod
from json import JSONDecodeError
from typing import Text, Dict, List, Any, Optional
from urllib.parse import urlparse

from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.events import SlotSet, EventType
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict

from actions.platform.integrations import (
    all_required_slots_are_set,
    is_source_name_valid,
    validate_integration_url,
)
from actions.slot_match import FuzzySlotMatch, FuzzySlotMatchOption, resolve_slot_match
from common.requests import send_console_request

integration_edit_what_match = FuzzySlotMatch(
    "integration_edit_what",
    [
        FuzzySlotMatchOption("enable", ["enable", "turn on", "resume"]),
        FuzzySlotMatchOption("disable", ["disable", "turn off", "cancel", "pause"]),
        FuzzySlotMatchOption("delete", ["delete", "erase", "remove"]),
        FuzzySlotMatchOption("data", ["edit", "update", "modify", "change"]),
    ],
)

integration_edit_data_what_slot = "integration_edit_data_what"
integration_edit_data_what_option_name = FuzzySlotMatchOption("name", ["name"])
integration_edit_data_what_option_url = FuzzySlotMatchOption("url", ["url", "endpoint"])
integration_edit_data_what_option_secret = FuzzySlotMatchOption(
    "secret", ["secret", "token"]
)

reporting_types = ["ansible"]
communications_camel_subtypes = ["google_chat", "teams", "slack"]
reporting_camel_subtypes = ["servicenow", "splunk"]

integration_edit_data_what_valid = {
    "red_hat": ["name"],
    "communications": ["name", "url"],
    "reporting": ["name", "url", "secret"],
    "webhook": ["name", "url", "secret"],
}

MAX_NUMBER_OF_INTEGRATIONS = 5


class IntegrationEditInit(Action):

    def name(self) -> Text:
        return "form_integration_edit_init"

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[Dict[Text, Any]]:
        return [
            SlotSet("integration_setup_name"),
            SlotSet("integration_setup_url"),
            SlotSet("integration_setup_secret"),
            SlotSet("integration_edit_what"),
            SlotSet("integration_edit_integration_search"),
            SlotSet("integration_edit_integration"),
            SlotSet("integration_edit_integration_confirm"),
            SlotSet("integration_edit_data_what"),
            SlotSet("integration_edit_data_more_changes"),
            SlotSet("integration_edit_data_other_integration"),
        ]


class IntegrationEdit(FormValidationAction):

    def name(self) -> Text:
        return "validate_form_integration_edit"

    async def extract_integration_edit_what(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict
    ) -> Dict[Text, Any]:
        if tracker.get_slot("requested_slot") == "integration_edit_what":
            resolved = resolve_slot_match(
                tracker.latest_message["text"], integration_edit_what_match
            )
            if len(resolved) > 0:
                return resolved

            return {"integration_edit_what": "other"}

        return {}

    async def validate_integration_edit_what(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        return {"integration_edit_what": slot_value}


class IntegrationButtonBuilder:

    def integration_buttons(self, integrations: Dict):
        buttons = []
        for index, integration in enumerate(integrations):
            buttons.append(
                {
                    "title": integration["name"],
                    "payload": f"integration:{json.dumps(integration)}",
                }
            )

        return buttons

    def notifications_type_to_group(self, integration):
        if integration["type"] == "webhook":
            return "webhook"
        if integration["type"] in reporting_types:
            return "reporting"

        if integration["type"] == "camel":
            if integration["sub_type"] in communications_camel_subtypes:
                return "communications"
            if integration["sub_type"] in reporting_camel_subtypes:
                return "reporting"

    async def fetch_integrations(
        self, tracker: Tracker, enabled: Optional[bool] = None
    ) -> (Dict, bool):
        search = tracker.get_slot("integration_edit_integration_search") or ""
        integrations = []

        has_errors = False

        prepend_camel = lambda s: f"camel:{s}"
        params = {
            "name": search,
            "type": [
                "webhook",
                *reporting_types,
                *map(prepend_camel, reporting_camel_subtypes),
                *map(prepend_camel, communications_camel_subtypes),
            ],
            "limit": MAX_NUMBER_OF_INTEGRATIONS,
        }

        if enabled is not None:
            params["active"] = str(enabled)

        response, content = await send_console_request(
            "notifications",
            f"/api/integrations/v1.0/endpoints",
            tracker,
            params=params,
        )

        if response.ok:
            for integration in content["data"]:
                integrations.append(
                    {
                        "name": integration["name"],
                        "enabled": integration["enabled"],
                        "type": "notifications",
                        "group": self.notifications_type_to_group(integration),
                        "id": integration["id"],
                    }
                )
        else:
            has_errors = True

        params = {
            "filter[name][contains_i]": search,
            "limit": MAX_NUMBER_OF_INTEGRATIONS,
        }

        if enabled is not None:
            if enabled is True:
                params["filter[paused_at][nil]"] = "1"
            else:
                params["filter[paused_at][not_nil]"] = "1"

        response, content = await send_console_request(
            "sources", f"/api/sources/v3.1/sources", tracker, params=params
        )

        if response.ok:
            for integration in content["data"]:
                integrations.append(
                    {
                        "name": integration["name"],
                        "enabled": (
                            True
                            if "paused_at" not in integration
                            or integration["paused_at"] is None
                            else False
                        ),
                        "type": "red_hat",
                        "group": "red_hat",
                        "id": integration["id"],
                    }
                )
        else:
            has_errors = True

        return integrations[:5], has_errors


class AskIntegrationDisable(Action, IntegrationButtonBuilder):
    def name(self) -> Text:
        return "action_ask_form_integration_edit_disable_integration_edit_integration_search"

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        integrations, has_errors = await self.fetch_integrations(tracker, enabled=True)

        dispatcher.utter_message(
            response="utter_form_integration_edit_disable_integration_edit_integration_search"
        )

        # Silently ignore errors this at this point, we are going to try again in the next message
        if not has_errors and len(integrations) > 0:
            buttons = self.integration_buttons(integrations)
            buttons.append(
                {
                    "title": "I want to do something else",
                    "payload": "/intent_core_something_else",
                }
            )

            dispatcher.utter_message(
                response="utter_integration_select_or_type", buttons=buttons
            )

        return []


class AskIntegrationEnable(Action, IntegrationButtonBuilder):
    def name(self) -> Text:
        return "action_ask_form_integration_edit_enable_integration_edit_integration_search"

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        integrations, has_errors = await self.fetch_integrations(tracker, enabled=False)

        dispatcher.utter_message(
            response="utter_form_integration_edit_enable_integration_edit_integration_search"
        )

        # Silently ignore errors this at this point, we are going to try again in the next message
        if not has_errors and len(integrations) > 0:
            buttons = self.integration_buttons(integrations)
            buttons.append(
                {
                    "title": "I want to do something else",
                    "payload": "/intent_core_something_else",
                }
            )

            dispatcher.utter_message(
                response="utter_integration_select_or_type", buttons=buttons
            )

        return []


class AskIntegrationEditWhat(Action, IntegrationButtonBuilder):
    def name(self) -> Text:
        return "action_ask_integration_edit_integration"

    def utter_results(self, integrations: Dict, dispatcher: CollectingDispatcher):
        buttons = self.integration_buttons(integrations)
        buttons.append(
            {
                "title": "I want to do something else",
                "payload": "/intent_core_something_else",
            }
        )
        dispatcher.utter_message(
            response="utter_integration_results_found", buttons=buttons
        )

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        if tracker.latest_message["intent"]["name"] == "intent_core_something_else":
            return []

        enabled_integrations = None
        if tracker.active_loop_name == "form_integration_edit_disable":
            enabled_integrations = True
        elif tracker.active_loop_name == "form_integration_edit_enable":
            enabled_integrations = False

        integrations, has_errors = await self.fetch_integrations(
            tracker, enabled=enabled_integrations
        )

        if len(integrations) > 0:
            self.utter_results(integrations, dispatcher)
        elif has_errors:
            dispatcher.utter_message(response="utter_integration_error_fetching")
        else:
            dispatcher.utter_message(response="utter_integration_not_found")
            return [
                SlotSet("integration_edit_integration_search"),
                SlotSet("requested_slot", "integration_edit_integration_search"),
            ]

        return []


class AskIntegrationEditWhatData(Action):
    def name(self) -> Text:
        return "action_ask_integration_edit_data_what"

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        integration = json.loads(tracker.get_slot("integration_edit_integration"))

        for data_what in integration_edit_data_what_valid[integration["group"]]:
            if data_what == "name":
                buttons = [{"title": "Rename the integration", "payload": "name"}]
            elif data_what == "url":
                buttons.append({"title": "Update the endpoint URL", "payload": "url"})
            elif data_what == "secret":
                buttons.append(
                    {"title": "Update the secret token", "payload": "secret"}
                )

        buttons.append({"title": "Something else", "payload": "other"})

        dispatcher.utter_message(
            response="utter_integration_edit_data_what", buttons=buttons
        )
        return []


class IntegrationEditCommon(FormValidationAction):

    @abstractmethod
    def name(self) -> Text:
        return super().name()

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        events = await super().run(dispatcher, tracker, domain)
        return events

    async def extract_integration_edit_integration_search(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict
    ) -> Dict[Text, Any]:
        if (
            tracker.get_slot("requested_slot") == "integration_edit_integration_search"
            and tracker.latest_message["intent"]["name"] != "intent_core_something_else"
        ):
            message = tracker.latest_message["text"]
            if tracker.latest_message["text"].startswith("integration:"):

                integration_data = message[len("integration:") :]
                try:
                    integration = json.loads(integration_data)
                    if (
                        integration["type"] == "red_hat"
                        or integration["type"] == "notifications"
                    ):
                        return {
                            "integration_edit_integration_search": integration["name"],
                            "integration_edit_integration": integration_data,
                        }
                finally:
                    pass

            return {"integration_edit_integration_search": message}

        return {}

    async def validate_integration_edit_integration_search(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        return {"integration_edit_integration_search": slot_value}

    async def extract_integration_edit_integration(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict
    ) -> Dict[Text, Any]:
        if tracker.get_slot("requested_slot") == "integration_edit_integration":
            message: Text = tracker.latest_message["text"]
            if message.startswith("integration:"):
                integration_data = message[len("integration:") :]
                try:
                    integration = json.loads(integration_data)
                    if (
                        integration["type"] == "red_hat"
                        or integration["type"] == "notifications"
                    ):
                        return {"integration_edit_integration": integration_data}
                except JSONDecodeError:
                    pass

            elif (
                tracker.latest_message["intent"]["name"] == "intent_core_something_else"
            ):
                return {}

            return {
                "integration_edit_integration": None,
                "integration_edit_integration_search": message,
            }

        return {}

    async def validate_integration_edit_integration(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        return {"integration_edit_integration": slot_value}

    async def extract_integration_edit_integration_confirm(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict
    ) -> Dict[Text, Any]:
        if tracker.get_slot("requested_slot") == "integration_edit_integration_confirm":
            return {
                "integration_edit_integration_confirm": tracker.latest_message[
                    "intent"
                ]["name"]
                == "intent_core_yes"
            }

        return {}

    async def validate_integration_edit_integration_confirm(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        return {"integration_edit_integration_confirm": slot_value}


class IntegrationEditEnable(IntegrationEditCommon):

    def name(self) -> Text:
        return "validate_form_integration_edit_enable"

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        events = await super().run(dispatcher, tracker, domain)

        if await all_required_slots_are_set(self, dispatcher, tracker, domain):
            integration = json.loads(tracker.get_slot("integration_edit_integration"))

            response = None
            if integration["type"] == "red_hat":
                response = await send_console_request(
                    "sources",
                    f"/api/sources/v3.1/sources/{integration['id']}/unpause",
                    tracker,
                    method="POST",
                    fetch_content=False,
                )
            elif integration["type"] == "notifications":
                response = await send_console_request(
                    "notifications",
                    f"/api/integrations/v1.0/endpoints/{integration['id']}/enable",
                    tracker,
                    method="PUT",
                    fetch_content=False,
                )

            if response is not None and response.ok:
                dispatcher.utter_message(response="utter_integration_edit_enable_done")
            else:
                dispatcher.utter_message(response="utter_integration_error")

        return events


class IntegrationEditDisable(IntegrationEditCommon):

    def name(self) -> Text:
        return "validate_form_integration_edit_disable"

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        events = await super().run(dispatcher, tracker, domain)

        if await all_required_slots_are_set(self, dispatcher, tracker, domain):
            integration = json.loads(tracker.get_slot("integration_edit_integration"))

            response = None
            if integration["type"] == "red_hat":
                response = await send_console_request(
                    "sources",
                    f"/api/sources/v3.1/sources/{integration['id']}/pause",
                    tracker,
                    method="POST",
                    fetch_content=False,
                )
            elif integration["type"] == "notifications":
                response = await send_console_request(
                    "notifications",
                    f"/api/integrations/v1.0/endpoints/{integration['id']}/enable",
                    tracker,
                    method="DELETE",
                    fetch_content=False,
                )

            if response is not None and response.ok:
                dispatcher.utter_message(response="utter_integration_edit_disable_done")
            else:
                dispatcher.utter_message(response="utter_integration_error")

        return events


class IntegrationEditDelete(IntegrationEditCommon):

    def name(self) -> Text:
        return "validate_form_integration_edit_delete"

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        events = await super().run(dispatcher, tracker, domain)

        if await all_required_slots_are_set(self, dispatcher, tracker, domain):
            if tracker.get_slot("integration_edit_integration_confirm") is True:
                integration = json.loads(
                    tracker.get_slot("integration_edit_integration")
                )

                response = None
                if integration["type"] == "red_hat":
                    response = await send_console_request(
                        "sources",
                        f"/api/sources/v3.1/sources/{integration['id']}",
                        tracker,
                        method="DELETE",
                        fetch_content=False,
                    )
                elif integration["type"] == "notifications":
                    response = await send_console_request(
                        "notifications",
                        f"/api/integrations/v1.0/endpoints/{integration['id']}",
                        tracker,
                        method="DELETE",
                        fetch_content=False,
                    )

                if response is not None and response.ok:
                    dispatcher.utter_message(
                        response="utter_integration_edit_delete_confirm_yes"
                    )
                else:
                    dispatcher.utter_message(response="utter_integration_error")
            else:
                dispatcher.utter_message(
                    response="utter_integration_edit_delete_confirm_no"
                )

        return events


class IntegrationEditData(IntegrationEditCommon):

    def name(self) -> Text:
        return "validate_form_integration_edit_data"

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        events = await super().run(dispatcher, tracker, domain)

        integration_edit_data_what = tracker.get_slot("integration_edit_data_what")
        requested_slot = tracker.get_slot("requested_slot")

        if (
            requested_slot == "integration_edit_data_what"
            and integration_edit_data_what is not None
        ):
            integration = json.loads(tracker.get_slot("integration_edit_integration"))
            if integration["type"] == "red_hat" and not integration["enabled"]:
                dispatcher.utter_message(
                    response="utter_integration_edit_data_what_name_redhat_disabled"
                )
                return events + [SlotSet("requested_slot")]

        if requested_slot == "integration_edit_data_more_changes" and tracker.get_slot(
            "integration_edit_data_more_changes"
        ):
            return [
                SlotSet("integration_edit_data_what"),
                SlotSet("integration_setup_name"),
                SlotSet("integration_setup_url"),
                SlotSet("integration_setup_secret"),
                SlotSet("integration_edit_data_more_changes"),
                SlotSet("integration_edit_data_other_integration"),
            ]

        if (
            requested_slot == "integration_edit_data_other_integration"
            and tracker.get_slot("integration_edit_data_other_integration")
        ):
            return [
                SlotSet("integration_edit_integration_search"),
                SlotSet("integration_edit_integration"),
                SlotSet("integration_edit_data_what"),
                SlotSet("integration_setup_name"),
                SlotSet("integration_setup_url"),
                SlotSet("integration_setup_secret"),
                SlotSet("integration_edit_data_more_changes"),
                SlotSet("integration_edit_data_other_integration"),
            ]

        if (
            integration_edit_data_what is not None
            and integration_edit_data_what != "other"
        ):
            integration_setup_name = tracker.get_slot("integration_setup_name")
            integration_setup_url = tracker.get_slot("integration_setup_url")
            integration_setup_secret = tracker.get_slot("integration_setup_secret")

            if (
                integration_edit_data_what == "name"
                and requested_slot == "integration_setup_name"
                and integration_setup_name is not None
            ):
                await self.update_name(tracker, dispatcher, integration_setup_name)
            elif (
                integration_edit_data_what == "url"
                and requested_slot == "integration_setup_url"
                and integration_setup_url is not None
            ):
                await self.update_url(tracker, dispatcher, integration_setup_url)
            elif (
                integration_edit_data_what == "secret"
                and requested_slot == "integration_setup_secret"
                and integration_setup_secret is not None
            ):
                await self.update_secret(tracker, dispatcher, integration_setup_secret)

        return events

    async def retrieve_notification_endpoint(self, tracker: Tracker, endpoint_id: Text):
        return await send_console_request(
            "notifications", f"/api/integrations/v1.0/endpoints/{endpoint_id}", tracker
        )

    async def update_name(
        self, tracker: Tracker, dispatcher: CollectingDispatcher, name: Text
    ):
        integration = json.loads(tracker.get_slot("integration_edit_integration"))
        response = None

        if integration["type"] == "red_hat":
            response = await send_console_request(
                "sources",
                f"/api/sources/v3.1/sources/{integration['id']}",
                tracker,
                method="PATCH",
                fetch_content=False,
                json={"name": name},
            )
        elif integration["type"] == "notifications":
            response, integration_data = await self.retrieve_notification_endpoint(
                tracker, integration["id"]
            )
            if response.ok:
                integration_data["name"] = name
                response = await send_console_request(
                    "notifications",
                    f"/api/integrations/v1.0/endpoints/{integration['id']}",
                    tracker,
                    method="PUT",
                    json=integration_data,
                    fetch_content=False,
                )

        if response is not None and response.ok:
            dispatcher.utter_message(
                response="utter_integration_edit_data_what_name_success"
            )
        else:
            dispatcher.utter_message(response="utter_integration_error")

    async def update_url(
        self, tracker: Tracker, dispatcher: CollectingDispatcher, url: Text
    ):
        integration = json.loads(tracker.get_slot("integration_edit_integration"))
        response = None

        if integration["type"] == "notifications":
            response, integration_data = await self.retrieve_notification_endpoint(
                tracker, integration["id"]
            )
            if response.ok:
                integration_data["properties"]["url"] = url
                response = await send_console_request(
                    "notifications",
                    f"/api/integrations/v1.0/endpoints/{integration['id']}",
                    tracker,
                    method="PUT",
                    json=integration_data,
                    fetch_content=False,
                )

        if response is not None and response.ok:
            dispatcher.utter_message(
                response="utter_integration_edit_data_what_url_success"
            )
        else:
            dispatcher.utter_message(response="utter_integration_error")

    async def update_secret(
        self, tracker: Tracker, dispatcher: CollectingDispatcher, secret: Text
    ):
        integration = json.loads(tracker.get_slot("integration_edit_integration"))
        response = None

        if integration["type"] == "notifications":
            response, integration_data = await self.retrieve_notification_endpoint(
                tracker, integration["id"]
            )
            if response.ok:
                integration_data["properties"]["secret_token"] = secret
                response = await send_console_request(
                    "notifications",
                    f"/api/integrations/v1.0/endpoints/{integration['id']}",
                    tracker,
                    method="PUT",
                    json=integration_data,
                    fetch_content=False,
                )

        if response is not None and response.ok:
            dispatcher.utter_message(
                response="utter_integration_edit_data_what_secret_success"
            )
        else:
            dispatcher.utter_message(response="utter_integration_error")

    async def extract_integration_edit_data_what(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict
    ) -> Dict[Text, Any]:
        if tracker.get_slot("requested_slot") == "integration_edit_data_what":
            integration = json.loads(tracker.get_slot("integration_edit_integration"))

            match_options = []

            for data_what in integration_edit_data_what_valid[integration["group"]]:
                if data_what == "name":
                    match_options.append(integration_edit_data_what_option_name)
                elif data_what == "url":
                    match_options.append(integration_edit_data_what_option_url)
                elif data_what == "secret":
                    match_options.append(integration_edit_data_what_option_secret)

            resolved = resolve_slot_match(
                tracker.latest_message["text"],
                FuzzySlotMatch(
                    integration_edit_data_what_slot,
                    match_options,
                ),
            )
            if len(resolved) > 0:
                return resolved

            return {"integration_edit_data_what": "other"}

        return {}

    async def validate_integration_edit_data_what(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        return {"integration_edit_data_what": slot_value}

    async def extract_integration_setup_name(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict
    ) -> Dict[Text, Any]:
        if tracker.get_slot("requested_slot") == "integration_setup_name":
            return {"integration_setup_name": tracker.latest_message["text"]}

        return {}

    async def validate_integration_setup_name(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        if is_source_name_valid(tracker, slot_value):
            return {"integration_setup_name": slot_value}
        else:
            dispatcher.utter_message(response="utter_integration_name_used")
            return {"integration_setup_name": None}

    async def extract_integration_setup_url(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict
    ) -> Dict[Text, Any]:
        if tracker.get_slot("requested_slot") == "integration_setup_url":
            if validate_integration_url(dispatcher, tracker.latest_message["text"]):
                return {"integration_setup_url": tracker.latest_message["text"]}
            return {"integration_setup_url": None}

        return {}

    async def validate_integration_setup_url(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        return {"integration_setup_url": slot_value}

    async def extract_integration_setup_secret(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict
    ) -> Dict[Text, Any]:
        if tracker.get_slot("requested_slot") == "integration_setup_secret":
            return {"integration_setup_secret": tracker.latest_message["text"]}
        return {}

    async def validate_integration_setup_secret(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        return {"integration_setup_secret": slot_value}

    async def extract_integration_edit_data_more_changes(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict
    ) -> Dict[Text, Any]:
        if tracker.get_slot("requested_slot") == "integration_edit_data_more_changes":
            if tracker.latest_message["intent"]["name"] == "intent_core_yes":
                return {"integration_edit_data_more_changes": True}

            elif tracker.latest_message["intent"]["name"] == "intent_core_no":
                return {"integration_edit_data_more_changes": False}

        return {}

    async def validate_integration_edit_data_more_changes(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        return {"integration_edit_data_more_changes": slot_value}

    async def extract_integration_edit_data_other_integration(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict
    ) -> Dict[Text, Any]:
        if (
            tracker.get_slot("requested_slot")
            == "integration_edit_data_other_integration"
        ):
            if tracker.latest_message["intent"]["name"] == "intent_core_yes":
                return {"integration_edit_data_other_integration": True}

            elif tracker.latest_message["intent"]["name"] == "intent_core_no":
                return {"integration_edit_data_other_integration": False}

        return {}

    async def validate_integration_edit_data_other_integration(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        return {"integration_edit_data_other_integration": slot_value}

    async def required_slots(
        self,
        domain_slots: List[Text],
        dispatcher: "CollectingDispatcher",
        tracker: "Tracker",
        domain: "DomainDict",
    ) -> List[Text]:
        edit_what = tracker.get_slot("integration_edit_data_what")
        if edit_what is not None:
            required_slots = [*domain_slots]

            if edit_what == "name":
                required_slots.insert(
                    required_slots.index("integration_edit_data_what") + 1,
                    "integration_setup_name",
                )
            elif edit_what == "url":
                required_slots.insert(
                    required_slots.index("integration_edit_data_what") + 1,
                    "integration_setup_url",
                )
            elif edit_what == "secret":
                required_slots.insert(
                    required_slots.index("integration_edit_data_what") + 1,
                    "integration_setup_secret",
                )
            else:
                return ["integration_edit_data_what"]

            return required_slots

        return domain_slots
