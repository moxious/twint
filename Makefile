default: docker_build
REGISTRY = gcr.io/testbed-187316
IMAGE ?= $(REGISTRY)/twint
DOCKER_TAG ?= latest

docker_build:
	docker build . -t $(IMAGE):$(DOCKER_TAG)

docker_push:
	docker push $(IMAGE):$(DOCKER_TAG)
