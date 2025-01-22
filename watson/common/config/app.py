from . import config as _config

connector_api_base_url = _config("CONNECTOR_API_BASE_URL", default='/api/virtual-assistant/v1')
connector_api_port = _config("CONNECTOR_API_PORT", default=5000)

watson_api_url = _config("WATSON_API_URL", default=None)
watson_api_key = _config("WATSON_API_KEY", default=None)
watson_env_id = _config("WATSON_ENV_ID", default=None)
watson_env_version = _config("WATSON_ENV_VERSION", default='2024-08-25')  # Needs updating if watson releases breaking change. See: https://cloud.ibm.com/apidocs/assistant-v2?code=python#versioning
