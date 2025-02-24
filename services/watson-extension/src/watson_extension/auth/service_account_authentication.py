import base64
import binascii
import json

import quart
from werkzeug.exceptions import Unauthorized

from watson_extension.auth import Authentication

class ServiceAccountAuthentication(Authentication):

    def __init__(self, client_id: str):
        self.client_id = client_id

    async def check_auth(self, request: quart.Request):
        identity_header = request.headers.get("x-rh-identity")
        if not identity_header:
            raise Unauthorized("Missing identity header")

        try:
            decoded = json.loads(base64.b64decode(identity_header))
        except (binascii.Error, ValueError):
            raise Unauthorized("Invalid identity header")

        if "identity" not in decoded or "service_account" not in decoded["identity"]:
            raise Unauthorized("Invalid identity header")

        service_account = decoded["identity"]["service_account"]

        if service_account["client_id"] != self.client_id:
            raise Unauthorized("Invalid identity header")
