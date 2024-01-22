#
# Targets for hyper-parameters optimizer
#

include make/Makefile.variables.mk

NLU_HYPEROPT_ROOT = .astro/nlu-hyperopt
NLU_HYPEROPT_CONFIG = config/nlu-hyperopt
NLU_HYPEROPT_WORKERS = 4

NLU_HYPEROPT_RASA_VERSION = ${shell pip list --format=json | jq -r '.[] | select(.name=="rasa").version'}

hyperopt-nlu: --hyperopt-nlu-workingdir --hyperopt-nlu-update --hyperopt-nlu-data --hyperopt-nlu-run

--hyperopt-nlu-workingdir: ${NLU_HYPEROPT_ROOT}

${NLU_HYPEROPT_ROOT}:
	git clone https://github.com/RasaHQ/nlu-hyperopt.git ${NLU_HYPEROPT_ROOT}
	git apply --directory ${NLU_HYPEROPT_ROOT} ${NLU_HYPEROPT_CONFIG}/nlu-hyperopt.diff

--hyperopt-nlu-update:
	cp ${NLU_HYPEROPT_CONFIG}/space.py ${NLU_HYPEROPT_ROOT}/nlu_hyperopt/
	cp ${NLU_HYPEROPT_CONFIG}/nlu-config.yml ${NLU_HYPEROPT_ROOT}/train_test_split/template_config.yml
	cp -R pipeline ${NLU_HYPEROPT_ROOT}/

--hyperopt-nlu-data:
	${RASA_EXEC} data split nlu --out ${NLU_HYPEROPT_ROOT}/train_test_split

--hyperopt-nlu-run: export RASA_VERSION=${NLU_HYPEROPT_RASA_VERSION}
--hyperopt-nlu-run:
	docker-compose -f ${NLU_HYPEROPT_ROOT}/docker-compose.yml build
	docker-compose -f ${NLU_HYPEROPT_ROOT}/docker-compose.yml up --scale hyperopt-worker=${NLU_HYPEROPT_WORKERS}
