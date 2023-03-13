#!/bin/bash

# a list of all "fst-*" images
IMAGES=`docker images fst-* | sed 1d | cut -f1 -d" "`

echo ${IMAGES}
if [[ ! -z "${IMAGES}" ]]; then
    docker image rm ${IMAGES}
fi

# -a (all images, not just dangling ones)
# -f for "force" (don't ask for confirmation)
docker image prune -a -f
