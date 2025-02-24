from unittest.mock import MagicMock
from hypothesis import given, strategies as st, assume
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


@given(st.text(), st.text())
async def test_wrong_key(good_api_key, wrong_api_key):
    assume(good_api_key != wrong_api_key)
    request = MagicMock(quart.Request)
    request.args.get = MagicMock(return_value=wrong_api_key)
    auth = ApiKeyAuthentication([good_api_key])
    with pytest.raises(Unauthorized):
        await auth.check_auth(request)
    request.args.get.assert_called_once_with("api_key")
