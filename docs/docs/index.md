# Overview

## What even is this?

__fst-web-interface__ is a web-based set of language tools, primarily aimed
at linguists. There are tools for _paradigm generation_, _analysis_, etc,
for a number of languages, some better than others, that the Giellatekno
group develops language models for.

__fst-web-interface__ replaces the _cgi-bin_-based setup, which can currently
be seen at [giellatekno.uit.no](https://giellatekno.uit.no/smilang.eng.html)


## Architechture

__fst-web-interface__ consists of two parts: a _client-side_ [Svelte][svelte] web app,
and a _server-side_ [FastAPI][FastAPI] API.

The API uses the normal [hfst][hfst] tool-chain with the [Giellatekno language models][models]
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

    api/                   -- API sub-project directory
        main.py            -- entry point of the FastAPI app
        toolset.py         -- defines what a "tool" is
        toolspecs/         -- the tools, and how they invoke hfst to produce results
    client/                -- The Svelte client-side app
        index.html         -- Skeleton html for svelte
        locales/           -- localization
            data/          -- locale data, stored in XML files (brought over from the previous
                              Apache Forrest-based solution
            {lang}.json    -- the compiled locale data for that language
            xmltojson.py
            make_final.py  -- scripts for compiling the stuff in /data to {lang}.json
        package.json
        package-lock.json
        node_modules/      -- standard package info and packages in js projects
        vite.config.js
        svelte.config.js
        jsconfig.json      -- configuration files for the tools
    docs/                  -- documentation
        README.md          -- documentation documentation
        mkdocs.yml         -- mkdocs configuration file
        docs/              -- markdown files of the actual documentation
    cgi-scripts/           -- a copy of the old cgi scripts, for reference
    perl_extractions/      -- a temporary place with some python translations of some perl scripts
