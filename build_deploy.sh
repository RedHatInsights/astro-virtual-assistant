#!/bin/bash

set -exv

IMAGE_API="quay.io/cloudservices/virtual-assistant-api"
IMAGE_ACTIONS="quay.io/cloudservices/virtual-assistant-actions"
IMAGE_TAG=$(git rev-parse --short=7 HEAD)
BUILD_COMMIT=$(git rev-parse HEAD)

if [[ -z "$QUAY_USER" || -z "$QUAY_TOKEN" ]]; then
    echo "QUAY_USER and QUAY_TOKEN must be set"
    exit 1
fi

if [[ -z "$RH_REGISTRY_USER" || -z "$RH_REGISTRY_TOKEN" ]]; then
    echo "RH_REGISTRY_USER and RH_REGISTRY_TOKEN  must be set"
    exit 1
fi

DOCKER_CONF="$PWD/.docker"
mkdir -p "$DOCKER_CONF"

docker --config="$DOCKER_CONF" login -u="$QUAY_USER" -p="$QUAY_TOKEN" quay.io
docker --config="$DOCKER_CONF" login -u="$RH_REGISTRY_USER" -p="$RH_REGISTRY_TOKEN" registry.redhat.io

docker --config="$DOCKER_CONF" build --build-arg BUILD_COMMIT=${BUILD_COMMIT} -f docker/Dockerfile.astro-virtual-assistant-rasa -t "${IMAGE_API}:${IMAGE_TAG}" .
docker --config="$DOCKER_CONF" tag "${IMAGE_API}:${IMAGE_TAG}" "${IMAGE_API}:latest"
docker --config="$DOCKER_CONF" push "${IMAGE_API}:${IMAGE_TAG}"
docker --config="$DOCKER_CONF" push "${IMAGE_API}:latest"

docker --config="$DOCKER_CONF" build --build-arg BUILD_COMMIT=${BUILD_COMMIT} -f docker/Dockerfile.astro-virtual-assistant-rasa-actions -t "${IMAGE_ACTIONS}:${IMAGE_TAG}" .
docker --config="$DOCKER_CONF" tag "${IMAGE_ACTIONS}:${IMAGE_TAG}" "${IMAGE_ACTIONS}:latest"
docker --config="$DOCKER_CONF" push "${IMAGE_ACTIONS}:${IMAGE_TAG}"
docker --config="$DOCKER_CONF" push "${IMAGE_ACTIONS}:latest"
