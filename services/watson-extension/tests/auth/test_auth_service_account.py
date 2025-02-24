import base64
import json
from unittest.mock import MagicMock
from wsgiref.headers import Headers

from hypothesis import given, strategies as st, assume
import quart
import pytest

from tests import get_resource_contents
from werkzeug.exceptions import Unauthorized

from watson_extension.auth.service_account_authentication import ServiceAccountAuthentication

def get_identity_header(client_id):
    def set_client_id(header):
        header["identity"]["service_account"]["client_id"] = client_id
    return get_identity_header_with_updater(set_client_id)

def get_identity_header_with_updater(updater):
    identity_header_json = json.loads(get_resource_contents("auth/identity-header.json"))
    updater(identity_header_json)
    return base64.b64encode(json.dumps(identity_header_json).encode("utf-8"))

@given(st.text())
async def test_valid_header(client_id):
    identity_header = get_identity_header(client_id)
    request = MagicMock(quart.Request)
    request.headers = MagicMock(Headers)
    request.headers.get = MagicMock(return_value=identity_header)
    auth = ServiceAccountAuthentication(client_id)
    await auth.check_auth(request)
    request.headers.get.assert_called_once_with("x-rh-identity")


@given(st.text(), st.text())
async def test_wrong_client_id(good_client_id, wrong_client_id):
    assume(good_client_id != wrong_client_id)
    identity_header = get_identity_header(wrong_client_id)
    request = MagicMock(quart.Request)
    request.headers = MagicMock(Headers)
    request.headers.get = MagicMock(return_value=identity_header)
    auth = ServiceAccountAuthentication(good_client_id)

    with pytest.raises(Unauthorized):
        await auth.check_auth(request)
    request.headers.get.assert_called_once_with("x-rh-identity")

async def test_identity_header_not_found():
    request = MagicMock(quart.Request)
    request.headers = MagicMock(Headers)
    request.headers.get = MagicMock(return_value=None)
    auth = ServiceAccountAuthentication("test")

    with pytest.raises(Unauthorized):
        await auth.check_auth(request)

    request.headers.get.assert_called_once_with("x-rh-identity")

async def test_invalid_identity_header_not_b64():
    request = MagicMock(quart.Request)
    request.headers = MagicMock(Headers)
    request.headers.get = MagicMock(return_value="not base64")
    auth = ServiceAccountAuthentication("test")

    with pytest.raises(Unauthorized):
        await auth.check_auth(request)

    request.headers.get.assert_called_once_with("x-rh-identity")

async def test_invalid_identity_header_not_json():
    request = MagicMock(quart.Request)
    request.headers = MagicMock(Headers)
    # { not-a-json, }
    request.headers.get = MagicMock(return_value="eyBub3QtYS1qc29uLCB9")
    auth = ServiceAccountAuthentication("test")

    with pytest.raises(Unauthorized):
        await auth.check_auth(request)

    request.headers.get.assert_called_once_with("x-rh-identity")

async def test_not_identity_header():
    def del_identity(x):
        del x["identity"]

    identity_header = get_identity_header_with_updater(del_identity)
    request = MagicMock(quart.Request)
    request.headers = MagicMock(Headers)
    request.headers.get = MagicMock(return_value=identity_header)
    auth = ServiceAccountAuthentication("test")

    with pytest.raises(Unauthorized):
        await auth.check_auth(request)
    request.headers.get.assert_called_once_with("x-rh-identity")

async def test_not_sa():
    def del_service_account(x):
        del x["identity"]["service_account"]

    identity_header = get_identity_header_with_updater(del_service_account)
    request = MagicMock(quart.Request)
    request.headers = MagicMock(Headers)
    request.headers.get = MagicMock(return_value=identity_header)
    auth = ServiceAccountAuthentication("test")

    with pytest.raises(Unauthorized):
        await auth.check_auth(request)
    request.headers.get.assert_called_once_with("x-rh-identity")