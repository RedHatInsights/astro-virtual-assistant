#
# Targets for lint tools
#

PRETTIER_ARGS = -c

lint: --lint

lint-fix: PRETTIER_ARGS +=  -w
lint-fix: --lint

--lint: --lint-prettier

--lint-prettier:
	npx prettier "data/**/**.yml" $(PRETTIER_ARGS)
