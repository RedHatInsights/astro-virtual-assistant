# can I import just match and case from future python versions?
from __future__ import annotations

from typing import Any, Optional

import aiohttp
from aiohttp import ContentTypeError
from rasa_sdk import Tracker

from common import logging
from common.config import app

from .header import Header
from .auth import get_auth_header

logger = logging.initialize_logging()


async def send_console_request(
    app_name: str,
    path: str,
    tracker: Tracker,
    method: str = "get",
    headers: Optional[Header] = None,
    fetch_content: bool = True,
    **kwargs,
) -> Any:
    if headers is None:
        headers = Header()

    try:
        get_auth_header(tracker, headers)
    except ValueError as e:
        print(f"An Exception occured while handling retrieving auth credentials: {e}")
        return None

    endpoint = None
    if app_name == "advisor":
        endpoint = app.advisor_url
    elif app_name == "advisor-openshift":
        endpoint = app.advisor_openshift_url
    elif app_name == "notifications-gw":
        endpoint = app.notifications_gw_url
    elif app_name == "notifications":
        endpoint = app.notifications_url
    elif app_name == "vulnerability":
        endpoint = app.vulnerability_url
    elif app_name == "content-sources":
        endpoint = app.content_sources_url
    elif app_name == "sources":
        endpoint = app.sources_url
    elif app_name == "rhsm":
        endpoint = app.rhsm_url
    elif app_name == "chrome-service":
        endpoint = app.chrome_service_url
    elif app_name == "rbac":
        endpoint = app.rbac_url
    else:
        print(f"Invalid app: {app_name}")
        raise ValueError(f"Invalid app_name used: {app_name}")

    url = "{}{}".format(endpoint, path)

    try:
        logger.info("Calling console service %s %s", method.upper(), url)
        async with aiohttp.ClientSession() as session:
            async with session.request(
                method,
                url,
                headers=headers.build_headers(),
                timeout=app.requests_timeout,
                **kwargs,
            ) as console_response:
                if not console_response.ok:
                    logger.error(
                        f"Received non OK~sh response from call {method.upper()} {url}: ({console_response.status}) - {await console_response.text()}"
                    )

                if fetch_content:
                    try:
                        return console_response, await console_response.json()
                    except ContentTypeError:
                        return console_response, await console_response.text()

                return console_response
    except Exception as e:
        logger.error(
            f"Exception while handling request: {method.upper()} {url}", exc_info=True
        )
        bad_response = object()
        bad_response.ok = False
        bad_response.status = None

        if fetch_content:
            return bad_response, None
        return bad_response


def send_console_request_watson(
    app_name: str,
    path: str,
    method: str = "get",
    headers: Optional[Header] = None,
    fetch_content: bool = True,
    **kwargs,
) -> Any:
    #TODO: this will be and implementation of send_console_request() without the Rasa tracker
    if app_name == "cat_facts":
        return  {"fact":"The first cat show was organized in 1871 in London. Cat shows later became a worldwide craze.","length":93}
    else:
        return {"app_name": app_name}
