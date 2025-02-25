from typing import Iterable, Dict, Any

from quart_schema import OpenAPIProvider
from quart_schema.openapi import Rule


class VirtualAssistantOpenAPIProvider(OpenAPIProvider):
    def schema(self) -> Dict[str, Any]:
        schema = super().schema()
        schema["openapi"] = "3.0.0"
        return schema

    def generate_rules(self) -> Iterable[Rule]:
        for rule in super().generate_rules():
            # This static endpoints gets added when using quart-injector - unsure if it's a dev only rule, but hiding from here.
            if rule.endpoint == "static":
                continue

            yield rule
