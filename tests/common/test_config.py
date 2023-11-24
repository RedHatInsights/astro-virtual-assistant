import builtins
import sys
import os
from unittest import mock
import importlib

import pytest
from decouple import UndefinedValueError


__config_modules = [
    "app_common_python",
    "common.config",
    "common.config.app",
]


def import_app_config():
    for module in __config_modules:
        importlib.import_module(module)


def clear_app_config():
    for module in __config_modules:
        if module in sys.modules:
            del sys.modules[module]


@mock.patch.dict(
    os.environ,
    {
        "ACG_CONFIG": "./tests/resources/clowdapp.json",
        "__DOT_ENV_FILE": ".i-dont-exist",
    },
    clear=True,
)
def test_clowdapp():
    try:
        import_app_config()
        from common.config import app

        assert app.is_running_locally is False

        assert app.advisor_url == "http://n-api.svc:8000"
        assert app.notifications_url == "http://n-gw.svc:1337"
        assert app.vulnerability_url == "http://v-engine.svc:1234"

        assert app.database_host == "some.host"
        assert app.database_port == 15432
        assert app.database_user == "aUser"
        assert app.database_password == "secret"
        assert app.database_name == "some-db"
        assert app.database_ssl_mode == "require"

        assert app.lock_store_type == "in_memory"

        assert app.namespace is None
    finally:
        clear_app_config()


@mock.patch.dict(
    os.environ,
    {
        "ACG_CONFIG": "./tests/resources/clowdapp-missing-vulnerability-endpoint.json",
        "__DOT_ENV_FILE": ".i-dont-exist",
    },
    clear=True,
)
def test_clowdapp_missing_required_endpoint():
    try:
        with pytest.raises(UndefinedValueError):
            import_app_config()
            from common.config import app
    finally:
        clear_app_config()


@mock.patch.dict(
    os.environ,
    {"IS_RUNNING_LOCALLY": "1", "__DOT_ENV_FILE": ".i-dont-exist"},
    clear=True,
)
def test_loads_file_when_running_locally():
    try:
        import_app_config()
        from common.config import app

        assert app.is_running_locally is True

        assert app.console_dot_base_url == "https://console.redhat.com"

        assert app.advisor_url == app.console_dot_base_url
        assert app.notifications_url == app.console_dot_base_url
        assert app.vulnerability_url == app.console_dot_base_url

        assert app.database_host is None
        assert app.database_port == 0
        assert app.database_user is None
        assert app.database_password is None
        assert app.database_name is None
        assert app.database_ssl_mode is None

        assert app.lock_store_type == "in_memory"
        assert app.namespace is None
    finally:
        clear_app_config()


@mock.patch.dict(
    os.environ,
    {"IS_RUNNING_LOCALLY": "1", "__DOT_ENV_FILE": ".i-dont-exist"},
    clear=True,
)
def test_loads_namespace():
    def openshift_mock_open(*args, **kwargs):
        if args[0] == "/var/run/secrets/kubernetes.io/serviceaccount/namespace":
            return mock.mock_open(read_data="my-cool-namespace")(*args, **kwargs)

        return builtins.open(*args, **kwargs)

    with mock.patch("builtins.open", openshift_mock_open):
        try:
            import_app_config()
            from common.config import app

            assert app.namespace == "my-cool-namespace"
        finally:
            clear_app_config()
