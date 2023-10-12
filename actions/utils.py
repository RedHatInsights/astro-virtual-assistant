from typing import Text, Optional, Dict, List, Any
from rasa_sdk import Tracker


def show_more(name: str, url_prefix: str):
    return {"show_more": {"name": name, "url_prefix": url_prefix}}


def is_user_event(event: Dict[Text, Any]):
    return event.get("event") == "user"


def get_current_url(tracker: Tracker) -> Optional[Text]:
    latest_user_event = next(filter(is_user_event, reversed(tracker.events)), None)

    if latest_user_event is not None:
        return latest_user_event.get("metadata").get("current_url")

    return None
