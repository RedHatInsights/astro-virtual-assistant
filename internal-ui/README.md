# Internal UI for Virtual Assistant

This UI is used as an internal tool to follow up conversations and being able to understand more effectively the way
virtual assistant is being used.

## Initial setup

Start by installing the local dependencies by running
```
npm install
```

## Working locally

You can either setup a full local environment or use internal.stage environment to develop locally.

### Fully local

At very least you need to run the tracker database and the internal server. 

### Using internal stage

You can start the proxy by running `session=<your-session> npm run proxy` (or change to `session=<your-session> npm run proxy:dev` to make changes to the proxy).

Your session token can be obtained by visiting [internal turnpike session page](https://internal.console.stage.redhat.com/api/turnpike/session).

## Running

After running a local internal server or the proxy, you can start development with

- Run the dev server (`npm run dev`)
- Open the displayed local url on any browser.
