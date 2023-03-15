# Deployment

!!! warning
    There are many details still missing. How and where to deploy it is not
    decided.

## Overview

The client and the api are deployed independently, each built as a docker image,
and deployed on Azure. The specific Azure "product" that runs a docker image,
and exposes it on a url, is named "Azure Container Instances".

## Client

Svelte builds into static html/css/js, and can be served by any web server.
It is a SPA, so webservers will have to route all requests to index.html.

### Build and deploy

The full process is to build the vite project, which outputs static html, css
and javascript. From those, an nginx docker image that hosts these sources
can be built. This image must be tagged to be able to push it to the Azure
Container Registry, so we tag, and push it. Finally, (if there already is a
container instance running), all we have to do is restart the container instance,
which will make sure to pull down the newly pushed image.

```bash
cd client/
npm run build
make image
docker tag fst-client gtfstcontainerregistry.azurecr.io/fst-client:latest

# must have docker logged into the container registry before this!
docker push gtfstcontainerregistry.azurecr.io/fst-client:latest

az container restart --name fst-client --resource-group test-fst
```

## API

The API uses compiled artifacts for the giellalt language models. Specifically,
each language should be compiled with

```bash
cd giellalt/lang-xxx
./configure --enable-fst-hyphenator --enable-spellers --enable-tokenisers --enable-phonetic --enable-tts
```

There are some 40-50 different languages, many of which takes a long time
to compile. For local development, using whichever files are already on
your system will be fine, and the site will show grayed out languages and tools
when the required files are not present.

### build.py

The __build.py__ script runs various dockerfiles. First an image called
__fst-compiler__ will be built. It contains the hfst tools used to compile the
language models. Each individual language is then built in an image called
__fst-lang-{lang}__. These images use the __fst-compiler__ image as a base,
and compiles each artifact for that language. Finally, an image that includes
the necessary artifacts for all languages, as well as the application itself,
called __fst-app__ will be built.

The images of each language will be built in parallel, but the entire process
will take a long time.


