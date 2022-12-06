shell:
	docker run --rm -it --entrypoint bash fst-app

# for now, no -d flag (-d means "detached". running with -d doesn't connect a terminal)
run:
	docker run -p 8000:8000 --env WEB_CONCURRENCY=`cat /proc/cpuinfo | grep "cpu cores" | uniq | cut -d ":" -f2 | sed "s/ //g"` fst-app
