import base64
import json

# decodes the x-rh-identity header
def decode_identity(identity):
    decoded_identity = base64.b64decode(identity)
    identity_dict = json.loads(decoded_identity)

    return identity_dict
