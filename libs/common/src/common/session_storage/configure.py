import injector
from ..config import app

from . import SessionStorage
from .file import FileSessionStorage
from .redis import RedisSessionStorage


def configure(binder: injector.Binder) -> None:
    # Read configuration and assemble our dependencies

    # This gets injected into routes when it is requested.
    # e.g. async def status(session_storage: injector.Inject[SessionStorage]) -> Response:
    if app.use_redis:
        binder.bind(SessionStorage, to=RedisSessionStorage())
    else:
        binder.bind(SessionStorage, to=FileSessionStorage(".va-session-storage"))
