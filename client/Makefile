image:
	docker build . -t fst-client -f Dockerfile.client

shell:
	docker run --rm -it fst-client /bin/bash

run:
	docker run --rm -it -p 80:80 fst-client

deploy:
	# must build first (or just take latest build?)
	# prereq: must be logged in (az login)
	#   check login of azure: az account list (which must be parsed..)
	az login
	# prereq: must be logged into container registry
	#    cmd: az acr login --name gtfstcontainerregistry
	#       (echoes "Login Succeeded" if ok)
	az acr login --name gtfstcontainerregistry
	# need the admin account of the registry to be able to deploy the
	# image from the registry directly to Azure Container Instances

	# tag with :latest, then just do restart
	# docker tag fst-client gtfstcontainerregistry.azurecr.io/fst-client:latest
	# docker push gtfstcontainerregistry.azurecr.io/fst-client:latest
	
	# now to either create or update the running container:
	# if first time setup, will need to create the container
	# --registry-username is same as the name of the regsitry
	# --registry-password I do not know how to get programmatically,
	#  but can be found on the website portal
	# az container create --resource-group test-fst --name fst-client --location norwayeast --image gtfstcontainerregistry.azurecr.io/fst-client:latest --ports 8000 --dns-name-label fst-api-test --registry-username gtfstcontainerregistry --registry-password "..."
	
	# If it has already been set up, all we have to do is restart the instance,
	# which will check for a new image, and pull it down if it finds a new one
	# az container restart --name fst-client --resource-group test-fst
	

	az ...somthing
