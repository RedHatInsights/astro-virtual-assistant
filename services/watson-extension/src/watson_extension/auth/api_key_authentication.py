from typing import List

import quart
from werkzeug.exceptions import Unauthorized

from watson_extension.auth import Authentication

class ApiKeyAuthentication(Authentication):

    def __init__(self, valid_keys: List[str]):
        self.valid_keys = valid_keys

    async def check_auth(self, request: quart.Request):
        api_key = request.args.get("api_key")
        if api_key not in self.valid_keys:
            raise Unauthorized("Invalid api_key")
