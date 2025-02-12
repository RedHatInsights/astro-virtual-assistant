# Astro virtual assistant

Astro is a virtual assistant for console.redhat.com. We are currently migrating away from [Rasa](https://rasa.com/docs/rasa/).
If you would like to see the legacy code head over to the [main](https://github.com/RedHatInsights/astro-virtual-assistant/tree/main) branch.

Warning: Instructions below might be outdated

## Development

### Setting up your environment


Astro also uses [uv](https://pypi.org/project/uv/) to manage it's dependencies.
Follow the [instructions on uv](https://pypi.org/project/uv/#installation) to install it.

After installing [pipenv](https://pypi.org/project/), you are now ready to install the project development dependencies 
by running:

```bash
pipenv install --dev
make install 
```

This will install [rasa](https://rasa.com/docs/rasa/) inside the virtual environment created by
[pipenv](https://pypi.org/project/).
To access it you can run `pipenv run rasa` to execute any 
[rasa](https://rasa.com/docs/rasa/) command or `pipenv shell` to start a session within the virtual environment.

> :information_source:  Any command below assumes that you are within a pipenv shell (i.e. after executing `pipenv shell`). If you
> don't want to use that mode, just preprend `pipenv run` to any command.


### File structure

The training files are inside [data](./data) directory. The common files are on the root of this directory and specific
files are in the subfolders. The current approach is to have a directory for the namespace/bundle and a sub-directory 
for the application. Each application can write its own `nlu`, `domain`, `stories` and `rules` file depending on its needs.

For example, [data/console/rbac/stories.yml](data/console/rbac/nlu.yml) holds the `nlu` info for `RBAC`.

Intents and responses are spread throughout the data directory in `domain.yml` files. This allows us to make changes to one bundle without affecting the other.

The custom actions (python code) is found within [actions](./actions) and holds the required code to execute it.

Test files are found in the [tests](libs/common/tests) folders.


### Training the model

You can run `make train` to start a full training session, or
you can do an incremental training of your previous model with `make train-finetune`. 

Note that incremental training doesn't work if you added any new intents or actions.

### Storing the models

The models are by default saved to `./models`.

### Offline Token

To be able to locally run the actions, you need to have a valid offline token for https://sso.redhat.com. 
All the API calls will be made on behalf of the user of this token. You can generate an offline token at
[https://access.redhat.com/management/api](https://access.redhat.com/management/api) by clicking "Generate token".
Copy this token to the environment variable `OFFLINE_REFRESH_TOKEN` (`.env` file is supported).

> :note: If you want to use the stage environment, generate the token at 
> [https://access.stage.redhat.com/management/api](https://access.stage.redhat.com/management/api) and also set the
> environment variable `SSO_REFRESH_TOKEN_URL` to `https://sso.stage.redhat.com/auth/realms/redhat-external/protocol/openid-connect/token`
>
> You will also need to point the `CONSOLEDOT_BASE_URL` environment variable to [https://console.stage.redhat.com](https://console.stage.redhat.com), and make sure that your http proxy url is set up properly.

### Starting tracker store database

This app is configured to use a postgres database to store its conversation history. To start the database, run `make run-db`.

Once rasa is running, it will automatically migrate, creating an `events` table.

[Tracker store docs](https://rasa.com/docs/rasa/tracker-stores/#sqltrackerstore)

### Executing

Once you have a trained model, you can run a local chat instance with `rasa shell` or `make run-cli`.

After setting up your offline token, start the actions server by executing `rasa run actions --auto-reload` or `make run-actions`.

### Errors when launching

#### Failed to find input channel class for 'channels.console.ConsoleInput'

> RasaException: Failed to find input channel class for 'channels.console.ConsoleInput'. Unknown input channel. Check your credentials configuration to make sure the mentioned channel is not misspelled. If you are creating your own channel, make sure it is a proper name of a class in a module.

This error happens when the class channels.console.ConsoleInput is not found OR the file containing that class fails to load. 
If the later, the error doesn't appear in the console, but we can check it by importing that file.

Running the following should make the error evident or at least give more information.

```bash
python -c "import channels.console"
```

## Makefile targets

We use a custom makefile with some useful targets. The main Makefile is located on the root of the project at:
[Makefile](./Makefile). We have submodules stored in [make](scripts/make) folder

Each module has its own targets to help us with the development.

### Makefile

Has general targets for installing dependencies, cleaning and running the project.

- `install`: Installs the dependencies and dev-dependencies of both rasa and actions server
- `clean`: Cleans any know temporal file, model, cache, results or reports from rasa.
- `run`: Runs rasa
- `run-interactive`: Runs rasa in interactive mode
- `run-actions`: Runs actions server
- `run-cli`: Runs rasa and shows the CLI/shell mode
- `run-db`:
- `db`:
- `drop-db`:
- `compose`:

### make/Makefile.variables.mk

Contains global variables used in all the other Makefiles to execute rasa and python in a common way. Also checks for a
`DEBUG` or `VERBOSE` environment to include the respective flags into the train and run arguments.

### make/Makefile.train.mk

Contains targets to train the models

- `train`: Full train, intents and stories
- `train-finetune`: Incremental training
- `train-nlu`: Only trains the NLU components

### make/Makefile.lint.mk

General purpose linting for our project. Inspects yml and python files.

- `lint`: Runs the linter in read only mode. Outputs the error but does not fix them.
- `lint-fix`: Runs the linter and attempts to fix the lint errors

### make/Makefile.test.mk

- `test`: Alias for `test-rata` and `test-python`
- `test-rasa`: Alias for `test-stories`, `test-data` and `test-nlu`
- `test-data` (alias: `validate`): Checks for inconsistencies in rasa's files.
- `test-nlu`: Runs a data split and nlu tests in the results. Split files are written under `.astro/train_test_split` 
- `test-stories-nlu`: Extracts user utterances and intents from the test stores and runs the nlu test on these. Files are written under `.astro/nlu-from-stories`
- `test-stories`: Run stories tests
- `test-python`: Run python tests
- `test-identity`: Convenience method to call the API
- `test-is-org-admin`: Convenience method to call the API as an org admin
- `test-is-not-org-admin`: Convenience method to call the API as a non org admin

### make/Makefile.hyperopt.mk

- `hyperopt-nlu`: Does an nlu optimization. See [Optimizing hyperparameters](#Optimizing-hyperparameters)

## Optimizing hyperparameters

These are the parameters used in our configs. There are multiple tools such as 
[hyperopt](https://github.com/hyperopt/hyperopt). There is a Rasa implementation that uses
hyperopt to optimize the NLU data. It can be see at [RasaHQ/nlu-hyperopt](https://github.com/RasaHQ/nlu-hyperopt/).

We have a make target (`hyperopt-nlu`) that sets this up for this project. 
It takes the configuration from [config/nlu-hyperopt/](./config/nlu-hyperopt) 
but further configuration can be done after first run in [.astro/nlu-hyperopt]. 
Refer to our config files and the original repository for more information.

## Scripts

To make it easier to review all our intents and their training examples, there are some scripts found on [scripts/](./scripts).
-  [scripts/dump_data.py](./scripts/dump_data.py) Will scan the [data](./data) directory, load all the intents and dump all
   of these in stdin in CSV format. It will also validate for repeated intents, which is something that could be
   extracted to a separate process.
- [scripts/update_google_sheet.py] It will read the file `./intents.csv` and upload it to google sheets using the following environmental variables:
  - SPREADSHEET_ID: Id of the google sheet
  - WORKSHEET_NAME: Name of the work sheet
  - GOOGLE_CLOUD_ACCOUNT: Service account email
  - GOOGLE_CLOUD_ACCOUNT_SECRET: Private key of the service account email
  
  This is currently done automatically on commits to main branch by one of our github workflows.

## Apple silicon

There are some extra steps required on apple silicon CPUs

### tensorflow

The tensorflow versions required by rasa is not available on apple silicon. Fortunately there is a [bridge package](https://developer.apple.com/metal/tensorflow-plugin/) available for installation.

In your python venv run the following:
```sh
# pip on macos only has tensorflow versions >=2.13.0
python -m pip install tensorflow-macos==2.12.0 # rasa requires 2.12.0
python -m pip install tensorflow-metal

```

### Out of memory issues while training a mode

You may see that the `make train` has exited with code **9**. This code means that some other process killed the process. After inspection, the train command was eating all the memory. You can reduce the memory requirements by reducing the number of epochs of the training. The numbers can be adjusted in the `./config.yml` file.

Because in Mac you can't install python packages outside of venv, you might hav to change some of the make commands so they do not run the pipenv twice. For example:
```diff
- pipenv run ${RASA_EXEC} run ${RASA_RUN_ARGS} --logging-config-file logging-config.yml 
+ ${RASA_EXEC} run ${RASA_RUN_ARGS} --logging-config-file logging-config.yml
```
