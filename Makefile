CONTAINER_EXEC ?= podman
COMPOSE_EXEC ?= ${CONTAINER_EXEC}-compose

export IS_RUNNING_LOCALLY=1

include make/Makefile.variables.mk
include make/Makefile.test.mk
include make/Makefile.lint.mk
include make/Makefile.train.mk
include make/Makefile.hyperopt.mk

# install and train the project
install:
	pipenv install --categories "packages dev-packages api-packages"

create-internal:
	mkdir -p .venv-internal
	python3 -m venv .venv-internal

install-internal:
	if [ ! -d .venv-internal ]; then ${MAKE} create-internal; fi
	. .venv-internal/bin/activate && pipenv install --categories "packages dev-packages internal-packages" --skip-lock

clean:
	rm -rf results .rasa models/* .astro

# runs the assistant
run:
	pipenv run ${RASA_EXEC} run ${RASA_RUN_ARGS}

run-interactive:
	pipenv run ${RASA_EXEC} interactive ${RASA_TRAIN_ARGS} ${RASA_RUN_ARGS}

run-actions:
	pipenv run ${RASA_ACTIONS_EXEC} --actions actions --auto-reload

run-cli:
	pipenv run ${RASA_EXEC} shell ${RASA_RUN_ARGS}

run-internal:
	. .venv-internal/bin/activate && ${INTERNAL_EXEC} run ${INTERNAL_RUN_ARGS}

run-db:
	pipenv run make db

db:
	${CONTAINER_EXEC} run --rm -it -p 5432:${DB_PORT} -e POSTGRES_PASSWORD=${DB_PASSWORD} -e POSTGRES_USER=${DB_USERNAME} -e POSTGRES_DB=${DB_NAME} --name postgres postgres:15.5

drop-db:
	${CONTAINER_EXEC} stop postgres
	${CONTAINER_EXEC} rm postgres

compose:
	pipenv run ${COMPOSE_EXEC} up
