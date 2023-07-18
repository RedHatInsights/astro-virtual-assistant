import base64
import json

from rasa_sdk import Tracker


def get_identity(tracker: Tracker):
    return tracker.get_slot('session_started_metadata')['identity']


def decode_identity(identity):
    decoded_identity = base64.b64decode(identity)
    identity_dict = json.loads(decoded_identity)

    return identity_dict
