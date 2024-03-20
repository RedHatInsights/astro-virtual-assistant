from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import (
    ActionExecuted,
    SlotSet,
    UserUtteranceReverted,
    ActionReverted,
)
from rasa_sdk.types import DomainDict

from actions.slot_match import FuzzySlotMatch, FuzzySlotMatchOption, resolve_slot_match

from common import logging
from common.header import Header
from common.requests import send_console_request


logger = logging.initialize_logging()

# Slots
RHEL_VERSION = "image_builder_rhel_version"
RHEL_VERSION_CONFIRM = "image_builder_rhel_version_confirmed"
CONTENT_REPOSITORY = "image_builder_content_repository"
CONTENT_REPOSITORY_VERSION = "image_builder_content_repository_version"

rhel_version_match = FuzzySlotMatch(
    RHEL_VERSION,
    [
        FuzzySlotMatchOption(
            "RHEL 9", ["RHEL 9", "9", "the newest one", "new", "newest", "best"]
        ),
        FuzzySlotMatchOption(
            "RHEL 8", ["RHEL 8", "8", "older version", "oldest", "oldest one"]
        ),
    ],
)

content_repository_match = FuzzySlotMatch(
    CONTENT_REPOSITORY,
    [
        FuzzySlotMatchOption("EPEL", ["EPEL", "epel", "extra packages", "provided"]),
        FuzzySlotMatchOption(
            "Other", ["Other", "other", "something else", "a different one"]
        ),
    ],
)

content_repository_version_match = FuzzySlotMatch(
    CONTENT_REPOSITORY_VERSION,
    [
        FuzzySlotMatchOption("EPEL 8", ["8", "epel 8", "EPEL 8"]),
        FuzzySlotMatchOption("EPEL 9", ["9", "epel 9", "EPEL 9"]),
    ],
)


class ValidateFormImageBuilderGettingStarted(FormValidationAction):
    def name(self) -> Text:
        return "validate_form_image_builder_getting_started"

    @staticmethod
    def extract_image_builder_rhel_version(
        dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict
    ) -> Dict[Text, Any]:
        if tracker.get_slot("requested_slot") == RHEL_VERSION:
            resolved = resolve_slot_match(
                tracker.latest_message["text"], rhel_version_match, accepted_rate=95
            )
            if len(resolved) > 0:
                return resolved

        return {}

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
        events = await super().run(dispatcher, tracker, domain)
        requested_slot = tracker.get_slot("requested_slot")

        if requested_slot == RHEL_VERSION:
            rhel_version = tracker.get_slot(RHEL_VERSION)
            if rhel_version == "RHEL 9":
                events.append(SlotSet("requested_slot", None))
                events.append(SlotSet(RHEL_VERSION_CONFIRM, True))
            else:
                dispatcher.utter_message(response="utter_image_builder_rhel_8_support")
                dispatcher.utter_message(
                    response="utter_image_builder_rhel_8_confirmation"
                )

        if requested_slot == RHEL_VERSION_CONFIRM:
            rhel_version_confirmed = tracker.get_slot(RHEL_VERSION_CONFIRM)
            if rhel_version_confirmed is True:
                events.append(SlotSet("requested_slot", None))
                events.append(SlotSet(RHEL_VERSION, "RHEL 8"))
            else:
                events.append(SlotSet("requested_slot", None))
                events.append(SlotSet(RHEL_VERSION, "RHEL 9"))

        return events

    async def required_slots(
        self,
        domain_slots: List[Text],
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> List[Text]:
        updated_slots = domain_slots.copy()

        if tracker.get_slot(RHEL_VERSION) == "RHEL 9":
            updated_slots.remove("image_builder_rhel_version_confirmed")

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
        rhel_version = tracker.get_slot(RHEL_VERSION)
        version_param = "rhel9"
        if rhel_version == "RHEL 8":
            version_param = "rhel8"
        dispatcher.utter_message(response="utter_image_builder_redirect_1")
        dispatcher.utter_message(
            response="utter_image_builder_redirect_2",
            link="https://console.redhat.com/insights/image-builder/imagewizard?release={version}#SIDs=&tags=".format(
                version=version_param
            ),
        )

        return [
            ActionExecuted(self.name()),
            SlotSet(RHEL_VERSION, None),
            SlotSet(RHEL_VERSION_CONFIRM, None),
        ]


class ValidateFormImageBuilderCustomContent(FormValidationAction):
    def name(self) -> Text:
        return "validate_form_image_builder_custom_content"

    @staticmethod
    def extract_image_builder_content_repository(
        dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict
    ) -> Dict[Text, Any]:
        if tracker.get_slot("requested_slot") == CONTENT_REPOSITORY:
            resolved = resolve_slot_match(
                tracker.latest_message["text"], content_repository_match
            )
            if len(resolved) > 0:
                return resolved

        return {}

    @staticmethod
    def extract_image_builder_content_repository_version(
        dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict
    ) -> Dict[Text, Any]:
        if tracker.get_slot("requested_slot") == CONTENT_REPOSITORY_VERSION:
            resolved = resolve_slot_match(
                tracker.latest_message["text"],
                content_repository_version_match,
                accepted_rate=95,
            )
            if len(resolved) > 0:
                return resolved

        return {}

    async def enable_custom_repositories(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, version: str
    ):
        response, result = await send_console_request(
            "content-sources",
            "/api/content-sources/v1/popular_repositories/?offset=0&limit=20",
            tracker,
        )

        if not response.ok or not result or not result["data"]:
            dispatcher.utter_message(
                response="utter_image_builder_custom_content_error"
            )
            logger.debug(
                "Failed to get a response from the content-sources API: status {}; result {}".format(
                    response.status, result
                )
            )
            return

        repository = None
        # find the information for the repository they want (EPEL 8 or EPEL 9)
        for repo in result["data"]:
            if repo["suggested_name"] and repo["suggested_name"].startswith(version):
                repository = repo
                break

        headers = Header()
        headers.add_header("Content-Type", "application/json")
        formatted = [
            {
                "name": repository["suggested_name"],
                "distribution_arch": repository["distribution_arch"],
                "distribution_versions": repository["distribution_versions"],
                "gpg_key": repository["gpg_key"],
                "metadata_verification": repository["metadata_verification"],
                "snapshot": False,
                "url": repository["url"],
            }
        ]

        response, result = await send_console_request(
            "content-sources",
            "/api/content-sources/v1.0/repositories/bulk_create/",
            tracker,
            "post",
            json=formatted,
            headers=headers,
        )
        status = response.status

        errors = None
        if "errors" in result:
            errors = result["errors"]

        if status == 400 and any(
            "already belongs" in error["detail"] for error in errors
        ):
            dispatcher.utter_message(
                response="utter_image_builder_custom_content_epel_already_enabled",
                version=version,
            )
        elif status == 201:
            dispatcher.utter_message(
                response="utter_image_builder_custom_content_epel_enabled",
                version=version,
            )
        else:
            dispatcher.utter_message(
                response="utter_image_builder_custom_content_error"
            )
            logger.debug(
                "Failed to get a response from the content-sources API bulk-create: status {}; result {}".format(
                    status, result
                )
            )

        return

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[Dict[Text, Any]]:
        events = await super().run(dispatcher, tracker, domain)
        requested_slot = tracker.get_slot("requested_slot")

        if requested_slot == CONTENT_REPOSITORY:
            repository = tracker.get_slot(CONTENT_REPOSITORY)
            if repository == "EPEL":
                dispatcher.utter_message(
                    response="utter_image_builder_custom_content_epel"
                )
                dispatcher.utter_message(
                    response="utter_image_builder_custom_content_epel_which"
                )
            if repository == "Other":
                dispatcher.utter_message(
                    response="utter_image_builder_custom_content_other"
                )
                events.append(SlotSet("requested_slot", None))

        if requested_slot == CONTENT_REPOSITORY_VERSION:
            version = tracker.get_slot(CONTENT_REPOSITORY_VERSION)
            await self.enable_custom_repositories(dispatcher, tracker, version)
            events.append(SlotSet(CONTENT_REPOSITORY, None))
            events.append(SlotSet(CONTENT_REPOSITORY_VERSION, None))
            events.append(SlotSet("requested_slot", None))

        return events

    async def required_slots(
        self,
        domain_slots: List[Text],
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> List[Text]:
        updated_slots = domain_slots.copy()

        if tracker.get_slot(CONTENT_REPOSITORY) == "Other":
            updated_slots.remove("image_builder_content_repository_version")

        return updated_slots


class ImageBuilderCustomContent(Action):
    def name(self) -> Text:
        return "action_image_builder_custom_content"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        epel_version = tracker.get_slot(CONTENT_REPOSITORY_VERSION)
        version_param = "rhel9"
        if epel_version == "EPEL 8":
            version_param = "rhel8"
        dispatcher.utter_message(response="utter_image_builder_redirect_1")
        dispatcher.utter_message(
            response="utter_image_builder_redirect_2",
            link="https://console.redhat.com/insights/image-builder/imagewizard?release={version}#SIDs=&tags=".format(
                version=version_param
            ),
        )

        return [
            ActionExecuted(self.name()),
            SlotSet(CONTENT_REPOSITORY, None),
            SlotSet(CONTENT_REPOSITORY_VERSION, None),
        ]


class ImageBuilderLaunch(Action):
    def name(self) -> Text:
        return "action_image_builder_launch"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        provider = ""
        provider_lower = ""
        if len(tracker.latest_message["entities"]) > 0:
            provider = tracker.latest_message["entities"][0]["value"]
            provider_lower = provider.lower()
        # The team does not have a generic quickstart for other providers, default to AWS
        quick_start = ""
        if (
            provider_lower == "aws"
            or provider_lower == "azure"
            or provider_lower == "gcp"
        ):
            quick_start = f"https://console.redhat.com/insights/image-builder?quickstart=insights-launch-{provider_lower}"
        else:
            provider = "your provider"
            quick_start = "https://console.redhat.com/insights/image-builder?quickstart=insights-launch-aws"

        dispatcher.utter_message(
            response="utter_image_builder_launch",
            provider=provider,
            quick_start=quick_start,
        )

        return [ActionExecuted(self.name())]
