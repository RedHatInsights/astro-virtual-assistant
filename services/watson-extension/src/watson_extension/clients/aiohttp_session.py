import aiohttp

from injector import provider, singleton

@singleton
@provider
def aiohttp_session() -> aiohttp.ClientSession:
    return aiohttp.ClientSession()
