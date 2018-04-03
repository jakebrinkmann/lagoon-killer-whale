.DEFAULT_GOAL := build
VERSION    := $(or $(TRAVIS_TAG),`cat version.txt`)
REPO       := $(or $(TRAVIS_REPO_SLUG),"`whoami`/$(shell basename $(shell pwd))")
REPO       := "$(DOCKER_USER)/lagoon-killer-whale"
BRANCH     := $(or $(TRAVIS_BRANCH),`git rev-parse --abbrev-ref HEAD | tr / -`)
COMMIT     := $(or $(TRAVIS_COMMIT),`git rev-parse HEAD`)
COMMIT_TAG := $(REPO):$(COMMIT)
BRANCH_TAG := $(REPO):$(BRANCH)-$(VERSION)

build:
	@docker build --target application -f Dockerfile -t $(COMMIT_TAG) --rm=true --compress $(PWD)

tag:
	@docker tag $(COMMIT_TAG) $(BRANCH_TAG)

login:
	@$(if $(and $(DOCKER_USER), $(DOCKER_PASS)), docker login -u $(DOCKER_USER) -p $(DOCKER_PASS), docker login)

push: login
	docker push $(REPO)

debug:
	@echo "VERSION:    $(VERSION)"
	@echo "REPO:       $(REPO)"
	@echo "BRANCH:     $(BRANCH)"
	@echo "COMMIT_TAG: $(COMMIT_TAG)"
	@echo "BRANCH_TAG: $(BRANCH_TAG)"

docker-deploy: debug build tag push

clean:
	@rm -rf dist build lcmap_pyccd_worker.egg-info
	@find . -name '*.pyc' -delete
	@find . -name '__pycache__' -delete

docker-deps-up:
	@docker network create backend
	@docker-compose -f setup/docker-compose.yml up -d

docker-deps-up-nodaemon:
	@docker network create backend
	@docker-compose -f setup/docker-compose.yml up

docker-deps-down:
	@docker-compose -f setup/docker-compose.yml down -v
	@docker network rm backend

test-local: clean
	@docker build --target tester -f Dockerfile -t $(COMMIT_TAG) --rm=true --compress $(PWD)
	@docker run --rm -t --net=backend $(COMMIT_TAG)

test: docker-deps-up test-local docker-deps-down
