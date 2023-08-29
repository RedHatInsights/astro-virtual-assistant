# Astro virtual assistant

Astro is a virtual assistant for console.redhat.com created with [Rasa](https://rasa.com/docs/rasa/).

## Development

### Setting up your environment

Astro uses [pipenv](https://pypi.org/project/) to manage it's dependencies. 
Follow the [instructions on pipenv](https://pypi.org/project/pipenv/#installation) to install it.

After installing [pipenv](https://pypi.org/project/), you are now ready to install the project development dependencies 
by running:

```bash
pipenv install --dev
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

For example, [data/console/rbac/stories.yml](./data/console/rbac/nlu.yml) holds the `nlu` info for `RBAC`.

Intents and responses are spread throughout the data directory in `domain.yml` files. This allows us to make changes to one bundle without affecting the other.

The custom actions (python code) is found within [actions](./actions) and holds the required code to execute it.

Test files are found in the [tests](./tests) folders.


### Training the model

You can run `make train` to start a full training session, or
you can do an incremental training of your previous model with `make finetune`. 

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
