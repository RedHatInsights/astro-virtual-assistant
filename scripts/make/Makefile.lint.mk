#
# Targets for lint tools
#

PRETTIER_ARGS = -c
RUFF_ARGS =

lint: RUFF_ARGS += --no-fix
lint: --lint

lint-fix: RUFF_ARGS += --fix
lint-fix: --lint

--lint: --lint-ruff

--lint-ruff:
	uv run ruff check . $(RUFF_ARGS)
