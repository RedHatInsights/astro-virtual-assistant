import abc

import injector
from common.session_storage import SessionStorage

class AbstractUserIdentityProvider(abc.ABC):
    async def get_user_identity(self) -> str: ...

class QuartUserIdentityProvider(AbstractUserIdentityProvider):
    def __init__(self, session_storage: injector.Inject[SessionStorage]):
        self.session_storage = session_storage

    async def get_user_identity(self):
        from quart import request

        session_id = request.headers["x-rh-session-id"]
        return (await self.session_storage.get(session_id)).user_identity

class FixedUserIdentityProvider(AbstractUserIdentityProvider):
    async def get_user_identity(self):
        """
        Fixed user identity equivalent to:
        {
           "identity":{
              "account_number":"account123",
              "org_id":"org123",
              "type":"User",
              "user":{
                 "is_org_admin":true,
                 "user_id":"1234567890",
                 "username":"astro"
              },
              "internal":{
                 "org_id":"org123"
              }
           }
        }
        """

        return "eyJpZGVudGl0eSI6IHsiYWNjb3VudF9udW1iZXIiOiJhY2NvdW50MTIzIiwib3JnX2lkIjoib3JnMTIzIiwidHlwZSI6IlVzZXIiLCJ1c2VyIjp7ImlzX29yZ19hZG1pbiI6dHJ1ZSwgInVzZXJfaWQiOiIxMjM0NTY3ODkwIiwidXNlcm5hbWUiOiJhc3RybyJ9LCJpbnRlcm5hbCI6eyJvcmdfaWQiOiJvcmcxMjMifX19"
