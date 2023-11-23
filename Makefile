CONTAINER_EXEC ?= podman
COMPOSE_EXEC ?= ${CONTAINER_EXEC}-compose

export TRACKER_STORE_TYPE ?=
export DB_HOST ?=
export DB_PORT ?=
export DB_USER ?=
export DB_PASSWORD ?=
export DB_LOGIN_DB ?=
export DB_NAME ?=

include make/Makefile.variables.mk
include make/Makefile.test.mk
include make/Makefile.lint.mk
include make/Makefile.train.mk

# install and train the project
install:
	pipenv install --categories "packages dev-packages api-packages"

clean:
	rm -rf results .rasa models/* train_test_split

# runs the assistant
run:
	pipenv run ${RASA_EXEC} run ${RASA_RUN_ARGS}

run-interactive:
	pipenv run ${RASA_EXEC} interactive ${RASA_TRAIN_ARGS} ${RASA_RUN_ARGS}

run-actions:
	pipenv run ${RASA_EXEC} run actions --auto-reload

run-cli:
	pipenv run ${RASA_EXEC} shell ${RASA_RUN_ARGS}

run-db:
	pipenv run make db

db:
	${CONTAINER_EXEC} run --rm -it -p 5432:${DB_PORT} -e POSTGRES_PASSWORD=${DB_PASSWORD} -e POSTGRES_USER=${DB_USER} -e POSTGRES_DB=${DB_NAME} --name postgres postgres:12.4

drop-db:
	${CONTAINER_EXEC} stop postgres
	${CONTAINER_EXEC} rm postgres

compose:
	pipenv run ${COMPOSE_EXEC} up
