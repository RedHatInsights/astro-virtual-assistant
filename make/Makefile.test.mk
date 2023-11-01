#
# Targets for validation and test tools
#

include make/Makefile.variables.mk

RASA_TEST_STORIES_PARAMS = --stories tests/stories ${RASA_DOMAIN_ARG}

ifndef TEST_ALLOW_ERRORS
	RASA_TEST_STORIES_PARAMS += --fail-on-prediction-errors
endif

validate: test-data

test: test-rasa test-python

test-rasa: test-data test-nlu test-stories

test-data:
	${RASA_EXEC} data validate ${RASA_DOMAIN_ARG}

test-nlu:
	${RASA_EXEC} data split nlu
	${RASA_EXEC} test nlu --nlu train_test_split/test_data.yml ${RASA_DOMAIN_ARG}

test-stories:
	${RASA_EXEC} test ${RASA_TEST_STORIES_PARAMS}

test-python:
	pipenv run pytest

# Convenience target to call the API
test-identity:
	curl -X POST http://0.0.0.0:5005/api/virtual-assistant/v1/talk -H "x-rh-identity: eyJpZGVudGl0eSI6IHsiYWNjb3VudF9udW1iZXIiOiJhY2NvdW50MTIzIiwib3JnX2lkIjoib3JnMTIzIiwidHlwZSI6IlVzZXIiLCJ1c2VyIjp7ImlzX29yZ19hZG1pbiI6dHJ1ZSwgInVzZXJfaWQiOiIxMjM0NTY3ODkwIn0sImludGVybmFsIjp7Im9yZ19pZCI6Im9yZzEyMyJ9fX0=" -H "Content-Type: application/json" --data '{ "message": "Hi there!", "metadata": {"current_url": "https://console.redhat.com"} }'
