import quart

from watson_extension.auth import Authentication


class NoAuthentication(Authentication):

    async def check_auth(self, request: quart.Request):
        pass
