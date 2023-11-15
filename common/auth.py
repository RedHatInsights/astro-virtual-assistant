from __future__ import annotations
import requests
from typing import Text, Dict, Any

from os import getenv
import jwt

from rasa_sdk import Tracker

OFFLINE_REFRESH_TOKEN = "OFFLINE_REFRESH_TOKEN"
SSO_REFRESH_TOKEN_URL_PARAM = "SSO_REFRESH_TOKEN_URL"
SSO_REFRESH_TOKEN_URL = (
    "https://sso.redhat.com/auth/realms/redhat-external/protocol/openid-connect/token"
)

local_dev_token: str | None = None


def is_user_event(event: Dict[Text, Any]):
    return event.get("event") == "user"


# if local token specified, it defaults to it
def get_auth_header(tracker: Tracker, header: Header) -> Header:
    global local_dev_token

    if _get_is_running_locally():
        # if its already saved, use it
        if local_dev_token is not None and _is_jwt_valid(local_dev_token):
            header.add_header("Authorization", "Bearer " + local_dev_token)
            return header
        else:
            local_dev_token = None

        # need to set the offline token
        offline_token = _get_offline_token()
        if offline_token is not None:
            local_dev_token = _with_refresh_token(offline_token)
            header.add_header("Authorization", "Bearer " + local_dev_token)
            return header

        raise ValueError("No offline token found")

    latest_user_event = next(filter(is_user_event, reversed(tracker.events)), None)

    if latest_user_event is not None:
        header.add_header(
            "x-rh-identity", latest_user_event.get("metadata").get("identity")
        )
        return header

    raise ValueError("No authentication found")


def _get_is_running_locally() -> bool:
    return getenv("IS_RUNNING_LOCALLY", "false").lower() == "true"


def _get_offline_token() -> str:
    return getenv(OFFLINE_REFRESH_TOKEN)


def _with_refresh_token(refresh_token: str) -> str:
    result = requests.post(
        getenv(SSO_REFRESH_TOKEN_URL_PARAM, SSO_REFRESH_TOKEN_URL),
        data={
            "grant_type": "refresh_token",
            "client_id": "rhsm-api",
            "refresh_token": refresh_token,
        },
    )

    if not result.ok:
        raise "Unable to refresh token"

    token = result.json()["access_token"]
    _jwt_decode(token)

    return token


def _is_jwt_valid(token: str) -> bool:
    try:
        # We want to know if the token expired
        _jwt_decode(token)
        return True
    except jwt.InvalidTokenError:
        return False


def _jwt_decode(token: str) -> None:
    # Skip signature check - token service is going to validate for us
    jwt.decode(
        token,
        options={"verify_signature": False, "verify_exp": True, "verify_nbf": True},
    )
