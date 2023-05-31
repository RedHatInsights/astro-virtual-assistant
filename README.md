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

> :info: Any command below assumes that you are within a pipenv shell (i.e. after executing `pipenv shell`). If you
> don't want to use that mode, just preprend `pipenv run` to any command.


### File structure

The training files are inside [data](./data) directory. The common files are on the root of this directory and specific
files are in the subfolders. The current approach is to have a directory for the namespace/bundle and a sub-directory 
for the application. Each application can write its own `nlu`, `stories` and `rules` file depending on its needs.

For example, [data/console/rbac/stories.yml](./data/console/rbac/nlu.yml) holds the `nlu` info for `RBAC`.

The custom actions (python code) is found within [actions](./actions) and holds the required code to execute it.

Test files are found in the [tests](./tests) folders.

> :warning: At this point, all the applications share the same [domain.yml](./domain.yml) file and every `intent` must exist in
this file. This might change in the future.

### Training the model

You can run `rasa train` to start a full training session or if appending `--finetune`
you can do an incremental training of your previous model. Note that incremental training doesn't work if you added
new intent or actions.

### Executing

Once you have a trained model, you can run a local chat instance by running `rasa shell`.

To be able to locally run the actions, you need to have a valid offline token for https://sso.redhat.com. 
All the API calls will be made on behalf of the user of this token. You can generate an offline token at
[https://access.redhat.com/management/api](https://access.redhat.com/management/api) by clicking "Generate token".
Copy this token to the environment variable `OFFLINE_REFRESH_TOKEN` (`.env` file is supported).

> :note: If you want to use the stage environment, generate the token at 
> [https://access.stage.redhat.com/management/api](https://access.stage.redhat.com/management/api) and also set the
> environment variable `SSO_REFRESH_TOKEN_URL` to `https://sso.stage.redhat.com/auth/realms/redhat-external/protocol/openid-connect/token`

When you are ready, start the actions server by executing `rasa run actions --auto-reload`. 
