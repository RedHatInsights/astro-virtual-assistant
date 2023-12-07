from __future__ import annotations

from typing import Any, Optional

from rasa_sdk import Tracker

from common import logging
from common.config import app

from .header import Header
from .auth import get_auth_header

logger = logging.initialize_logging()


def create_console_link(path: str, preview: bool) -> str:
    if preview:
        return f"{app.console_dot_base_url}/preview{path}"
    else:
        return f"{app.console_dot_base_url}{path}"
