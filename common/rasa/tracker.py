from rasa_sdk import Tracker
from typing import Text, Dict, Any, Optional

from common.identity import decode_identity
from common.config import app


def _is_user_event(event: Dict[Text, Any]) -> bool:
    return event.get("event") == "user"


def get_last_user_message(tracker: Tracker) -> Optional[Dict[Text, Any]]:
    return next(filter(_is_user_event, reversed(tracker.events)), None)


def get_user_identity(tracker: Tracker) -> Optional[Text]:
    if app.is_running_locally:
        return __get_mocked_user_identity()

    latest_user_event = get_last_user_message(tracker)

    if latest_user_event is not None:
        return latest_user_event.get("metadata").get("identity")

    return None


def __get_mocked_user_identity() -> Text:
    return "eyJpZGVudGl0eSI6IHsiYWNjb3VudF9udW1iZXIiOiJhY2NvdW50MTIzIiwib3JnX2lkIjoib3JnMTIzIiwidHlwZSI6IlVzZXIiLCJ1c2VyIjp7ImlzX29yZ19hZG1pbiI6dHJ1ZSwgImVtYWlsIjoidXNlckBzb21ld2hlcmUiLCAidXNlcl9pZCI6IjEyMzQ1Njc4OTAiLCJ1c2VybmFtZSI6ImFzdHJvIn0sImludGVybmFsIjp7Im9yZ19pZCI6Im9yZzEyMyJ9fX0="


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
        return latest_user_event.get("metadata").get(
            "is_org_admin", True
        )  # Change this to false
    except Exception as e:
        print(f"An Exception occured while handling retrieving is_org_admin: {e}")

    return False


def get_email(tracker: Tracker) -> Optional[Text]:
    latest_user_event = get_last_user_message(tracker)

    email = None
    try:
        email = latest_user_event.get("metadata").get("email")
    except Exception as e:
        print(f"An Exception occured while handling retrieving is_org_admin: {e}")

    if email is None or email == "":
        return "email not provided"

    return email
