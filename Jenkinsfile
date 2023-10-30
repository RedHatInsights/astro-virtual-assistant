def secrets = [
    [path: params.VAULT_PATH_SVC_ACCOUNT_EPHEMERAL, engineVersion: 1, secretValues: [
        [envVar: 'OC_LOGIN_TOKEN_DEV', vaultKey: 'oc-login-token-dev'],
        [envVar: 'OC_LOGIN_SERVER_DEV', vaultKey: 'oc-login-server-dev']]],
    [path: params.VAULT_PATH_QUAY_PUSH, engineVersion: 1, secretValues: [
        [envVar: 'QUAY_USER', vaultKey: 'user'],
        [envVar: 'QUAY_TOKEN', vaultKey: 'token']]],
    [path: params.VAULT_PATH_RHR_PULL, engineVersion: 1, secretValues: [
        [envVar: 'RH_REGISTRY_USER', vaultKey: 'user'],
        [envVar: 'RH_REGISTRY_TOKEN', vaultKey: 'token']]]
]

def configuration = [vaultUrl: params.VAULT_ADDRESS, vaultCredentialId: params.VAULT_CREDS_ID, engineVersion: 1]

pipeline {
    agent { label 'insights' }
    options {
        timestamps()
    }
    environment {
        APP_NAME="virtual-assistant"  // name of app-sre "application" folder this component lives in
        COMPONENT_NAME="virtual-assistant-api"  // name of app-sre "resourceTemplate" in deploy.yaml for this component
        API_COMPONENT_NAME="virtual-assistant-api"  // name of app-sre "resourceTemplate" in deploy.yaml for this component
        ACTIONS_COMPONENT_NAME="virtual-assistant-actions"  // name of app-sre "resourceTemplate" in deploy.yaml for this component
        IMAGE="quay.io/cloudservices/virtual-assistant-api"
        DOCKERFILE="docker/Dockerfile.astro-virtual-assistant-rasa"

        IQE_PLUGINS="virtual-assistant"
        IQE_MARKER_EXPRESSION="smoke"
        IQE_FILTER_EXPRESSION=""
        IQE_CJI_TIMEOUT="30m"

        // Install bonfire repo/initialize
        CICD_URL="https://raw.githubusercontent.com/RedHatInsights/bonfire/master/cicd"
    }
    stages {
        stage('Pipeline') {
            steps {
                sh 'mkdir -p artifacts'
            }
        }
    }
}