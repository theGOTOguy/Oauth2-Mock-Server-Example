# Oauth2-Mock-Server-Example
Example of getting auth tokens from the OAuth2 Mock server

We will use [Navikt's Mock Oauth2](https://github.com/navikt/mock-oauth2-server) Server to back this example.
In particular, this guide will walk you through:

1)  Starting up the Docker OAuth2 server with appropriate settings.
2)  Using Python to authenticate a test user against this server.

## Setting Up the OAuth2 Mock Server

First, pull the docker image with:

```bash
docker pull ghcr.io/navikt/mock-oauth2-server:2.1.10
```

You can now run the server with:
```bash
docker-compose up
```

Note that, if the server is running in this way, we can get a login page by sending, e.g., a request to [this url](http://localhost:8080/default/authorize?client_id=foo&response_type=code&redirect_uri=http://localhost:3000&scope=openid).

## Example Getting a Token

```bash
virtualenv venv -p python3
pip install -r requirements.txt
venv/bin/python example_auth.txt
```

## Why Aren't Scopes Attached to the Access Token?

[navikt's server doesn't include it because nimbus stopped doing so](https://github.com/jenspav/mock-oauth2-server/commit/25701a98f5f0ba7295df460043b7590a9fc58e9f)
[We also tried this one, but a bug prevents scopes from working.  It's now been six months and they haven't cut a new release.](https://github.com/axa-group/oauth2-mock-server/issues/259)
