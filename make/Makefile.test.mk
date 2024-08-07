#
# Targets for validation and test tools
#

include make/Makefile.variables.mk

RASA_TEST_STORIES_PARAMS = --stories tests/stories ${RASA_DOMAIN_ARG}

__FAILED_TEST_STORIES = results/failed_test_stories.yml

validate: test-data

test: test-rasa test-python

test-rasa: test-stories test-data test-nlu-all

test-data:
	${RASA_EXEC} data validate ${RASA_DOMAIN_ARG}

test-nlu-all:
	${RASA_EXEC} data split nlu --out .astro/train_test_split
	${RASA_EXEC} test nlu --nlu .astro/train_test_split ${RASA_DOMAIN_ARG}

test-nlu-examples:
	${RASA_EXEC} test nlu --nlu tests/nlu/examples.yml ${RASA_DOMAIN_ARG}

test-stories-nlu:
	${PYTHON_EXEC} tests/extract_stories_nlu.py
	${RASA_EXEC} test nlu --nlu .astro/nlu-from-stories/test_data.yml ${RASA_DOMAIN_ARG}

test-stories:
	${RASA_EXEC} test ${RASA_TEST_STORIES_PARAMS}
	@(head -n 1 ${__FAILED_TEST_STORIES} | grep -q '# None of the test stories failed - all good!') || (cat ${__FAILED_TEST_STORIES} && false)

test-python:
	pipenv run pytest

# Convenience target to call the API
test-identity:
	curl -X POST http://0.0.0.0:5005/api/virtual-assistant/v1/talk -H "x-rh-identity: eyJpZGVudGl0eSI6IHsiYWNjb3VudF9udW1iZXIiOiJhY2NvdW50MTIzIiwib3JnX2lkIjoib3JnMTIzIiwidHlwZSI6IlVzZXIiLCJ1c2VyIjp7ImlzX29yZ19hZG1pbiI6dHJ1ZSwgInVzZXJfaWQiOiIxMjM0NTY3ODkwIiwidXNlcm5hbWUiOiJhc3RybyJ9LCJpbnRlcm5hbCI6eyJvcmdfaWQiOiJvcmcxMjMifX19" -H "Content-Type: application/json" --data '{ "message": "Hi there!", "metadata": {"current_url": "https://console.redhat.com"} }'

test-identity-2:
	curl -X POST http://0.0.0.0:5005/api/virtual-assistant/v1/talk -H "x-rh-identity: eyJpZGVudGl0eSI6IHsiYWNjb3VudF9udW1iZXIiOiJhY2NvdW50MTIzIiwib3JnX2lkIjoib3JnMTIzIiwidHlwZSI6IlVzZXIiLCJ1c2VyIjp7ImlzX29yZ19hZG1pbiI6dHJ1ZSwgInVzZXJfaWQiOiIxMjM0NTY3ODkwIiwidXNlcm5hbWUiOiJkaWZmZXJlbnRfYXN0cm8ifSwiaW50ZXJuYWwiOnsib3JnX2lkIjoib3JnMTIzIn19fQ==" -H "Content-Type: application/json" --data '{ "message": "Hi there!", "metadata": {"current_url": "https://console.redhat.com"} }'

test-first-access:
	curl -X GET http://0.0.0.0:5005/api/virtual-assistant/v1/session/status -H "x-rh-identity: eyJpZGVudGl0eSI6IHsiYWNjb3VudF9udW1iZXIiOiJhY2NvdW50MTIzIiwib3JnX2lkIjoib3JnMTIzIiwidHlwZSI6IlVzZXIiLCJ1c2VyIjp7ImlzX29yZ19hZG1pbiI6dHJ1ZSwgInVzZXJfaWQiOiIxMjM0NTY3ODkwIiwidXNlcm5hbWUiOiJhc3RybyJ9LCJpbnRlcm5hbCI6eyJvcmdfaWQiOiJvcmcxMjMifX19" -H "Content-Type: application/json"

test-is-org-admin:
	curl -X POST http://0.0.0.0:5005/api/virtual-assistant/v1/talk -H "x-rh-identity: eyJpZGVudGl0eSI6IHsiYWNjb3VudF9udW1iZXIiOiJhY2NvdW50MTIzIiwib3JnX2lkIjoib3JnMTIzIiwidHlwZSI6IlVzZXIiLCJ1c2VyIjp7ImlzX29yZ19hZG1pbiI6dHJ1ZSwgInVzZXJfaWQiOiIxMjM0NTY3ODkwIiwidXNlcm5hbWUiOiJhc3RybyJ9LCJpbnRlcm5hbCI6eyJvcmdfaWQiOiJvcmcxMjMifX19" -H "Content-Type: application/json" --data '{ "message": "What do you do?", "metadata": {"current_url": "https://console.redhat.com"} }'

test-is-not-org-admin:
	curl -X POST http://0.0.0.0:5005/api/virtual-assistant/v1/talk -H "x-rh-identity: eyJpZGVudGl0eSI6IHsiYWNjb3VudF9udW1iZXIiOiJhY2NvdW50MTIzIiwib3JnX2lkIjoibzFyMmczIiwidHlwZSI6IlVzZXIiLCJ1c2VyIjp7ImlzX29yZ19hZG1pbiI6ZmFsc2UsICJ1c2VyX2lkIjoiMTIzNDU2Nzg5MCIsInVzZXJuYW1lIjoiYXN0cm8ifSwiaW50ZXJuYWwiOnsib3JnX2lkIjoibzFyMmczIn19fQ==" -H "Content-Type: application/json" --data '{ "message": "What do you do?", "metadata": {"current_url": "https://console.redhat.com"} }'

test-openapi:
	curl -X GET http://0.0.0.0:5005/api/virtual-assistant/v1/openapi.json
