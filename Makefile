CONTAINER_EXEC ?= podman
COMPOSE_EXEC ?= ${CONTAINER_EXEC}-compose

export IS_RUNNING_LOCALLY=1

include make/Makefile.variables.mk
include make/Makefile.test.mk
include make/Makefile.lint.mk
include make/Makefile.train.mk
include make/Makefile.hyperopt.mk

main-env:
	export PIPENV_CUSTOM_VENV_NAME=astro-main

internal-env:
	export PIPENV_CUSTOM_VENV_NAME=astro-internal

# install and train the project
install:
	${MAKE} main-env
	pipenv install --categories "packages dev-packages api-packages"
	${MAKE} internal-env
	pipenv install --categories "packages dev-packages internal-packages"

clean:
	rm -rf results .rasa models/* .astro

# runs the assistant
run: main-env
	pipenv run ${RASA_EXEC} run ${RASA_RUN_ARGS}

run-interactive:  main-env
	pipenv run ${RASA_EXEC} interactive ${RASA_TRAIN_ARGS} ${RASA_RUN_ARGS}

run-actions:  main-env
	pipenv run ${RASA_ACTIONS_EXEC} --actions actions --auto-reload

run-cli:  main-env
	pipenv run ${RASA_EXEC} shell ${RASA_RUN_ARGS}

run-internal: internal-env
	pipenv run ${INTERNAL_EXEC} run ${INTERNAL_RUN_ARGS}

run-db: main-env
	pipenv run make db

db:
	${CONTAINER_EXEC} run --rm -it -p 5432:${DB_PORT} -e POSTGRES_PASSWORD=${DB_PASSWORD} -e POSTGRES_USER=${DB_USERNAME} -e POSTGRES_DB=${DB_NAME} --name postgres postgres:15.5

drop-db:
	${CONTAINER_EXEC} stop postgres
	${CONTAINER_EXEC} rm postgres

compose: main-env
	pipenv run ${COMPOSE_EXEC} up
