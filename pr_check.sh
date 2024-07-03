#!/bin/bash
# --------------------------------------------
# Options that must be configured by app owner
# --------------------------------------------
APP_NAME="virtual-assistant"  # name of app-sre "application" folder this component lives in
API_COMPONENT_NAME="virtual-assistant-api"  # name of app-sre "resourceTemplate" in deploy.yaml for this component
ACTIONS_COMPONENT_NAME="virtual-assistant-actions"  # name of app-sre "resourceTemplate" in deploy.yaml for this component
REF_ENV="insights-stage"

IQE_PLUGINS="virtual-assistant"
IQE_MARKER_EXPRESSION="smoke"
IQE_FILTER_EXPRESSION=""
IQE_CJI_TIMEOUT="30m"

# Install bonfire repository/initialize
CICD_URL=https://raw.githubusercontent.com/RedHatInsights/bonfire/master/cicd
curl -s $CICD_URL/bootstrap.sh > .cicd_bootstrap.sh && source .cicd_bootstrap.sh

# Build Virtual Assistant image based on the latest commit
IMAGE="quay.io/cloudservices/virtual-assistant-api"
DOCKERFILE="docker/Dockerfile.astro-virtual-assistant-rasa"
source $CICD_ROOT/build.sh

# Build and Deploy Virtual Assistant Actions image
IMAGE="quay.io/cloudservices/virtual-assistant-actions"
DOCKERFILE="docker/Dockerfile.astro-virtual-assistant-rasa-actions"
source $CICD_ROOT/build.sh

# Build and Deploy Virtual Assistant Internal image
IMAGE="quay.io/cloudservices/virtual-assistant-internal"
DOCKERFILE="docker/Dockerfile.astro-virtual-assistant-internal"
source $CICD_ROOT/build.sh

# Deploy to an ephemeral environment
source $CICD_ROOT/deploy_ephemeral_env.sh

# Run Virtual Assistant IQE tests
# IQE_PLUGINS="virtual-assistant"
# IQE_MARKER_EXPRESSION="smoke"
# IQE_FILTER_EXPRESSION=""
# IQE_CJI_TIMEOUT="30m"

# source $CICD_ROOT/cji_smoke_test.sh

source $CICD_ROOT/post_test_results.sh
