from . import config as _config

offline_refresh_token = _config("OFFLINE_REFRESH_TOKEN", default=None)
sso_refresh_token_url = _config("SSO_REFRESH_TOKEN_URL", default="https://sso.redhat.com/auth/realms/redhat-external/protocol/openid-connect/token")

