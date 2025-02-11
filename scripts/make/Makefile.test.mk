#
# Targets for validation and test tools
#

include scripts/make/Makefile.variables.mk

test: test-python

test-python:
	uv run --directory libs/common pytest
	uv run --directory services/virtual-assistant pytest
	uv run --directory services/watson-extension pytest

test-openapi:
	curl -X GET http://0.0.0.0:5005/api/virtual-assistant/v1/openapi.json
