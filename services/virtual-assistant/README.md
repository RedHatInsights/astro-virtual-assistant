# Virtual assistant

This is the main REST API for virtual assistant. It listens for calls from users of the platform and routes the 
requests to watson and returns the contents of the "conversation" to the user.

## Running
This service can be run by using `make run` from the root of the project. It will start the service
listening on port 5000.

API spec is [served](http://127.0.0.1:5000/api/virtual-assistant-watson-extension/v2/openapi.json) by the service.
There are also [redocs](http://127.0.0.1:5000/redocs), [scalar](http://127.0.0.1:5000/scalar) and [swagger](http://127.0.0.1:5000/docs) frontends available for convenience.

## Testing
Tests can be found on [tests](./tests) and are run by invoking `make tests` on the root of the project. The tests
use `pytest` as a runner.
