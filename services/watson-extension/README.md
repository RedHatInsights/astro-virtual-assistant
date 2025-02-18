# Virtual assistant watson extension

This service bridges platform data for a specific user through the Virtual Assistant.

Its API is designed to process user queries and provide information that requires platform data, such as advisor 
recommendations, notifications, integrations, feedback, and admin contact.

The service uses multiple clients, each interacting with different APIs to fetch relevant data and generate responses 
that enrich user conversations.

Responses are built using a templating engine (Jinja), making it easier to update them without modifying the code.

API endpoints (routes) should be scoped based on the type of flow being implemented. 
In some cases, multiple applications may need to be queried, leading to a single API endpoint that utilizes multiple clients.

## Sample diagram

The following UML diagram illustrates a Client (connection to a service in the platform), a Route (endpoint) component, 
and a template for the endpoint. 
The diagram also highlights different test levels, showing what is being mocked and tested at each level.

In reality, a route could use multiple clients to perform their operation.

![API Diagram](./diagram.mermaid)

## Running
This service can be run by using `make run-watson-extension` from the root of the project. It will start the service
listening on port 5050.

API spec is [served](http://127.0.0.1:5050/api/virtual-assistant-watson-extension/v2//openapi.json) by the service.
There are also [redocs](http://127.0.0.1:5050/redocs), [scalar](http://127.0.0.1:5050/scalar) and [swagger](http://127.0.0.1:5050/docs) frontends available for convenience.

## Developing

This section is still in development, this should be updated as we make changes to our design.

The current architecture makes use of `clients` to communicate with other services in the platform, `core` layer to
handle the business logic and `routes` to handle the incoming Http rests requests from watson and finally 
`templates` to render the messages we got from the customers.

We are currently targeting only UI on our console, but we could configure out templates to use different outputs
depending on the formats we require.

If we ever need to support a different communication mechanism (i.e. [MCP](https://modelcontextprotocol.io/introduction))
we could do one of the following:

1. Create 2 new python packages in this repository. One for the http-rest routes (i.e. watson-extension-rest)
and other for mcp (i.e. watson-extension-mcp). The later could be built on quart, or we could use a library that implements
MCP and has support for [injector](https://pypi.org/project/injector/).
2. If what we need to support is compatible with HTTP (i.e. JSONRPC over HTTP), we could support it in the same application
by using the headers to decide how to translate the input and output of the request.

## Running locally

To be able to communicate to services within console.redhat.com, you need to have a valid offline token for https://sso.redhat.com.
All the API calls will be made on behalf of the user of this token. You can generate an offline token at
[https://access.redhat.com/management/api](https://access.redhat.com/management/api) by clicking "Generate token".
Copy this token to the environment variable `DEV_PLATFORM_REQUEST_OFFLINE_TOKEN` (`.env` file is supported).

> If you want to use the stage environment, generate the token at
> [https://access.stage.redhat.com/management/api](https://access.stage.redhat.com/management/api) and also set the
> environment variable `DEV_PLATFORM_REQUEST_REFRESH_URL` to `https://sso.stage.redhat.com/auth/realms/redhat-external/protocol/openid-connect/token`
>
> You will also need to point the `PLATFORM_URL` environment variable to [https://console.stage.redhat.com](https://console.stage.redhat.com), and make sure that your http proxy url is set up properly.

## API

The public API follows this path style: `/{group}/{service}/{operation}` e.g. `/insights/advisor/recommendations`.
Try to group endpoints under the most appropriate group and service. If an API interacts with multiple services, 
use the one most relevant to the operation's end goal.

All services will return a `response` field containing a string. For example:

```json
{
  "response": "Here are your top recommendations from Advisor:\n 1. Clean your room.\n 2. Take out the trash.\n 3. Floss your teeth.\n"
}
```

Additional attributes may be included. However, at the time of writing, the Watsonx Assistant UI does not support nested attributes in responses—only top-level attributes can be combined.
Note: This may change in the future, so please verify the current capabilities of Watsonx Assistant.

## Testing
Tests can be found on [tests](./tests) and are run by invoking `make tests` on the root of the project. The tests
use `pytest` as a runner and are currently focused on clients and routes. See [client test_advisor](./tests/clients/insights/test_advisor.py) 
and [route test_advisor](./tests/routes/insights/test_advisor.py) for examples.
