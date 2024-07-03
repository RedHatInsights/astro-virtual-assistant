#!/bin/bash

set -exv

IMAGE_API="quay.io/cloudservices/virtual-assistant-api"
IMAGE_ACTIONS="quay.io/cloudservices/virtual-assistant-actions"
IMAGE_INTERNAL="quay.io/cloudservices/virtual-assistant-internal"
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

# Create tmp dir to store data in during job run (do NOT store in $WORKSPACE)
TMP_JOB_DIR=$(mktemp -d -p "$HOME" -t "jenkins-${JOB_NAME}-${BUILD_NUMBER}-XXXXXX")
export TMP_JOB_DIR
echo "job tmp dir location: $TMP_JOB_DIR"

function job_cleanup() {
    echo "cleaning up job tmp dir: $TMP_JOB_DIR"
    rm -fr $TMP_JOB_DIR
}

trap job_cleanup EXIT ERR SIGINT SIGTERM

DOCKER_CONF="$TMP_JOB_DIR/.docker"
mkdir -p "$DOCKER_CONF"

docker --config="$DOCKER_CONF" login -u="$QUAY_USER" -p="$QUAY_TOKEN" quay.io
docker --config="$DOCKER_CONF" login -u="$RH_REGISTRY_USER" -p="$RH_REGISTRY_TOKEN" registry.redhat.io

docker --config="$DOCKER_CONF" build --pull --build-arg BUILD_COMMIT=${BUILD_COMMIT} -f docker/Dockerfile.astro-virtual-assistant-rasa -t "${IMAGE_API}:${IMAGE_TAG}" .
docker --config="$DOCKER_CONF" tag "${IMAGE_API}:${IMAGE_TAG}" "${IMAGE_API}:latest"
docker --config="$DOCKER_CONF" push "${IMAGE_API}:${IMAGE_TAG}"
docker --config="$DOCKER_CONF" push "${IMAGE_API}:latest"

docker --config="$DOCKER_CONF" build --pull --build-arg BUILD_COMMIT=${BUILD_COMMIT} -f docker/Dockerfile.astro-virtual-assistant-rasa-actions -t "${IMAGE_ACTIONS}:${IMAGE_TAG}" .
docker --config="$DOCKER_CONF" tag "${IMAGE_ACTIONS}:${IMAGE_TAG}" "${IMAGE_ACTIONS}:latest"
docker --config="$DOCKER_CONF" push "${IMAGE_ACTIONS}:${IMAGE_TAG}"
docker --config="$DOCKER_CONF" push "${IMAGE_ACTIONS}:latest"

docker --config="$DOCKER_CONF" build --pull --no-cache --build-arg BUILD_COMMIT=${BUILD_COMMIT} -f docker/Dockerfile.astro-virtual-assistant-internal -t "${IMAGE_INTERNAL}:${IMAGE_TAG}" .
docker --config="$DOCKER_CONF" tag "${IMAGE_INTERNAL}:${IMAGE_TAG}" "${IMAGE_INTERNAL}:latest"
docker --config="$DOCKER_CONF" push "${IMAGE_INTERNAL}:${IMAGE_TAG}"
docker --config="$DOCKER_CONF" push "${IMAGE_INTERNAL}:latest"
