SHELL := /bin/bash
# =================================================================
# Building containers
VERSION := 1.0

all: sonic

sonic: build push

build:
	docker buildx build --load \
		-f docker/dockerfile.sonic \
		-t thefueley/sonic:$(VERSION) \
		--build-arg BUILD_REF=$(VERSION) \
		--build-arg BUILD_DATE=`date -u +"%Y-%m-%dT%H:%M:%SZ"` \
		.
push:
	docker buildx build --push \
		-f docker/dockerfile.sonic \
		-t thefueley/sonic:$(VERSION) \
		--platform linux/amd64,linux/arm64 \
		--build-arg BUILD_REF=$(VERSION) \
		--build-arg BUILD_DATE=`date -u +"%Y-%m-%dT%H:%M:%SZ"` \
		.
# =================================================================
# Run app
run:
	docker run -e FLASK_APP=sonic -p 5001:5000 thefueley/sonic:$(VERSION)