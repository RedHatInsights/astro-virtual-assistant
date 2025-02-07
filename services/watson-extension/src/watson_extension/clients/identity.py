import typing
from injector import provider

UserIdentity = typing.NewType("UserIdentity", str)

@provider
def user_identity_from_platform() -> UserIdentity:
    raise NotImplementedError("user_identity_from_platform not implemented yet")


@provider
def user_identity_fixed() -> UserIdentity:
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
    return UserIdentity("eyJpZGVudGl0eSI6IHsiYWNjb3VudF9udW1iZXIiOiJhY2NvdW50MTIzIiwib3JnX2lkIjoib3JnMTIzIiwidHlwZSI6IlVzZXIiLCJ1c2VyIjp7ImlzX29yZ19hZG1pbiI6dHJ1ZSwgInVzZXJfaWQiOiIxMjM0NTY3ODkwIiwidXNlcm5hbWUiOiJhc3RybyJ9LCJpbnRlcm5hbCI6eyJvcmdfaWQiOiJvcmcxMjMifX19")
