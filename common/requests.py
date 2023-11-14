# can I import just match and case from future python versions?
from __future__ import annotations
from typing import Any
from os import getenv

from rasa_sdk import Tracker

import requests

from .header import Header
from .auth import get_auth_header

IS_RUNNING_LOCALLY = getenv("IS_RUNNING_LOCALLY", "false") == "true"
CONSOLEDOT_BASE_URL = getenv("CONSOLEDOT_BASE_URL", "https://console.redhat.com")

ENDPOINT_ADVISOR_BACKEND = getenv("ENDPOINT_ADVISOR_BACKEND", "http://advisor-backend:8080")
ENDPOINT_NOTIFICATIONS_GW = getenv("ENDPOINT_NOTIFICATIONS_GW", "http://notifications-gw:8080")
ENDPOINT_VULNERABILITY_ENGINE = getenv("ENDPOINT_VULNERABILITY_ENGINE", "http://vulnerability-engine:8080")

def send_console_request(app: str, path: str, tracker: Tracker) -> Any:
    header = Header()
    try:
        get_auth_header(tracker, header)
    except Exception as e:
        print(f"An Exception occured while handling retrieving auth credentials: {e}")
        return None

    endpoint = None
    if app == "advisor":
        endpoint = ENDPOINT_ADVISOR_BACKEND
    elif app == "notifications":
        endpoint = ENDPOINT_NOTIFICATIONS_GW
    elif app == "vulnerability":
        endpoint = ENDPOINT_VULNERABILITY_ENGINE
    else:
        print(f"Invalid app: {app}")
        return None

    url = None
    if IS_RUNNING_LOCALLY:
        url = "{}{}".format(CONSOLEDOT_BASE_URL, path)
    else:
        url = "{}{}".format(endpoint, path)

    result = None
    status = None
    try:
        result = requests.get(
            url,
            headers=header.build_headers()
        )
        status = result.status_code
        result = result.json()
    except Exception as e:
        print(f"An Exception occured while handling response from the Advisor API: {e}")
        return None

    return result, status
