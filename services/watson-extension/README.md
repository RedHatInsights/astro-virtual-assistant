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

The following UML diagram illustrates an API that returns advisor recommendations. 
It requires a single client (RHEL Advisor) and one template. 
The diagram also highlights different test levels, showing what is being mocked and tested at each stage.

![API Diagram](./diagram.mermaid)

