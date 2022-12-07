shell:
	docker run --rm -it --entrypoint bash fst-app

# for now, no -d flag (-d means "detached". running with -d doesn't connect a terminal)
run:
	docker run -p 8000:8000 --env WEB_CONCURRENCY=`cat /proc/cpuinfo | grep "cpu cores" | uniq | cut -d ":" -f2 | sed "s/ //g"` fst-app


# print out all languages that are compiled
# i.e. if we have the docker image "fst-lang-xxx", then xxx will be printed
# one language per line

havelangs:
	@docker images | grep "fst-lang-*" | cut -d " " -f1 | sed "s/fst-lang-//"
