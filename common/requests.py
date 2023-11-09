from __future__ import annotations
from typing import Any
from os import getenv

from rasa_sdk import Tracker

import requests

from .header import Header
from .auth import get_auth_header

CONSOLEDOT_BASE_URL = "https://console.redhat.com"

base_url = getenv("CONSOLEDOT_BASE_URL", CONSOLEDOT_BASE_URL)

def send_console_request(url: str, tracker: Tracker) -> Any:
    header = Header()
    try:
        get_auth_header(tracker, header)
    except Exception as e:
        print(f"An Exception occured while handling retrieving auth credentials: {e}")
        return None

    result = None
    try:
        result = requests.get(
            base_url+url,
            headers=header.build_headers()
        ).json()
    except Exception as e:
        print(f"An Exception occured while handling response from the Advisor API: {e}")
        return None

    return result
