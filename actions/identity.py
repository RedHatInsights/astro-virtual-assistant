from rasa_sdk import Tracker

def get_identity(tracker):
    return tracker.get_slot('session_started_metadata')['identity']