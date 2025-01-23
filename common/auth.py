from __future__ import annotations
import requests

from common.config import app
from .header import Header

from flask import request, jsonify
import base64
import functools
import json

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


def check_identity(identity_header):
    try:
        base64.b64decode(identity_header)
    except Exception:
        return False
    return True


def require_identity_header(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        identity_header = request.headers.get("x-rh-identity")
        if not identity_header or not check_identity(identity_header):
            return jsonify(message="Invalid x-rh-identity"), 401
        return func(*args, **kwargs)

    return wrapper


def get_org_id_from_identity(identity):
    decoded_identity = base64.b64decode(identity).decode("utf8")
    identity_json = json.loads(decoded_identity)
    identity = identity_json.get("identity", {})
    org_id = identity.get("org_id")
    return org_id
