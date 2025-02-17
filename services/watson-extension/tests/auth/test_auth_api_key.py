from unittest.mock import MagicMock
from hypothesis import given, strategies as st
import quart
import pytest

from watson_extension.auth.api_key_authentication import ApiKeyAuthentication
from werkzeug.exceptions import Unauthorized


@given(st.text())
async def test_api_key_valid(api_key):
    request = MagicMock(quart.Request)
    request.args.get = MagicMock(return_value=api_key)
    auth = ApiKeyAuthentication([api_key])
    await auth.check_auth(request)
    request.args.get.assert_called_once_with("api_key")

@given(st.text(), st.text())
async def test_multiple_params(api_key1, api_key2):
    request = MagicMock(quart.Request)
    request.args.get = MagicMock(return_value=api_key1)
    auth = ApiKeyAuthentication([api_key1, api_key2])
    await auth.check_auth(request)
    request.args.get.assert_called_once_with("api_key")

async def test_wrong_key():
    request = MagicMock(quart.Request)
    request.args.get = MagicMock(return_value="hacker")
    auth = ApiKeyAuthentication(["1234"])
    with pytest.raises(Unauthorized):
        await auth.check_auth(request)
    request.args.get.assert_called_once_with("api_key")
