from __future__ import annotations


# Helper class for building request headers
class Header:
    def __init__(self) -> None:
        self.headers = {}

    def add_header(self, key, value):
        self.headers[key] = value

    def add_dict(self, dict):
        self.headers.update(dict)

    def build_headers(self):
        return self.headers
