import base64
import json


def decode_identity(identity):
    decoded_identity = base64.b64decode(identity)
    identity_dict = json.loads(decoded_identity)

    return identity_dict
