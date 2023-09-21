CONTAINER_EXEC ?= podman
COMPOSE_EXEC ?= ${CONTAINER_EXEC}-compose

RASA_EXEC = python app.py
RASA_TRAIN_ARGS = --domain data
RASA_RUN_ARGS = --endpoints endpoints.yml

export TRACKER_STORE_TYPE ?=
export DB_HOST ?=
export DB_PORT ?=
export DB_USER ?=
export DB_PASSWORD ?=
export DB_LOGIN_DB ?=
export DB_DATABASE ?=

# install and train the project
install:
	pipenv install --dev

train:
	pipenv run ${RASA_EXEC} train ${RASA_TRAIN_ARGS}

finetune:
	pipenv run ${RASA_EXEC} train ${RASA_TRAIN_ARGS} --finetune

# runs the assistant
run:
	pipenv run ${RASA_EXEC} run ${RASA_RUN_ARGS}

run-interactive:
	pipenv run ${RASA_EXEC} interactive ${RASA_TRAIN_ARGS} ${RASA_RUN_ARGS}

run-actions:
	PROMETHEUS=False pipenv run ${RASA_EXEC} run actions --auto-reload

run-cli:
	pipenv run ${RASA_EXEC} shell ${RASA_RUN_ARGS}

run-db:
	pipenv run make db

db:
	${CONTAINER_EXEC} run --rm -it -p 5432:${DB_PORT} -e POSTGRES_PASSWORD=${DB_PASSWORD} -e POSTGRES_USER=${DB_USER} -e POSTGRES_DB=${DB_DATABASE} --name postgres postgres:12.4

drop-db:
	${CONTAINER_EXEC} stop postgres
	${CONTAINER_EXEC} rm postgres

compose:
	pipenv run ${COMPOSE_EXEC} up

# validate and test changes
validate:
	pipenv run ${RASA_EXEC} data validate --fail-on-warnings --domain data

test:
	pipenv run ${RASA_EXEC} test --fail-on-prediction-errors --stories tests/stories ${RASA_TRAIN_ARGS}

test-python:
	pipenv run pytest

test-identity:
	curl -X POST http://0.0.0.0:5005/api/virtual-assistant/talk -H "x-rh-identity: eyJpZGVudGl0eSI6IHsiYWNjb3VudF9udW1iZXIiOiJhY2NvdW50MTIzIiwib3JnX2lkIjoib3JnMTIzIiwidHlwZSI6IlVzZXIiLCJ1c2VyIjp7ImlzX29yZ19hZG1pbiI6dHJ1ZSwgInVzZXJfaWQiOiIxMjM0NTY3ODkwIn0sImludGVybmFsIjp7Im9yZ19pZCI6Im9yZzEyMyJ9fX0=" -H "Content-Type: application/json" --data '{ "message": "Hi there!", "metadata": {} }'
