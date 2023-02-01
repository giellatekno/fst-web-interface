# Meta Documentation

> Meta documentation, i.e. documentation about the documentation.
>
> This is the same document as __docs/README.md__.

The documentation is an [mkdocs][1] site, with the [material theme][2].
Documentation is written as markdown files, and gets rendered to html with
a nice theme by these tools.

[1]: https://www.mkdocs.org/
[2]: https://squidfunk.github.io/mkdocs-material/


## View

The build output is a static web site located in the __site/__ folder. Just open
up the index.html page in a browser to view the documentation.

    firefox site/index.html


## Writing documentation


### First time setup

__mkdocs__ is a python tool. Create a virtual environment, activate it, and
install the requirements. The first and last step is only done once.

    python3 -m venv .venv
    . .venv/bin/activate
    pip install -r -requirements.txt

When coming back to the documentation, only the second command (`. .venv/bin/activate`),
needs to be run.


### Writing and serving

In order to write documentation, just write markdown files, in the __docs/__ folder.
To be able to see the generated html output while writing, mkdocs can be run with 

    mkdocs serve

If the fst-web-interface application is also running, the default port will
be used. Specify another one with:

    mkdocs serve -a localhost:8001

Open up a browser at that address to see the generated documentation as you write it.

To build the final documentation site, use

    mkdocs build

It ends up as a static build in the __site/__ directory, as mentioned above.
