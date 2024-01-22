# Configuration of search space
# see http://hyperopt.github.io/hyperopt/getting-started/search_spaces/

# This file is copied over https://github.com/RasaHQ/nlu-hyperopt.git code

from hyperopt import hp

search_space = {
    "diet-classifier-epochs": hp.randint("diet-classifier-epochs", 75, 150),
    "response-selector-epochs": hp.randint("response-selector-epochs", 75, 150),
    "fallback-classifier-threshold": hp.uniform("fallback-classifier-threshold", 0.3, 0.9)
}
