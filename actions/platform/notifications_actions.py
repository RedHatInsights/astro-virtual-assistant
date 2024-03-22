from typing import Any, Text, Dict, List, Optional

from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from rasa_sdk.types import DomainDict

from actions.slot_match import FuzzySlotMatch, FuzzySlotMatchOption, resolve_slot_match

from common import logging
from common.header import Header
from common.requests import send_console_request


logger = logging.initialize_logging()

# Slots
_SLOT_IS_ORG_ADMIN = "is_org_admin"
NOTIF_BUNDLE = "notifications_bundle"
NOTIF_BUNDLE_OPT = "notifications_bundle_option"
NOTIF_EVENT = "notifications_event"
NOTIF_EVENT_OPT = "notifications_event_option"
NOTIF_BEHAVIOR_OPT = "notifications_behavior_option"
NOTIF_CONTACT_ADMIN = "notifications_contact_admin"

UNSURE_SERVICE = {"id": "unsure", "name": "unsure", "display_name": "unsure"}

service_match = FuzzySlotMatch(
    NOTIF_BUNDLE,
    [
        FuzzySlotMatchOption("Openshift", ["openshift", "open shift"]),
        FuzzySlotMatchOption("RHEL", ["rhel", "red hat enterprise linux", "linux"]),
        FuzzySlotMatchOption(
            "Core Console", ["core console", "console", "hcc", "platform"]
        ),
        FuzzySlotMatchOption(
            "unsure",
            [
                "not sure",
                "unsure",
                "idk",
                "I'm not sure",
                "no clue",
                "I have no idea",
                "other",
            ],
        ),
    ],
)

# going to continue to test phrases
service_opt_match = FuzzySlotMatch(
    NOTIF_BUNDLE_OPT,
    [
        FuzzySlotMatchOption(
            "manage events",
            [
                "manage events",
                "Manage my organization's event settings",
                "event settings",
                "org events",
            ],
        ),
        FuzzySlotMatchOption(
            "manage preferences",
            [
                "manage preferences",
                "manage my own notification preferences",
                "manage preferences for my current notifications",
                "preferences",
                "pref",
            ],
        ),
        FuzzySlotMatchOption(
            "contact admin",
            [
                "contact admin",
                "contact my org admin for me",
                "contact my organization's admin",
                "org admin",
                "admin",
            ],
        ),
        FuzzySlotMatchOption(
            "learn",
            [
                "learn more about notifications",
                "learn",
                "help",
                "docs",
                "documentation",
                "learn more",
                "learn about notifications",
                "learn about",
            ],
        ),
    ],
)

event_match = FuzzySlotMatch(
    NOTIF_EVENT,
    [],
)

event_opt_match = FuzzySlotMatch(
    NOTIF_EVENT_OPT,
    [
        FuzzySlotMatchOption("new", ["set up a new event", "add", "new event", "new"]),
        FuzzySlotMatchOption(
            "modify",
            [
                "modify settings for an event notification",
                "edit",
                "change",
                "modify",
                "existing",
            ],
        ),
        FuzzySlotMatchOption(
            "disable",
            [
                "disable an event notification",
                "disable notification please",
                "delete event",
                "remove",
                "delete",
                "disable",
            ],
        ),
    ],
)

behavior_opt_match = FuzzySlotMatch(
    NOTIF_BEHAVIOR_OPT,
    [
        FuzzySlotMatchOption(
            "attach", ["attach an existing behavior group", "attach", "existing"]
        ),
        FuzzySlotMatchOption(
            "create", ["create a new behavior group", "create", "new", "new behavior"]
        ),
        FuzzySlotMatchOption(
            "remove",
            [
                "remove an existing behavior group",
                "Remove existing behavior groups",
                "remove",
                "detach them",
                "delete",
            ],
        ),
    ],
)


class ValidateFormNotifications(FormValidationAction):
    def name(self) -> Text:
        return "validate_form_notifications"

    @staticmethod
    def extract_notifications_bundle(
        dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict
    ) -> Dict[Text, Any]:
        if tracker.get_slot("requested_slot") != NOTIF_BUNDLE:
            return {}

        resolved = resolve_slot_match(tracker.latest_message["text"], service_match)
        if len(resolved) > 0:
            return resolved

        return {}

    @staticmethod
    def extract_notifications_bundle_option(
        dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict
    ) -> Dict[Text, Any]:
        if tracker.get_slot("requested_slot") != NOTIF_BUNDLE_OPT:
            return {}

        resolved = resolve_slot_match(tracker.latest_message["text"], service_opt_match)
        if len(resolved) > 0:
            return resolved

        return {}

    @staticmethod
    def extract_notifications_event_option(
        dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict
    ) -> Dict[Text, Any]:
        if tracker.get_slot("requested_slot") != NOTIF_EVENT_OPT:
            return {}

        resolved = resolve_slot_match(tracker.latest_message["text"], event_opt_match)
        if len(resolved) > 0:
            return resolved

        return {}

    @staticmethod
    async def extract_notifications_event(
        dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict
    ) -> Dict[Text, Any]:
        if tracker.get_slot("requested_slot") != NOTIF_EVENT:
            return {}

        # build FuzzySlotMatchOptions from the available events
        bundle = tracker.get_slot(NOTIF_BUNDLE)
        if not bundle:
            return {}

        options = []
        response, result = await get_available_events_by_bundle(tracker, bundle["id"])
        if not response.ok or not result:
            received_notifications_error(dispatcher, response, result)
            return {}
        for event in result["data"]:
            possible_value = {
                "id": event["id"],
                "name": event["name"],
                "display_name": event["display_name"],
                "application_id": event["application_id"],
                "application_name": event["application"]["name"],
                "application_display_name": event["application"]["display_name"],
            }
            options.append(
                FuzzySlotMatchOption(
                    possible_value,
                    [event["name"], event["display_name"], event["application_id"]],
                )
            )

        options.append(
            FuzzySlotMatchOption(
                UNSURE_SERVICE,
                [
                    "Another service",
                    "not listed",
                    "unsure",
                    "not sure",
                    "idk",
                    "I'm not sure",
                    "no clue",
                    "I have no idea",
                    "other",
                ],
            )
        )

        event_match.options = options
        resolved = resolve_slot_match(tracker.latest_message["text"], event_match)
        if len(resolved) > 0:
            return resolved

        return {}

    @staticmethod
    def extract_notifications_behavior_option(
        dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict
    ) -> Dict[Text, Any]:
        if tracker.get_slot("requested_slot") != NOTIF_BEHAVIOR_OPT:
            return {}

        resolved = resolve_slot_match(
            tracker.latest_message["text"], behavior_opt_match
        )
        if len(resolved) > 0:
            return resolved

        return {}

    @staticmethod
    async def validate_notifications_bundle(
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        if value == "unsure":
            return {NOTIF_BUNDLE: UNSURE_SERVICE}
        response, result = await get_available_bundles(tracker, name=value)
        if not response.ok or not result:
            received_notifications_error(dispatcher, response, result)
            return {NOTIF_BUNDLE: None}
        if len(result) == 0:
            return {NOTIF_BUNDLE: None}
        formatted = {
            "id": result[0]["id"],
            "name": result[0]["name"],
            "display_name": result[0]["displayName"],
        }
        return {NOTIF_BUNDLE: formatted}

    @staticmethod
    def validate_notifications_bundle_option(
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        return {NOTIF_BUNDLE_OPT: value}

    @staticmethod
    def validate_notifications_event_option(
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        return {NOTIF_EVENT_OPT: value}

    @staticmethod
    def validate_notifications_event(
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        return {NOTIF_EVENT: value}

    @staticmethod
    def validate_notifications_behavior_option(
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        return {NOTIF_BEHAVIOR_OPT: value}

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[Dict[Text, Any]]:
        events = await super().run(dispatcher, tracker, domain)
        requested_slot = tracker.get_slot("requested_slot")

        if requested_slot == NOTIF_BUNDLE_OPT:
            option = tracker.get_slot(NOTIF_BUNDLE_OPT)
            if option == "manage events":
                dispatcher.utter_message(response="utter_notifications_edit")
                dispatcher.utter_message(response="utter_notifications_edit_events_how")
                events.append(SlotSet("requested_slot", NOTIF_EVENT_OPT))
            elif option == "manage preferences":
                dispatcher.utter_message(response="utter_notifications_edit_non_admin")
                events.append(SlotSet("requested_slot", NOTIF_BUNDLE))
            elif option == "contact admin":
                events.append(SlotSet(NOTIF_CONTACT_ADMIN, True))
                events.append(SlotSet("requested_slot", None))
            elif option == "learn":
                dispatcher.utter_message(response="utter_notifications_learn")
                dispatcher.utter_message(response="utter_notifications_learn_dashboard")
                dispatcher.utter_message(response="utter_notifications_learn_docs")
                events.append(SlotSet("requested_slot", None))

        if requested_slot == NOTIF_BUNDLE:
            bundle = tracker.get_slot(NOTIF_BUNDLE)
            # avoiding a bug
            if not bundle:
                return events
            option = tracker.get_slot(NOTIF_BUNDLE_OPT)
            if bundle["name"] == "unsure":
                dispatcher.utter_message(response="utter_notifications_learn")
                dispatcher.utter_message(response="utter_notifications_learn_dashboard")
                dispatcher.utter_message(response="utter_notifications_learn_docs")
                events.append(SlotSet("requested_slot", None))
            else:
                has_notifications_available = None
                if option == "manage preferences":
                    has_notifications_available = True
                response, result = await get_available_events_by_bundle(
                    tracker, bundle["id"], has_notifications_available
                )
                if not response.ok or not result:
                    received_notifications_error(dispatcher, response, result)
                    return events
                if len(result) == 0:
                    dispatcher.utter_message(
                        response="utter_notifications_edit_events_none_1",
                        bundle=bundle["display_name"],
                    )
                    dispatcher.utter_message(
                        response="utter_notifications_edit_events_none_2"
                    )
                    events.append(SlotSet("requested_slot", None))
                    return events

                buttons = []
                for event in result["data"]:
                    buttons.append(
                        {
                            "title": "{} | {}".format(
                                event["display_name"],
                                event["application"]["display_name"],
                            ),
                            "payload": event["display_name"],
                        }
                    )

                if option != "manage preferences":
                    dispatcher.utter_message(
                        response="utter_notifications_setup_for_chosen_service",
                        bundle=bundle["display_name"],
                    )
                dispatcher.utter_message(
                    response="utter_notifications_edit_events_for_service",
                    bundle=bundle["display_name"],
                    buttons=buttons,
                )

                if tracker.get_slot(NOTIF_EVENT_OPT) is None:
                    # implied event_option (skipped N2.2)
                    events.append(SlotSet(NOTIF_EVENT_OPT, "modify"))

        if requested_slot == NOTIF_EVENT_OPT:
            option = tracker.get_slot(NOTIF_EVENT_OPT)
            if option == "new":
                dispatcher.utter_message(
                    response="utter_notifications_setup_which_service"
                )
                events.append(SlotSet(NOTIF_BUNDLE_OPT, "manage events"))
            elif option == "modify" or option == "disable":
                dispatcher.utter_message(
                    response="utter_notifications_edit_events_which_service"
                )
            events.append(SlotSet("requested_slot", NOTIF_BUNDLE))

        if requested_slot == NOTIF_EVENT:
            bundle = tracker.get_slot(NOTIF_BUNDLE)
            event = tracker.get_slot(NOTIF_EVENT)
            if event["id"] == "unsure":
                if tracker.get_slot(_SLOT_IS_ORG_ADMIN):
                    dispatcher.utter_message(
                        response="utter_notifications_edit_preferences_other_admin"
                    )
                else:
                    dispatcher.utter_message(
                        response="utter_notifications_edit_preferences_other"
                    )
                    events.append(SlotSet(NOTIF_CONTACT_ADMIN, True))
                events.append(SlotSet("requested_slot", None))
                return events

            if tracker.get_slot(NOTIF_BUNDLE_OPT) == "manage preferences":
                dispatcher.utter_message(
                    response="utter_notifications_edit_preferences_selected",
                    bundle=bundle["name"],
                    service=event["application_name"],
                )
                events.append(SlotSet("requested_slot", None))
                return events

            if tracker.get_slot(NOTIF_EVENT_OPT) == "disable":
                response = await mute_event(tracker, event["id"])
                if response.ok:
                    dispatcher.utter_message(
                        response="utter_notifications_edit_events_mute_success",
                        event=event["display_name"],
                    )
                else:
                    dispatcher.utter_message(
                        response="utter_notifications_edit_events_mute_error"
                    )
                    logger.error(
                        "Failed to get a response from the notifications API (PUT): status {}".format(
                            response
                        ),
                        exc_info=True,
                    )
                    return events

                events.append(SlotSet("requested_slot", None))
            else:
                dispatcher.utter_message(
                    response="utter_notifications_edit_selected_event",
                    event=event["display_name"],
                )

        if requested_slot == NOTIF_BEHAVIOR_OPT:
            option = tracker.get_slot(NOTIF_BEHAVIOR_OPT)
            event = tracker.get_slot(NOTIF_EVENT)
            bundle = tracker.get_slot(NOTIF_BUNDLE)
            if option == "attach":
                dispatcher.utter_message(response="utter_notifications_edit_new_group")
                events.append(SlotSet("requested_slot", None))
            elif option == "create":
                dispatcher.utter_message(
                    response="utter_notifications_edit_create_group",
                    event=event["display_name"],
                )
                events.append(SlotSet("requested_slot", None))
            elif option == "remove":
                response, result = await get_behavior_groups(tracker, bundle["id"])
                if not response.ok or not result:
                    received_notifications_error(dispatcher, response, result)
                    return events

                if len(result) > 0:
                    response = await mute_event(tracker, event["id"])
                    if response.ok:
                        dispatcher.utter_message(
                            response="utter_notifications_edit_events_mute_success",
                            event=event["display_name"],
                        )
                        events.append(SlotSet("requested_slot", None))
                    else:
                        dispatcher.utter_message(
                            response="utter_notifications_edit_events_mute_error"
                        )
                else:
                    dispatcher.utter_message(
                        response="utter_notifications_edit_no_groups",
                        event=event["display_name"],
                    )
                    dispatcher.utter_message(
                        response="utter_notifications_edit_no_groups_what"
                    )
                    events.append(SlotSet(NOTIF_BEHAVIOR_OPT))
                    events.append(SlotSet("requested_slot", NOTIF_BEHAVIOR_OPT))

        return events

    async def required_slots(
        self,
        domain_slots: List[Text],
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> List[Text]:
        return domain_slots


class ActionNotificationsReset(Action):
    def name(self) -> Text:
        return "action_notifications_reset"

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[Dict[Text, Any]]:
        return [
            SlotSet(NOTIF_BUNDLE, None),
            SlotSet(NOTIF_BUNDLE_OPT, None),
            SlotSet(NOTIF_EVENT, None),
            SlotSet(NOTIF_EVENT_OPT, None),
            SlotSet(NOTIF_BEHAVIOR_OPT, None),
            SlotSet(NOTIF_CONTACT_ADMIN, None),
        ]


class ActionNotificationsSetup(Action):
    def name(self) -> Text:
        return "action_notifications_setup"

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[Dict[Text, Any]]:
        is_org_admin = tracker.get_slot(_SLOT_IS_ORG_ADMIN)
        if is_org_admin is False:
            dispatcher.utter_message(response="utter_notifications_non_admin")
            dispatcher.utter_message(
                response="utter_notifications_setup_non_admin_can_help"
            )
            return [SlotSet("requested_slot", NOTIF_BUNDLE_OPT)]
        else:
            dispatcher.utter_message(response="utter_notifications_setup")
            dispatcher.utter_message(response="utter_notifications_setup_which_service")
            return [
                SlotSet("requested_slot", NOTIF_BUNDLE),
                SlotSet(NOTIF_BUNDLE_OPT, "new"),
            ]


class ActionNotificationsEdit(Action):
    def name(self) -> Text:
        return "action_notifications_edit"

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[Dict[Text, Any]]:
        is_org_admin = tracker.get_slot(_SLOT_IS_ORG_ADMIN)
        if is_org_admin is False:
            dispatcher.utter_message(response="utter_notifications_non_admin")
            dispatcher.utter_message(
                response="utter_notifications_edit_non_admin_options"
            )
            return [SlotSet("requested_slot", NOTIF_BUNDLE_OPT)]
        else:
            dispatcher.utter_message(response="utter_notifications_edit")
            dispatcher.utter_message(response="utter_notifications_edit_what")
            return [SlotSet("requested_slot", NOTIF_BUNDLE_OPT)]


def received_notifications_error(dispatcher: CollectingDispatcher, response, result):
    dispatcher.utter_message(response="utter_notifications_error")
    logger.error(
        "Failed to get a response from the notifications API: status {}; result {}".format(
            response.status, result
        ),
        exc_info=True,
    )


async def get_available_bundles(tracker: Tracker, name: Optional[str] = None):
    params = "?includeApplications=false"
    if name:
        params += f"&bundleName={name}"
    return await send_console_request(
        "notifications-gw",
        "/api/notifications/v1.0/notifications/facets/bundles%s" % params,
        tracker,
    )


async def get_available_events_by_bundle(
    tracker: Tracker, bundleId: str, has_notifications_available: Optional[bool] = None
):
    # TODO: request this feature
    if has_notifications_available:
        # params = "?hasNotifications=true"
        pass
    return await send_console_request(
        "notifications-gw",
        "/api/notifications/v1.0/notifications/eventTypes?bundleId=%s&limit=20&offset=0&sort_by=application:ASC"
        % bundleId,
        tracker,
    )


async def get_behavior_groups(tracker: Tracker, bundleId: str):
    return await send_console_request(
        "notifications-gw",
        "/api/notifications/v1.0/notifications/bundles/%s/behaviorGroups" % bundleId,
        tracker,
    )


async def mute_event(tracker: Tracker, eventId: str):
    headers = Header()
    headers.add_header("Content-Type", "application/json")
    return await send_console_request(
        "notifications-gw",
        "/api/notifications/v1.0/notifications/eventTypes/%s/behaviorGroups" % eventId,
        tracker,
        "put",
        json=[],
        headers=headers,
        fetch_content=False,
    )
