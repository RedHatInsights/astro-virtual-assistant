from typing import Iterable

from quart_schema import OpenAPIProvider
from quart_schema.openapi import Rule

class VirtualAssistantOpenAPIProvider(OpenAPIProvider):

    def generate_rules(self) -> Iterable[Rule]:
        for rule in super().generate_rules():
            # This static endpoints gets added when using quart-injector - unsure if it's a dev only rule, but hiding from here.
            if rule.endpoint == "static":
                continue

            yield rule
