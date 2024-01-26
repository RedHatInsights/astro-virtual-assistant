# Variables shared across the Makefiles

PYTHON_EXEC = pipenv run python
RASA_EXEC = ${PYTHON_EXEC} app.py
RASA_ACTIONS_EXEC = ${PYTHON_EXEC} run_actions.py
RASA_TRAIN_EXEC = pipenv run rasa
RASA_DOMAIN_ARG = --domain data
RASA_ENDPOINTS_ARG = --endpoints endpoints.yml

RASA_TRAIN_ARGS = ${RASA_DOMAIN_ARG}
RASA_RUN_ARGS = ${RASA_ENDPOINTS_ARG}

INTERNAL_EXEC = ${PYTHON_EXEC} run_internal.py
INTERNAL_RUN_ARGS =

ifdef DEBUG
  RASA_TRAIN_ARGS += --debug
  RASA_RUN_ARGS += --debug
endif

ifdef VERBOSE
  RASA_TRAIN_ARGS += --verbose
  RASA_RUN_ARGS += --verbose
endif
