# Variables shared across the Makefiles

RASA_EXEC = pipenv run python app.py
RASA_DOMAIN_ARG = --domain data
RASA_ENDPOINTS_ARG = --endpoints endpoints.yml

RASA_TRAIN_ARGS = ${RASA_DOMAIN_ARG}
RASA_RUN_ARGS = ${RASA_ENDPOINTS_ARG}

ifdef DEBUG
  RASA_TRAIN_ARGS += --debug
  RASA_RUN_ARGS += --debug
endif

ifdef VERBOSE
  RASA_TRAIN_ARGS += --verbose
  RASA_RUN_ARGS += --verbose
endif
