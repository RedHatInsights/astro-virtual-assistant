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

The current architecture makes use of `clients` to communicate with other services in the platform, `routes` to handle
incoming requests from watson and `templates` to render the messages we got from the customers.

We could create an additional layer to handle the business logic if we feel the routes is doing too much work already.

We are currently targeting only UI on our console, but we could configure out templates to use different outputs
depending on the formats we require.

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
