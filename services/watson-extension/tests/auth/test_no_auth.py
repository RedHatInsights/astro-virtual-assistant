from unittest.mock import MagicMock

from watson_extension.auth.no_authentication import NoAuthentication


async def test_no_auth():
    auth = NoAuthentication()
    request = MagicMock()
    await auth.check_auth(request)
    request.assert_not_called()
