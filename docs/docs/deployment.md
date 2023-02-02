# Deployment

!!! warning
    There are many details still missing. Where to deploy it is not decided.

## API

The API is a bit hefty to make and run, because for every language in giellatekno,
we need a lot of the compiled hfsts.

We need compiled fst files.

## build.py

The __build.py__ script runs various dockerfiles. First an image called
__fst-compiler__ will be built. It contains the hfst tools used to compile the
language models. Each individual language is then built in an image called
__fst-lang-{lang}__. These images use the __fst-compiler__ image as a base,
and compiles each artifact for that language. Finally, an image that includes
the necessary artifacts for all languages, as well as the application itself,
called __fst-app__ will be built.

The images of each language will be built in parallel, but the entire process
will take a long time.

