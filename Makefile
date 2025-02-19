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

# install
install:
	uv sync

# runs the assistant
run:
	uv run --directory services/virtual-assistant src/run.py

run-watson-extension:
	uv run --directory services/watson-extension src/run.py

redis:
	${CONTAINER_EXEC} run --name va-redis -d -p 6379:${REDIS_PORT} redis
