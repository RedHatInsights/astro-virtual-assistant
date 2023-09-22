#
# Targets for lint tools
#

PRETTIER_ARGS = -c
BLACK_ARGS =

lint: BLACK_ARGS += --check
lint: --lint

lint-fix: PRETTIER_ARGS +=  -w
lint-fix: --lint

--lint: --lint-prettier --lint-black

--lint-prettier:
	npx prettier "data/**/**.yml" $(PRETTIER_ARGS)

--lint-black:
	black . $(BLACK_ARGS)
