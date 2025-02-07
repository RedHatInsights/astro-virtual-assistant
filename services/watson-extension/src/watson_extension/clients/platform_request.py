from typing import Optional

import injector

from watson_extension.clients.identity import UserIdentity

import aiohttp
from aiohttp import ClientResponse
from aiohttp.hdrs import METH_GET, METH_OPTIONS, METH_HEAD, METH_POST, METH_PUT, METH_PATCH, METH_DELETE

class PlatformRequest:
    def __init__(self, session: injector.Inject[aiohttp.ClientSession]):
        self.session = session

    async def request(self, method: str, base_url: str, api_path: str, user_identity: Optional[UserIdentity] = None, **kwargs) -> ClientResponse:
        headers =  kwargs.pop("headers", {})
        if user_identity is not None:
            headers['x-rh-identity'] = user_identity

        return await self.session.request(method, f"{base_url}{api_path}", headers=headers, **kwargs)

    async def get(self, base_url: str, api_path: str, user_identity: Optional[UserIdentity] = None, **kwargs) -> ClientResponse:
        return await self.request(METH_GET, base_url, api_path, user_identity, **kwargs)

    async def options(self, base_url: str, api_path: str, user_identity: Optional[UserIdentity] = None, **kwargs) -> ClientResponse:
        return await self.request(METH_OPTIONS, base_url, api_path, user_identity, **kwargs)

    async def head(self, base_url: str, api_path: str, user_identity: Optional[UserIdentity] = None, **kwargs) -> ClientResponse:
        return await self.request(METH_HEAD, base_url, api_path, user_identity, **kwargs)

    async def post(self, base_url: str, api_path: str, user_identity: Optional[UserIdentity] = None, **kwargs) -> ClientResponse:
        return await self.request(METH_POST, base_url, api_path, user_identity, **kwargs)

    async def put(self, base_url: str, api_path: str, user_identity: Optional[UserIdentity] = None, **kwargs) -> ClientResponse:
        return await self.request(METH_PUT, base_url, api_path, user_identity, **kwargs)

    async def patch(self, base_url: str, api_path: str, user_identity: Optional[UserIdentity] = None, **kwargs) -> ClientResponse:
        return await self.request(METH_PATCH, base_url, api_path, user_identity, **kwargs)

    async def delete(self, base_url: str, api_path: str, user_identity: Optional[UserIdentity] = None, **kwargs) -> ClientResponse:
        return await self.request(METH_DELETE, base_url, api_path, user_identity, **kwargs)
