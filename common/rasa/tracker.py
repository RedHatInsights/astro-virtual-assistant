from rasa_sdk import Tracker
from typing import Text, Dict, Any, Optional

from common.identity import decode_identity


def _is_user_event(event: Dict[Text, Any]) -> bool:
    return event.get("event") == "user"


def get_last_user_message(tracker: Tracker) -> Optional[Dict[Text, Any]]:
    return next(filter(_is_user_event, reversed(tracker.events)), None)


def get_user_identity(tracker: Tracker) -> Optional[Text]:
    latest_user_event = get_last_user_message(tracker)

    if latest_user_event is not None:
        return latest_user_event.get("metadata").get("identity")

    return None


def get_decoded_user_identity(tracker: Tracker) -> Optional[Dict[Text, Any]]:
    identity = get_user_identity(tracker)

    if identity is not None:
        return decode_identity(identity)

    return None


def get_current_url(tracker: Tracker) -> Optional[Text]:
    latest_user_event = get_last_user_message(tracker)

    if latest_user_event is not None:
        return latest_user_event.get("metadata").get("current_url")

    return None


def get_is_org_admin(tracker: Tracker) -> bool:
    latest_user_event = get_last_user_message(tracker)

    try:
        return latest_user_event.get("metadata").get("is_org_admin")
    except Exception as e:
        print(f"An Exception occured while handling retrieving is_org_admin: {e}")

    return False
