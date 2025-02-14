# import functools
from abc import ABC, abstractmethod

# import injector
import quart


class Authentication(ABC):
    @abstractmethod
    async def check_auth(self, request: quart.Request): ...

# def require_auth(f):
#     @functools.wraps(f)
#     async def wrapper(authentication: injector.Inject[Authentication], *args, **kwargs):
#         await authentication.check_auth(quart.request)
#         f(*args, **kwargs)
#
#     return wrapper
