# Astro virtual assistant

Astro is a virtual assistant for console.redhat.com. We are currently migrating away from [Rasa](https://rasa.com/docs/rasa/).
If you would like to see the legacy code head over to the [main](https://github.com/RedHatInsights/astro-virtual-assistant/tree/main) branch.

## Development

### Setting up your environment

Astro uses [uv](https://pypi.org/project/uv/) to manage its dependencies.
Follow the [instructions on uv](https://pypi.org/project/uv/#installation) to install it.

After installing, you are now ready to install the project development dependencies 
by running:

```bash
make install 
```

This will install all the required dependencies in a virtual environment created by [uv](https://pypi.org/project/uv/)
To access it you can run `uv run` to execute any command within the virtual environment.

### File structure

We are using a monorepo setup to hold our services and shared libraries.

- [deploy](./deploy) - Has our clowder files
- [libs](./libs) - Has any code that is to be shared by our dependencies.
  - [common](./libs/common) - Our shared library with configuration helpers, types and our session storage functions.
- [scripts](./scripts) - Scripts used in building or ci tasks.
- [services](./services) - Deployed services that compose virtual-assistant
  - [virtual-assistant](./services/virtual-assistant/README.md) - Public REST API in charge of listening to users and directing queries to watson or any other project as required.
  - [watson-extension](./services/watson-extension/README.md) - Internal REST API, listens for watson messages to provide additional information in behalf of the services within console.redhat.com

Refer to each service's README file for instructions on how to run it.

## Makefile targets

We use a custom makefile with some useful targets. The main Makefile is located on the root of the project at:
[Makefile](./Makefile). We have submodules stored in [scripts/make](scripts/make) folder

Each module has its own targets to help us with the development.

### Makefile

Has general targets for installing dependencies, cleaning and running the project.

- `install`: Syncs dependencies
- `run`: Runs virtual-assistant
- `run-watson-extension`: Runs watson-extension
- `redis`: Runs a redis container

### make/Makefile.variables.mk

Contains global variables used in all the other Makefiles to execute.

### make/Makefile.lint.mk

General purpose linting for our project. Inspects yml and python files.

- `lint`: Runs the linter in read only mode. Outputs the error but does not fix them.
- `lint-fix`: Runs the linter and attempts to fix the lint errors

### make/Makefile.test.mk

- `test`: Alias for `test-python`
- `test-python`: Run python tests
