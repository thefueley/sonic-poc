SHELL := /bin/bash
# =================================================================
# Building containers
VERSION ?= 1.0

all: sonic

sonic: build push

build:
	docker buildx build --load \
		-f docker/dockerfile.sonic \
		-t thefueley/sonic-poc:$(VERSION) \
		--build-arg BUILD_REF=$(VERSION) \
		--build-arg BUILD_DATE=`date -u +"%Y-%m-%dT%H:%M:%SZ"` \
		.
push:
	docker buildx build --push \
		-f docker/dockerfile.sonic \
		-t thefueley/sonic-poc:$(VERSION) \
		--platform linux/amd64,linux/arm64 \
		--build-arg BUILD_REF=$(VERSION) \
		--build-arg BUILD_DATE=`date -u +"%Y-%m-%dT%H:%M:%SZ"` \
		.
# =================================================================
# Run app in local Docker container
APP_NAME=sonic-poc
IMAGE_NAME=thefueley/sonic-poc:$(VERSION)
HOST_PORT=5001
PORT=5000

RUNNING_CONTAINER_ID=$(shell docker ps -q -f name=$(APP_NAME))
STOPPED_CONTAINER_ID=$(shell docker ps -aq -f name=$(APP_NAME))

run:
	@if [ -z "$(RUNNING_CONTAINER_ID)" ]; then \
		echo "Starting new container..."; \
		docker run -d --name $(APP_NAME) -p $(HOST_PORT):$(PORT) $(IMAGE_NAME); \
	else \
		echo "Container $(APP_NAME) is already running"; \
	fi

rerun: stop clean run

stop:
	@if [ ! -z "$(RUNNING_CONTAINER_ID)" ]; then \
		echo "Stopping container $(APP_NAME)..."; \
		docker stop $(RUNNING_CONTAINER_ID); \
	else \
		echo "No running container to stop."; \
	fi

clean:
	@if [ ! -z "$(STOPPED_CONTAINER_ID)" ]; then \
		echo "Removing container $(APP_NAME)..."; \
		docker rm $(STOPPED_CONTAINER_ID); \
	else \
		echo "No container to remove."; \
	fi
