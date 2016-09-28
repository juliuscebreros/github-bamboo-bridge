# Github-Bamboo bridge

Receives github pull request hook and calls the local bamboo server to run a plan

## Configure
1. Create a .env file in the root of this server
2. Set these properties:

```
SECRET_KEY="SECRET_KEY"
BAMBOO_USER="julius"
BAMBOO_PASSWORD="password"
BAMBOO_PORT=8085
PORT=7080
```

## Setup Webhooks
1. In Github, YOUR_REPO -> Settings -> Webhooks
2. Payload URL: `http://buildserver.com/pullrequest/BAMBOO_BUILD_ID`
3. Secret: the `SECRET_KEY` in your .env config
4. Tick `Let Me Select Individual Events`
5. Tick `pull_request`
