__CONTAINER_EXEC ?= $(shell command -v podman)

ifeq (, $(shell command -v podman 2> /dev/null))
	__CONTAINER_EXEC := $(shell command -v docker)
endif

CONTAINER_EXEC ?= ${__CONTAINER_EXEC}
COMPOSE_EXEC ?= ${CONTAINER_EXEC}-compose

ifeq (,$(shell command -v uv 2>/dev/null))
$(error "uv was not found. Install it by following: https://github.com/astral-sh/uv?tab=readme-ov-file#installation")
endif

include scripts/make/Makefile.variables.mk
include scripts/make/Makefile.test.mk
include scripts/make/Makefile.lint.mk

export PIPENV_IGNORE_VIRTUALENVS=1

# install
install:
	uv sync

# runs the assistant
run:
	uv run --directory services/virtual-assistant src/virtual-assistant/run.py

run-watson-extension:
	uv run --directory services/watson-extension src/watson-extension/run.py

run-db:
	pipenv run make db

db:
	${CONTAINER_EXEC} run --rm -it -p 5432:${DB_PORT} -e POSTGRESQL_PASSWORD=${DB_PASSWORD} -e POSTGRESQL_USER=${DB_USERNAME} -e POSTGRESQL_DATABASE=${DB_NAME} --name postgres quay.io/sclorg/postgresql-15-c9s:latest

drop-db:
	${CONTAINER_EXEC} stop postgres
	${CONTAINER_EXEC} rm postgres

redis:
	${CONTAINER_EXEC} run --name va-redis -d -p 6379:${REDIS_PORT} redis

compose:
	pipenv run ${COMPOSE_EXEC} up
