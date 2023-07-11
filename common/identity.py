from rasa_sdk import Tracker
import base64
import json
# Identity header format: https://github.com/RedHatInsights/identity/blob/main/identity.go

def get_identity(tracker):
    return tracker.get_slot('session_started_metadata')['identity']

def decode_identity(identity):
    decoded_identity = base64.b64decode(identity)
    identity_dict = json.loads(decoded_identity)

    return identity_dict
