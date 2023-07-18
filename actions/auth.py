from __future__ import annotations
import requests

from os import getenv
import jwt

OFFLINE_REFRESH_TOKEN = 'OFFLINE_REFRESH_TOKEN'
SSO_REFRESH_TOKEN_URL_PARAM = 'SSO_REFRESH_TOKEN_URL'
SSO_REFRESH_TOKEN_URL = 'https://sso.redhat.com/auth/realms/redhat-external/protocol/openid-connect/token'

local_dev_token: str | None = None


def get_auth_token() -> str:
    global local_dev_token

    if local_dev_token is not None and _is_jwt_valid(local_dev_token):
        return local_dev_token
    else:
        local_dev_token = None

    offline_token = getenv(OFFLINE_REFRESH_TOKEN)
    if offline_token is None:
        raise 'offline dev token not found'

    local_dev_token = _with_refresh_token(offline_token)
    return local_dev_token


def _with_refresh_token(refresh_token: str) -> str:
    result = requests.post(
        getenv(SSO_REFRESH_TOKEN_URL_PARAM, SSO_REFRESH_TOKEN_URL),
        data={
            'grant_type': 'refresh_token',
            'client_id': 'rhsm-api',
            'refresh_token': refresh_token
        }
    )

    if not result.ok:
        raise 'Unable to refresh token'

    token = result.json()['access_token']
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
    jwt.decode(token, options={'verify_signature': False, 'verify_exp': True, 'verify_nbf': True})
