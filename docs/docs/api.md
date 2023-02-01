# API

## Project layout

    main.py            -- entry point
    toolset.py         -- defines what a tool is
    toolspecs/         -- individual tool specifications
    config.py          -- Reads system configuration
                          Note: NOT a place to configure how the api will behave
    util.py            -- Various utilities


## Routes

The API exposes one route per tool. They take their arguments on the path of
the url. Language and input is also taken in on the path.

The simplest way to explain how the path looks for the tool routes, is this:

    /{tool}/{lang}/{input}

That is, if a user is exploring the `"analyze"` tool for north sami (`"sme"`),
and writes down the input `"viessu"`, the query path will be

    /analyze/sme/viessu

!!! note
    FastAPI automatically documents the routes in the API using OpenAPI. They
    can be read at [/docs][docs] or [/redoc][redoc]. The [/docs][docs] one can
    be used to test out queries to the API. It's also possible to use a tool
    like [hoppscotch][hoppscotch] to run test queries against the API.

[docs]: localhost:8000/docs
[redoc]: localhost:8000/redoc
[hoppscotch]: https://hoppscotch.io/


## Architecture

Routes in the API is dynamically imported from the __toolspecs/__ folder.

One file in the __toolspecs/__ folder corresponds to one route.


### Tools

Tools are python files located in the __toolspecs/__ folder. They are python
scripts, but certain variable names will be interpreted and read specially.
Defining a name __summary__ as a string will make that string show up in the
OpenAPI documentation. A longer __description__ can also be given. What the
tool does is specified by the variable named __pipeline__.

### pipeline

Can be either a dictionary or a list. If it is a dictionary, the keys are strings
of 3-letter iso language names, and the value is a pipeline list of that language.
The special key `"*"` will be used for all languages that are not specified.

### pipeline list

A pipeline list (which is just a normal python list) consists of a series
of steps that will be done in sequence. The input to the first step is the
input from the route. The output from the last step is the return value of
the route. Each step takes input from it

A pipeline list (which is just a normal python list) specifies the operations
that this tool will do to its input. Each entry in the list can be either
a list or a function. If it is a function (async or not), it will be called,
and the output will be the input for the next step.

    route input => step1 => step2 => stepN => response from route


