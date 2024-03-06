import uuid
from datetime import datetime

from rasa_sdk import Tracker

from common.header import Header
from common.requests import send_console_request
from common.config import app


async def send_notification(tracker: Tracker, event: dict):
    """Send a notification using the notifications-gateway"""
    headers = Header()
    headers.add_header("Content-Type", "application/json")
    return await send_console_request(
        "notifications", "/notifications", tracker, "post", json=event, headers=headers
    )


async def send_rbac_request_admin(
    tracker: Tracker,
    org_id: str,
    username: str,
    requested_url: str,
    user_email: str,
    user_message: str,
):
    if app.is_running_locally:
        print("called send_rbac_request_admin in local envionment")
        return

    event = dict(
        {
            "id": str(uuid.uuid4()),
            "bundle": "console",
            "application": "rbac",
            "event_type": "request-access",
            "timestamp": datetime.now().isoformat(),
            "org_id": org_id,
            "context": {},
            "events": [
                {
                    "metadata": {},
                    "payload": {
                        "url_path": requested_url,
                        "username": username,
                        "user": {"email": user_email, "request": user_message},
                    },
                }
            ],
            "recipients": [{"only_admins": True}],
        }
    )

    return await send_notification(tracker, event)
