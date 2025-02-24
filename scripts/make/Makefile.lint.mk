#
# Targets for lint tools
#

PRETTIER_ARGS = -c
RUFF_CHECK_ARGS =
RUFF_FORMAT_ARGS =

lint: RUFF_CHECK_ARGS += --no-fix
lint: RUFF_FORMAT_ARGS += --diff
lint: --lint

lint-fix: RUFF_CHECK_ARGS += --fix
lint-fix: --lint

--lint: --lint-ruff

--lint-ruff:
	uv run ruff check . $(RUFF_CHECK_ARGS)
	uv run ruff format . ${RUFF_FORMAT_ARGS}
