# API

FastAPI automatically documents the routes in the API using OpenAPI. They
can be read at [/docs][docs] or [/redoc][redoc].

!!! note
    Use [hoppscotch][hoppscotch] to manually test out API queries.

[docs]: localhost:8000/docs
[redoc]: localhost:8000/redoc
[hoppscotch]: https://hoppscotch.io/

## Architecture

Routes in the API is dynamically imported from the __toolspecs/__ folder.

One file in the __toolspecs/__ folder corresponds to one route.

Each of those files defines a few names:

    summary            -- string
    description        -- string
    pipeline           -- list


## Project layout

    main.py            -- entry point
    toolspecs/         -- tool specifications
