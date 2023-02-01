# Overview

## What even is this?

__fst-web-interface__ is a web-based set of language tools, primarily aimed
at linguists. There are tools for _paradigm generation_, _analysis_, etc,
for a number of languages, some better than others, that the Giellatekno
group develops language models for.

__fst-web-interface__ replaces the _cgi-bin_-based setup, which can currently
be seen at [giellatekno.uit.no](https://giellatekno.uit.no/smilang.eng.html)


## Architechture

Broadly speaking, there is a _client-side_ [Svelte][svelte] web app, which
fetches data from a _server-side_ [FastAPI][FastAPI] API. The API uses the
normal [hfst][hfst] tool-chain with the [Giellatekno language models][models]
to provide results to queries coming from the _client-side_.

For everything related to __hfst__ and the Giellatekno language models, check out
[Giellatekno documentation][gtdocs].

[svelte]: https://svelte.dev
[FastAPI]: https://fastapi.tiangolo.com/
[hfst]: https://hfst.github.io/
[models]: https://github.com/giellalt
[gtdocs]: https://giellalt.github.io/


## Project layout

In the root folder, the client-side page is stored.

api  cgi-scripts  docs  index.html  jsconfig.json  locales  node_modules  package.json  package-lock.json  perl_extractions  README.md  src  svelte.config.js  vite.config.js

    api/              -- everything related to the api
    cgi-scripts/      -- a copy of the old cgi scripts, for reference
    locales/          -- locale data
    docs/             -- documentation (you're reading it now)
        README.md     -- documentation documentation
    node_modules/     -- used by npm, where js packages used in the project are stored
