#
# Targets for validation and test tools
#

include scripts/make/Makefile.variables.mk

test: test-python

test-python:
	uv run --directory libs/common pytest
	uv run --directory services/virtual-assistant pytest
	uv run --directory services/watson-extension pytest

test-python-coverage:
	uv run --directory libs/common coverage run -m pytest && uv run --directory libs/common coverage report
	uv run --directory services/virtual-assistant coverage run -m pytest && uv run --directory services/virtual-assistant coverage report
	uv run --directory services/watson-extension coverage run -m pytest && uv run --directory services/watson-extension coverage report
ifneq ($(COVERAGE_FORMAT),)
	uv run --directory libs/common coverage $(COVERAGE_FORMAT)
	uv run --directory services/virtual-assistant coverage $(COVERAGE_FORMAT)
	uv run --directory services/watson-extension coverage $(COVERAGE_FORMAT)
endif

test-openapi:
	curl -X GET http://0.0.0.0:5005/api/virtual-assistant/v1/openapi.json
