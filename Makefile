CONTAINERS=`docker ps -a -q`
IMAGES=`docker images -q`

# pull the tag from version.py
TAG=0.0.1
WORKERIMAGE=espa-web:$(TAG)

docker-build:
	docker build -t $(WORKERIMAGE) $(PWD)

docker-shell:
	docker run -it --entrypoint=/bin/bash usgseros/$(WORKERIMAGE)

docker-deps-up:
	docker network create backend
	docker-compose -f setup/docker-compose.yml up -d

docker-deps-up-nodaemon:
	docker-compose -f setup/docker-compose.yml up

docker-deps-down:
	docker-compose -f setup/docker-compose.yml down
	docker network rm backend

deploy-pypi:

deploy-dockerhub:

clean-venv:
	@rm -rf .venv

clean:
	@find . -name '*.pyc' -delete
	@find . -name '__pycache__' -delete

