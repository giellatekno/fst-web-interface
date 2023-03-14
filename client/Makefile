image:
	docker build -t fst-client -f Dockerfile.client .

shell:
	docker run --rm -it fst-client /bin/bash

run:
	docker run --rm -it -p 80:80 fst-client

deploy:
	# tag with :latest, then just do restart
	# docker tag fst-client gtfstcontainerregistry.azurecr.io/fst-client:latest
	# docker push gtfstcontainerregistry.azurecr.io/fst-client:latest
	
	# hmm.. update the container instance?
	# the thing is, the dns-name-label is the same
	
	# on updates, just restart. the new image will be pulled
	# az container restart --name fst-client --resource-group test-fst
	
	# if first time, will need to create
	# --registry-username is same as the name of the regsitry
	# --registry-password I do not know how to get programmatically...hmm
	# az container create --resource-group test-fst --name fst-client --location norwayeast --image gtfstcontainerregistry.azurecr.io/fst-client:latest --ports 8000 --dns-name-label fst-api-test --registry-username gtfstcontainerregistry --registry-password "..."

	az ...somthing
