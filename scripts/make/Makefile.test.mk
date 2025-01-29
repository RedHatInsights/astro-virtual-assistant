#
# Targets for validation and test tools
#

include scripts/make/Makefile.variables.mk

test: test-python

test-python-root:
	pipenv run pytest

test-python: test-python-root
	make -C services/watson-extension test

test-openapi:
	curl -X GET http://0.0.0.0:5005/api/virtual-assistant/v1/openapi.json
