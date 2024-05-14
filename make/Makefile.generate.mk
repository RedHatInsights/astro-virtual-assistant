#
# Pulls data from API and adds to NLU
#

include make/Makefile.variables.mk

GENERATE_SERVICES = scripts.generate_services_list

generate_services:
	pipenv run python -m ${GENERATE_SERVICES}
