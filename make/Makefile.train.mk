#
# Targets for train
#

include make/Makefile.variables.mk

RASA_EXTRA_TRAIN_ARGS =

train: --train

train-finetune: RASA_EXTRA_TRAIN_ARGS += --finetune
train-finetune: --train


train-nlu:
	DISABLE_FUZZYENTITYEXTRACTOR=1 ${RASA_EXEC} train nlu ${RASA_TRAIN_ARGS} ${RASA_EXTRA_TRAIN_ARGS}

--train:
	${RASA_TRAIN_EXEC} train ${RASA_TRAIN_ARGS} ${RASA_EXTRA_TRAIN_ARGS}
