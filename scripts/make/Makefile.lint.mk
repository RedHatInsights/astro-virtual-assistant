#
# Targets for lint tools
#

PRETTIER_ARGS = -c
BLACK_ARGS =

lint: BLACK_ARGS += --diff --check
lint: --lint

lint-fix: --lint

--lint: --lint-black

--lint-black:
	pipenv run black . $(BLACK_ARGS)
