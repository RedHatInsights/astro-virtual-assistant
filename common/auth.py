from __future__ import annotations
import requests

from common.config import app
from .header import Header

import jwt

from rasa_sdk import Tracker

from common.rasa.tracker import get_user_identity

local_dev_token: str | None = None


# if local token specified, it defaults to it
def get_auth_header(tracker: Tracker, header: Header) -> Header:
    global local_dev_token

    if app.is_running_locally:
        # if its already saved, use it
        if local_dev_token is not None and _is_jwt_valid(local_dev_token):
            header.add_header("Authorization", "Bearer " + local_dev_token)
            return header
        else:
            local_dev_token = None

        # need to set the offline token
        offline_token = app.dev_offline_refresh_token
        if offline_token is not None:
            local_dev_token = _with_refresh_token(offline_token)
            header.add_header("Authorization", "Bearer " + local_dev_token)
            return header

        raise ValueError("No offline token found")

    identity = get_user_identity(tracker)
    if identity is not None:
        header.add_header("x-rh-identity", identity)
        return header

    raise ValueError("No authentication found")


def _with_refresh_token(refresh_token: str) -> str:
    result = requests.post(
        app.dev_sso_refresh_token_url,
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
