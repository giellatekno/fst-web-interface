#!/bin/bash

# remove all stopped containers
docker container prune -f

# get a list of all "fst-*" images
FST_IMAGES=`docker images fst-* | sed 1d | cut -f1 -d" "`
APERTIUM_IMAGES=`docker images apertium-* | sed 1d | cut -f1 -d" "`

if [[ ! -z "${FST_IMAGES}" ]]; then
    docker image rm ${FST_IMAGES}
fi

if [[ ! -z "${APERTIUM_IMAGES}" ]]; then
    docker image rm ${APERTIUM_IMAGES}
fi

# -a (all images, not just dangling ones)
# -f for "force" (don't ask for confirmation)
docker image prune -a -f
