import abc
from typing import Optional

import injector
import jwt

import aiohttp
from aiohttp import ClientResponse
from aiohttp.hdrs import (
    METH_GET,
    METH_OPTIONS,
    METH_HEAD,
    METH_POST,
    METH_PUT,
    METH_PATCH,
    METH_DELETE,
)


class AbstractPlatformRequest(abc.ABC):
    def __init__(self, session: injector.Inject[aiohttp.ClientSession]):
        self.session = session

    @abc.abstractmethod
    async def request(
        self,
        method: str,
        base_url: str,
        api_path: str,
        user_identity: Optional[str] = None,
        **kwargs,
    ) -> ClientResponse: ...

    async def get(
        self,
        base_url: str,
        api_path: str,
        user_identity: Optional[str] = None,
        **kwargs,
    ) -> ClientResponse:
        return await self.request(METH_GET, base_url, api_path, user_identity, **kwargs)

    async def options(
        self,
        base_url: str,
        api_path: str,
        user_identity: Optional[str] = None,
        **kwargs,
    ) -> ClientResponse:
        return await self.request(
            METH_OPTIONS, base_url, api_path, user_identity, **kwargs
        )

    async def head(
        self,
        base_url: str,
        api_path: str,
        user_identity: Optional[str] = None,
        **kwargs,
    ) -> ClientResponse:
        return await self.request(
            METH_HEAD, base_url, api_path, user_identity, **kwargs
        )

    async def post(
        self,
        base_url: str,
        api_path: str,
        user_identity: Optional[str] = None,
        **kwargs,
    ) -> ClientResponse:
        return await self.request(
            METH_POST, base_url, api_path, user_identity, **kwargs
        )

    async def put(
        self,
        base_url: str,
        api_path: str,
        user_identity: Optional[str] = None,
        **kwargs,
    ) -> ClientResponse:
        return await self.request(METH_PUT, base_url, api_path, user_identity, **kwargs)

    async def patch(
        self,
        base_url: str,
        api_path: str,
        user_identity: Optional[str] = None,
        **kwargs,
    ) -> ClientResponse:
        return await self.request(
            METH_PATCH, base_url, api_path, user_identity, **kwargs
        )

    async def delete(
        self,
        base_url: str,
        api_path: str,
        user_identity: Optional[str] = None,
        **kwargs,
    ) -> ClientResponse:
        return await self.request(
            METH_DELETE, base_url, api_path, user_identity, **kwargs
        )


class DevPlatformRequest(AbstractPlatformRequest):
    def __init__(
        self,
        session: injector.Inject[aiohttp.ClientSession],
        refresh_token: str,
        refresh_token_url: str,
    ):
        super().__init__(session)
        self._refresh_token = refresh_token
        self._refresh_token_url = refresh_token_url
        self._dev_token: Optional[str] = None

    async def refresh_token(self):
        result = await self.session.post(
            self._refresh_token_url,
            data={
                "grant_type": "refresh_token",
                "client_id": "rhsm-api",
                "refresh_token": self._refresh_token,
            },
        )

        if not result.ok:
            raise "Unable to refresh dev token"

        token = (await result.json())["access_token"]
        self.verify_token(token)
        self._dev_token = token

    @staticmethod
    def verify_token(token: str):
        jwt.decode(
            token,
            options={"verify_signature": False, "verify_exp": True, "verify_nbf": True},
        )

    async def request(
        self,
        method: str,
        base_url: str,
        api_path: str,
        user_identity: Optional[str] = None,
        **kwargs,
    ) -> ClientResponse:
        if self._dev_token is not None:
            try:
                self.verify_token(self._dev_token)
            except jwt.InvalidTokenError:
                await self.refresh_token()
        else:
            await self.refresh_token()

        headers = kwargs.pop("headers", {})
        if user_identity is not None:
            headers["Authorization"] = "Bearer " + self._dev_token

        return await self.session.request(
            method, f"{base_url}{api_path}", headers=headers, **kwargs
        )


class PlatformRequest(AbstractPlatformRequest):
    async def request(
        self,
        method: str,
        base_url: str,
        api_path: str,
        user_identity: Optional[str] = None,
        **kwargs,
    ) -> ClientResponse:
        headers = kwargs.pop("headers", {})
        if user_identity is not None:
            headers["x-rh-identity"] = user_identity

        return await self.session.request(
            method, f"{base_url}{api_path}", headers=headers, **kwargs
        )
