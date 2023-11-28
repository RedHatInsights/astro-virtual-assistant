# can I import just match and case from future python versions?
from __future__ import annotations

from typing import Any, Optional

from rasa_sdk import Tracker

import requests
from common import logging
from common.config import app

from .header import Header
from .auth import get_auth_header

logger = logging.initialize_logging()


def send_console_request(
    app_name: str,
    path: str,
    tracker: Tracker,
    method: str = "get",
    headers: Optional[Header] = None,
    **kwargs,
) -> Any:
    if headers is None:
        headers = Header()

    try:
        get_auth_header(tracker, headers)
    except Exception as e:
        print(f"An Exception occured while handling retrieving auth credentials: {e}")
        return None

    endpoint = None
    if app_name == "advisor":
        endpoint = app.advisor_url
    elif app_name == "notifications":
        endpoint = app.notifications_url
    elif app_name == "vulnerability":
        endpoint = app.vulnerability_url
    else:
        print(f"Invalid app: {app_name}")
        raise ValueError(f"Invalid app_name used: {app_name}")

    url = "{}{}".format(endpoint, path)

    try:
        logger.info("Calling console service %s %s", method.upper(), url)
        result = requests.request(
            method,
            url,
            headers=headers.build_headers(),
            timeout=app.requests_timeout,
            **kwargs,
        )

        if not result.ok:
            logger.error(
                f"Received non OK~sh response from call {method.upper()} {url}: ({result.status_code}) - {result.content}"
            )

        return result
    except Exception as e:
        print(f"An Exception occured while handling response from {app_name}: {e}")
        return None
