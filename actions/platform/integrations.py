from abc import abstractmethod
from typing import List, Dict, Text, Any
from urllib.parse import urlparse

from rasa_sdk import FormValidationAction, Tracker, Action
from rasa_sdk.events import SlotSet, EventType, ActiveLoop
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict

from actions.slot_match import FuzzySlotMatch, FuzzySlotMatchOption, resolve_slot_match
from common.requests import send_console_request

communication_slot_match = FuzzySlotMatch(
    "integration_setup_type",
    [
        FuzzySlotMatchOption("google_chat", ["google chat", "google"]),
        FuzzySlotMatchOption("teams", ["microsoft office teams", "teams"]),
        FuzzySlotMatchOption("slack", ["slack"]),
    ],
)

reporting_slot_match = FuzzySlotMatch(
    "integration_setup_type",
    [
        FuzzySlotMatchOption("ansible", ["event driven ansible", "ansible"]),
        FuzzySlotMatchOption("service-now", ["service now", "servicenow"]),
        FuzzySlotMatchOption("splunk", ["splunk"]),
    ],
)

integrations_slot_match = FuzzySlotMatch(
    "integration_setup_kind",
    [
        FuzzySlotMatchOption("cloud"),
        FuzzySlotMatchOption("red_hat", ["red hat", "redhat"]),
        FuzzySlotMatchOption("communications", sub_options=communication_slot_match),
        FuzzySlotMatchOption(
            "reporting",
            [
                "reporting & automation",
                "reporting and automation",
                "reporting",
                "automation",
            ],
            sub_options=reporting_slot_match,
        ),
        FuzzySlotMatchOption("webhook"),
    ],
)


def get_communications_integration_type_name(raw_type: str):
    if raw_type == "google_chat":
        return "Google Chat"
    if raw_type == "teams":
        return "Microsoft Office Teams"
    if raw_type == "slack":
        return "Slack"


def get_reporting_integration_type_name(raw_type: str):
    if raw_type == "ansible":
        return "Event-Driven Ansible"
    if raw_type == "service-now":
        return "ServiceNow"
    if raw_type == "splunk":
        return "Splunk"


class IntegrationSetup(FormValidationAction):
    def name(self) -> str:
        return "validate_form_integration_setup"

    async def run(
        self,
        dispatcher: "CollectingDispatcher",
        tracker: "Tracker",
        domain: "DomainDict",
    ) -> List[EventType]:
        events = await super().run(dispatcher, tracker, domain)
        if tracker.get_slot("requested_slot") == "integration_setup_kind":
            resolved_match = resolve_slot_match(
                tracker.latest_message["text"], integrations_slot_match
            )
            if len(resolved_match) > 0:
                for resolved_slot in resolved_match:
                    events.append(SlotSet(resolved_slot, resolved_match[resolved_slot]))
            else:
                dispatcher.utter_message(response="utter_integration_kind_not_found")
                events.append(SlotSet("requested_slot", None))
                events.append(ActiveLoop(None))
                events.append(SlotSet("requested_slot", "integration_setup_kind"))
                events.append(ActiveLoop("form_integration_setup"))

        return events

    # We are processing in the `run` method, but this ensures we don't break out of the form.
    async def extract_integration_setup_kind(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict
    ) -> Dict[Text, Any]:
        return {"integration_setup_kind": None}

    async def validate_integration_setup_kind(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        return {"integration_setup_kind": slot_value}


class IntegrationSetupInit(Action):

    def name(self) -> Text:
        return "form_integration_setup_init"

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[Dict[Text, Any]]:
        return [
            SlotSet("integration_setup_kind"),
            SlotSet("integration_setup_walk_me"),
            SlotSet("integration_setup_name"),
            SlotSet("integration_setup_create_other"),
            SlotSet("integration_setup_url"),
            SlotSet("integration_setup_use_secret"),
            SlotSet("integration_setup_secret"),
            SlotSet("integration_setup_redhat_operator_installed"),
            SlotSet("integration_setup_redhat_cluster_identifier"),
            SlotSet("integration_setup_type"),
        ]


class IntegrationSetupCommon(FormValidationAction):

    @abstractmethod
    def walk_template(self) -> Text:
        raise NotImplementedError(
            f"walk_template was not implemented in {self.__class__.__name__}"
        )

    @abstractmethod
    async def process_data(
        self,
        tracker: Tracker,
        dispatcher: CollectingDispatcher,
        next_events: List[EventType],
    ) -> List[EventType]:
        raise NotImplementedError(
            f"process_data was not implemented in {self.__class__.__name__}"
        )

    @abstractmethod
    def create_template(self) -> List[Text]:
        raise NotImplementedError(
            f"create_template was not implemented in {self.__class__.__name__}"
        )

    async def run(
        self,
        dispatcher: "CollectingDispatcher",
        tracker: "Tracker",
        domain: "DomainDict",
    ) -> List[EventType]:
        next_events = await super().run(dispatcher, tracker, domain)

        for event in next_events:
            if event["event"] == "slot":
                if (
                    event["name"] == "integration_setup_walk_me"
                    and event["value"] is True
                ):
                    for template in self.create_template():
                        dispatcher.utter_message(response=template)

        only_show_me_where = tracker.get_slot("integration_setup_walk_me") is False
        create_other_was_requested = (
            tracker.get_slot("requested_slot") == "integration_setup_create_other"
        )

        if (
            not create_other_was_requested
            and not only_show_me_where
            and await self.all_required_slots_are_set(dispatcher, tracker, domain)
        ):
            return await self.process_data(tracker, dispatcher, next_events)

        return next_events

    async def all_required_slots_are_set(
        self,
        dispatcher: "CollectingDispatcher",
        tracker: "Tracker",
        domain: "DomainDict",
    ) -> bool:
        for slot in await self.required_slots(
            self.domain_slots(domain), dispatcher, tracker, domain
        ):
            if slot == "integration_setup_create_other":
                continue
            if tracker.get_slot(slot) is None:
                return False

        return True

    async def extract_integration_setup_walk_me(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict
    ) -> Dict[Text, Any]:
        if tracker.get_slot("requested_slot") == "integration_setup_walk_me":
            if tracker.latest_message["intent"]["name"] == "intent_core_learn_more":
                dispatcher.utter_message(response=self.walk_template())
                return {"integration_setup_walk_me": False, "requested_slot": None}
            elif tracker.latest_message["intent"]["name"] == "intent_core_guide_me":
                return {"integration_setup_walk_me": True}

        return {}

    async def validate_integration_setup_walk_me(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        return {"integration_setup_walk_me": slot_value}

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
        return {"integration_setup_name": slot_value}

    async def extract_integration_setup_url(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict
    ) -> Dict[Text, Any]:
        # Validate URL
        if tracker.get_slot("requested_slot") == "integration_setup_url":
            try:
                result = urlparse(tracker.latest_message["text"])
                if result.scheme != "https":
                    dispatcher.utter_message(text="The URL is not using https.")
                    dispatcher.utter_message(
                        response="utter_integration_setup_validation_error"
                    )
                    return {"integration_setup_url": None}

            except AttributeError:
                dispatcher.utter_message(
                    response="utter_integration_setup_validation_error"
                )
                return {"integration_setup_url": None}

            return {"integration_setup_url": tracker.latest_message["text"]}

        return {}

    async def validate_integration_setup_url(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        return {"integration_setup_url": slot_value}

    async def extract_integration_setup_create_other(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict
    ) -> Dict[Text, Any]:
        if tracker.get_slot("requested_slot") == "integration_setup_create_other":
            if tracker.latest_message["intent"]["name"] == "intent_core_yes":
                return {
                    slot: None if slot != "integration_setup_walk_me" else True
                    for slot in self.domain_slots(domain)
                }

            elif tracker.latest_message["intent"]["name"] == "intent_core_no":
                return {"integration_setup_create_other": False}

        return {}

    async def validate_integration_setup_create_other(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        return {"integration_setup_create_other": slot_value}

    async def extract_integration_setup_use_secret(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict
    ) -> Dict[Text, Any]:
        if tracker.get_slot("requested_slot") == "integration_setup_use_secret":
            if tracker.latest_message["intent"]["name"] == "intent_core_yes":
                return {"integration_setup_use_secret": True}

            elif tracker.latest_message["intent"]["name"] == "intent_core_no":
                return {
                    "integration_setup_use_secret": False,
                    "integration_setup_secret": "",
                }

        return {}

    async def validate_integration_setup_use_secret(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        return {"integration_setup_use_secret": slot_value}

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

    async def required_slots(
        self,
        domain_slots: List[Text],
        dispatcher: "CollectingDispatcher",
        tracker: "Tracker",
        domain: "DomainDict",
    ) -> List[Text]:
        if tracker.get_slot("integration_setup_walk_me") is False:
            return ["integration_setup_walk_me"]

        return domain_slots


class IntegrationSetupRedHat(IntegrationSetupCommon):
    def name(self) -> Text:
        return "validate_form_integration_setup_redhat"

    def walk_template(self) -> Text:
        return "utter_integration_setup_redhat_go"

    async def validate_integration_setup_name(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        response, content = await send_console_request(
            "sources",
            "/api/sources/v3.1/graphql",
            tracker,
            method="post",
            json={
                "query": f'{{ sources(filter: {{name: "name", value: "{slot_value}"}}){{ id, name }}}}'
            },
        )

        if response.ok and len(content.get("data").get("sources")) == 0:
            return {"integration_setup_name": slot_value}
        else:
            dispatcher.utter_message(text="That name is taken. Try another.")
            return {"integration_setup_name": None}

    async def process_data(
        self,
        tracker: Tracker,
        dispatcher: CollectingDispatcher,
        next_events: List[EventType],
    ) -> List[EventType]:
        response, content = await send_console_request(
            "sources",
            "/api/sources/v3.1/bulk_create",
            tracker,
            method="post",
            json={
                "applications": [
                    {
                        "application_type_id": "2",
                        "extra": {"hcs": False},
                        "source_name": tracker.get_slot("integration_setup_name"),
                    }
                ],
                "authentications": [
                    {
                        "authtype": "token",
                        "resource_name": "/insights/platform/cost-management",
                        "resource_type": "application",
                    }
                ],
                "endpoints": [],
                "sources": [
                    {
                        "name": tracker.get_slot("integration_setup_name"),
                        "source_ref": tracker.get_slot(
                            "integration_setup_redhat_cluster_identifier"
                        ),
                        "source_type_name": "openshift",
                    }
                ],
            },
        )

        if response.ok:
            dispatcher.utter_message(
                response="utter_integration_setup_redhat_walk_success"
            )
        else:
            dispatcher.utter_message(response="utter_integration_setup_error")
            next_events.append(SlotSet("requested_slot", None))
            next_events.append(ActiveLoop(None))
            next_events.append(ActiveLoop("form_closing"))

        return next_events

    def create_template(self) -> List[Text]:
        return [
            "utter_integration_setup_redhat_walk_1",
            "utter_integration_setup_redhat_walk_2",
        ]

    async def extract_integration_setup_redhat_operator_installed(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict
    ) -> Dict[Text, Any]:
        if (
            tracker.get_slot("requested_slot")
            == "integration_setup_redhat_operator_installed"
        ):
            if tracker.latest_message["intent"]["name"] == "intent_core_yes":
                return {"integration_setup_redhat_operator_installed": True}

            elif tracker.latest_message["intent"]["name"] == "intent_core_no":
                dispatcher.utter_message(
                    json_message={
                        "type": "command",
                        "command": "redirect",
                        "params": {
                            "url": "https://access.redhat.com/documentation/en-us/cost_management_service/1-latest#installing-cost-operator_adding-an-ocp-source"
                        },
                    }
                )
                return {"integration_setup_redhat_operator_installed": False}

        return {}

    async def validate_integration_setup_redhat_operator_installed(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        return {"integration_setup_redhat_operator_installed": slot_value}

    async def extract_integration_setup_redhat_cluster_identifier(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict
    ) -> Dict[Text, Any]:
        if (
            tracker.get_slot("requested_slot")
            == "integration_setup_redhat_cluster_identifier"
        ):
            return {
                "integration_setup_redhat_cluster_identifier": tracker.latest_message[
                    "text"
                ]
            }
        return {}

    async def validate_integration_setup_redhat_cluster_identifier(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        return {"integration_setup_redhat_cluster_identifier": slot_value}


class IntegrationSetupCommunications(IntegrationSetupCommon):
    def name(self) -> Text:
        return "validate_form_integration_setup_communications"

    def walk_template(self) -> Text:
        return "utter_integration_setup_communications_go"

    async def process_data(
        self,
        tracker: Tracker,
        dispatcher: CollectingDispatcher,
        next_events: List[EventType],
    ) -> List[EventType]:
        response = await send_console_request(
            "notifications",
            "/api/integrations/v1.0/endpoints",
            tracker,
            method="post",
            json={
                "enabled": True,
                "description": "Endpoint created by Virtual assistant",
                "name": tracker.get_slot("integration_setup_name"),
                "properties": {
                    "method": "POST",
                    "disable_ssl_verification": False,
                    "url": tracker.get_slot("integration_setup_url"),
                    "secret_token": (
                        tracker.get_slot("integration_setup_secret")
                        if tracker.get_slot("integration_setup_use_secret") is True
                        else None
                    ),
                },
                "type": "camel",
                "sub_type": tracker.get_slot("integration_setup_type"),
            },
            fetch_content=False,
        )

        if response.ok:
            dispatcher.utter_message(
                response="utter_integration_setup_communications_success",
                integration_type_name=get_communications_integration_type_name(
                    tracker.get_slot("integration_setup_type")
                ),
            )
        else:
            dispatcher.utter_message(response="utter_integration_setup_error")
            next_events.append(SlotSet("requested_slot", None))
            next_events.append(ActiveLoop(None))
            next_events.append(ActiveLoop("form_closing"))

        return next_events

    def create_template(self) -> List[Text]:
        return []

    def extract_integration_setup_type(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict
    ) -> Dict[Text, Any]:
        if tracker.get_slot("requested_slot") == "integration_setup_type":
            resolved = resolve_slot_match(
                tracker.latest_message["text"], communication_slot_match
            )
            if len(resolved) > 0:
                return resolved

        return {}

    async def validate_integration_setup_type(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        return {"integration_setup_type": slot_value}


class AskForIntegrationSetupWalkMe(Action):
    def name(self) -> Text:
        return "action_ask_integration_setup_walk_me"

    def get_reporting_integration_type_display_name(self, tracker: Tracker):
        integration_type = tracker.get_slot("integration_setup_type")
        if integration_type:
            return get_reporting_integration_type_name(integration_type)
        return ""

    def get_communication_integration_type_display_name(self, tracker: Tracker):
        integration_type = tracker.get_slot("integration_setup_type")
        if integration_type:
            return get_communications_integration_type_name(integration_type)
        return ""

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        if tracker.active_loop_name == "form_integration_setup_communications":
            dispatcher.utter_message(
                response="utter_form_integration_setup_reporting_integration_setup_walk_me",
                integration_type_display_name=self.get_communication_integration_type_display_name(
                    tracker
                ),
            )
        elif tracker.active_loop_name == "form_integration_setup_reporting":
            dispatcher.utter_message(
                response="utter_form_integration_setup_communications_integration_setup_walk_me",
                integration_type_display_name=self.get_reporting_integration_type_display_name(
                    tracker
                ),
            )

        return []


class IntegrationSetupReporting(IntegrationSetupCommon):
    def name(self) -> Text:
        return "validate_form_integration_setup_reporting"

    def walk_template(self) -> Text:
        return "utter_integration_setup_communications_go"

    def get_integration_type(self, raw_type: str) -> Text:
        if raw_type == "ansible":
            return "ansible"

        return "camel"

    def get_integration_sub_type(self, raw_type: str) -> Text:
        if raw_type == "ansible":
            return None

        if raw_type == "service-now":
            return "servicenow"

        return raw_type

    async def process_data(
        self,
        tracker: Tracker,
        dispatcher: CollectingDispatcher,
        next_events: List[EventType],
    ) -> List[EventType]:
        response = await send_console_request(
            "notifications",
            "/api/integrations/v1.0/endpoints",
            tracker,
            method="post",
            json={
                "enabled": True,
                "description": "Endpoint created by Virtual assistant",
                "name": tracker.get_slot("integration_setup_name"),
                "properties": {
                    "method": "POST",
                    "disable_ssl_verification": False,
                    "url": tracker.get_slot("integration_setup_url"),
                    "secret_token": (
                        tracker.get_slot("integration_setup_secret")
                        if tracker.get_slot("integration_setup_use_secret") is True
                        else None
                    ),
                },
                "type": self.get_integration_type(
                    tracker.get_slot("integration_setup_type")
                ),
                "sub_type": self.get_integration_sub_type(
                    tracker.get_slot("integration_setup_type")
                ),
            },
            fetch_content=False,
        )

        if response.ok:
            dispatcher.utter_message(
                response="utter_integration_setup_reporting_success",
                integration_type_name=get_reporting_integration_type_name(
                    tracker.get_slot("integration_setup_type")
                ),
            )
        else:
            dispatcher.utter_message(response="utter_integration_setup_error")
            next_events.append(SlotSet("requested_slot", None))
            next_events.append(ActiveLoop(None))
            next_events.append(ActiveLoop("form_closing"))

        return next_events

    def create_template(self) -> List[Text]:
        return []

    def extract_integration_setup_type(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict
    ) -> Dict[Text, Any]:
        if tracker.get_slot("requested_slot") == "integration_setup_type":
            resolved = resolve_slot_match(
                tracker.latest_message["text"], reporting_slot_match
            )
            if len(resolved) > 0:
                return resolved

        return {}

    async def validate_integration_setup_type(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        return {"integration_setup_type": slot_value}


class IntegrationSetupWebhook(IntegrationSetupCommon):
    def name(self) -> Text:
        return "validate_form_integration_setup_webhook"

    def walk_template(self) -> Text:
        return "utter_integration_setup_webhook_go"

    async def process_data(
        self,
        tracker: Tracker,
        dispatcher: CollectingDispatcher,
        next_events: List[EventType],
    ) -> List[EventType]:
        response = await send_console_request(
            "notifications",
            "/api/integrations/v1.0/endpoints",
            tracker,
            method="post",
            json={
                "enabled": True,
                "description": "Endpoint created by Virtual assistant",
                "name": tracker.get_slot("integration_setup_name"),
                "properties": {
                    "method": "POST",
                    "disable_ssl_verification": False,
                    "url": tracker.get_slot("integration_setup_url"),
                    "secret_token": (
                        tracker.get_slot("integration_setup_secret")
                        if tracker.get_slot("integration_setup_use_secret") is True
                        else None
                    ),
                },
                "type": "webhook",
            },
            fetch_content=False,
        )

        if response.ok:
            dispatcher.utter_message(response="utter_integration_setup_webhook_success")
        else:
            dispatcher.utter_message(response="utter_integration_setup_error")
            next_events.append(SlotSet("requested_slot", None))
            next_events.append(ActiveLoop(None))
            next_events.append(ActiveLoop("form_closing"))

        return next_events

    def create_template(self) -> List[Text]:
        return []
