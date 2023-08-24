CONTAINER_EXEC ?= podman
COMPOSE_EXEC ?= ${CONTAINER_EXEC}-compose

# install and train the project
install:
	pipenv install --dev

train:
	pipenv run rasa train --domain data

finetune:
	pipenv run rasa train --domain data --finetune

# runs the assistant
run:
	pipenv run rasa run --endpoints endpoints.yml

run-actions:
	pipenv run rasa run actions --auto-reload

run-cli:
	pipenv run rasa shell --endpoints endpoints.yml

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
	pipenv run rasa data validate --fail-on-warnings --domain data

test:
	pipenv run rasa test --fail-on-prediction-errors

test-python:
	pipenv run pytest

test-identity:
	curl -X POST http://0.0.0.0:5005/api/virtual-assistant/talk -H "x-rh-identity: eyJpZGVudGl0eSI6IHsiYWNjb3VudF9udW1iZXIiOiJhY2NvdW50MTIzIiwib3JnX2lkIjoib3JnMTIzIiwidHlwZSI6IlVzZXIiLCJ1c2VyIjp7ImlzX29yZ19hZG1pbiI6dHJ1ZSwgInVzZXJfaWQiOiIxMjM0NTY3ODkwIn0sImludGVybmFsIjp7Im9yZ19pZCI6Im9yZzEyMyJ9fX0=" -H "Content-Type: application/json" --data '{ "message": "Hi there!", "metadata": {} }'
