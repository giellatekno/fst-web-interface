.PHONY: image run clean check-gt-home

have-image = $(shell docker images forrest | sed 1d | wc -l)

image:
	docker build . -t forrest

run: check-have-image
	docker run --rm -it forrest /bin/bash

gtuit-run: check-gt-home check-have-image
	docker run --rm -it -v $(GTHOME):/home/main forrest

clean:
	-docker image rm forrest
	#docker image prune -af


check-gt-home:
ifndef GTHOME
	$(error Environment variable GTHOME is not set)
endif

check-have-image:
	@if [ "${have-image}" != "1" ]; then \
		echo forrest docker image does not exist, run make image; \
		exit 1; \
	fi

printvar:
	echo $(have-image)
