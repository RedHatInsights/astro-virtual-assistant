from typing import Optional, Callable

from quart import Quart, Blueprint
from quart_schema import QuartSchema
import quart_injector
import injector


def app_with_blueprint(
    blueprint: Blueprint,
    injector_module: Optional[Callable[[injector.Binder], None]] = None,
) -> Quart:
    app = Quart(__name__, template_folder="../../src/templates")
    app.register_blueprint(blueprint)

    injector_binders = (
        [_injector_config, injector_module]
        if injector_module is not None
        else [_injector_config]
    )

    quart_injector.wire(app, injector_binders)

    QuartSchema(app)  # Ensures we can return objects from the endpoints
    return app


def _injector_config(binder: injector.Binder) -> None: ...
