__CONTAINER_EXEC ?= $(shell command -v podman)

ifeq (, $(shell command -v podman 2> /dev/null))
	__CONTAINER_EXEC := $(shell command -v docker)
endif

CONTAINER_EXEC ?= ${__CONTAINER_EXEC}
COMPOSE_EXEC ?= ${CONTAINER_EXEC}-compose

include scripts/make/Makefile.variables.mk
include scripts/make/Makefile.test.mk
include scripts/make/Makefile.lint.mk

# install and train the project
install:
	pipenv install
	make install -C services/virtual-assistant
	make install -C services/watson-extension

# runs the assistant
run:
	make run -C services/virtual-assistant

run-watson-extension:
	make run -C services/watson-extension

run-db:
	pipenv run make db

db:
	${CONTAINER_EXEC} run --rm -it -p 5432:${DB_PORT} -e POSTGRESQL_PASSWORD=${DB_PASSWORD} -e POSTGRESQL_USER=${DB_USERNAME} -e POSTGRESQL_DATABASE=${DB_NAME} --name postgres quay.io/sclorg/postgresql-15-c9s:latest

drop-db:
	${CONTAINER_EXEC} stop postgres
	${CONTAINER_EXEC} rm postgres

compose:
	pipenv run ${COMPOSE_EXEC} up
