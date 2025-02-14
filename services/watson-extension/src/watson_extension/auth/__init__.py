from abc import ABC, abstractmethod

import quart


class Authentication(ABC):
    @abstractmethod
    async def check_auth(self, request: quart.Request): ...
