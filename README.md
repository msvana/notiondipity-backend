# Notiondipity Backend

This repository contains an implementation of a backend
for the [Notiondipity](https://github.com/msvana/notiondipity-extension)
browser extension. It fulfills the following
functions:

- It acts as a proxy for calling the Notion API when needed. Notion API can't be
  used directly from a browser because it doesn't support cross-site scripting.
- It uses OpenAI's APIs to create Notion page embeddings and to generate project
  ideas.
- It stores embeddings, Notion page titles and encrypted contents in a Postgres 
  database. Getting this data from a database is much faster than calling Notion API

## API

The backend exposes a REST-like API with following endpoints. Except
for the `/v1/token` endpoint, all API requests need to have an
`Authorization` containing `Bearer {JWT}`.

### /v1/token/ (POST)

Expects an OAuth2 code and a redirect URL. Returns a JWT that is
then used to authenticate all other API requests. The JWT contains a
unique Notion user ID and a Notion API access token.

### /has-data/ (GET)

Checks if user's Notion data have been already processed and can
be used to recommend similar pages, generate ideas or perform other
actions

### /refresh-embeddings/ (GET)

Refreshes Notion page embeddings, contents and titles for a given
user. Since this is a computationaly intensive operation each user
can only perform it once every 30 minutes.

### /ideas/ (POST)

Generates project ideas from provided content and the content of
up to 2 most similar Notion pages. This usually takes several
tens of seconds.

### /v2/recommend/ (POST)

Returns a list of pages most similar to provided content. Can
be used both to perform semantic search and to recommend pages
similar to the one currently open.
