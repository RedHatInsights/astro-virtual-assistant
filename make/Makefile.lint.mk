#
# Targets for lint tools
#

PRETTIER_ARGS = -c
BLACK_ARGS =

lint: BLACK_ARGS += --diff
lint: --lint

lint-fix: PRETTIER_ARGS +=  -w
lint-fix: --lint

--lint: --lint-prettier --lint-black

--lint-prettier:
	npx prettier "data/**/**.yml" $(PRETTIER_ARGS)

--lint-black:
	pipenv run black . $(BLACK_ARGS)
