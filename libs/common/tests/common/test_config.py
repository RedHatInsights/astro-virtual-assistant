import os
from unittest import mock
import sys
from unittest.mock import MagicMock

from .. import path_to_resource
import pytest
from decouple import UndefinedValueError

__config_modules = [
    "app_common_python",
    "common.config",
]


@pytest.fixture(autouse=True)
def clear_app_config():
    for module in __config_modules:
        if module in sys.modules:
            del sys.modules[module]


@mock.patch.dict(
    os.environ,
    {
        "ACG_CONFIG": path_to_resource("clowdapp.json"),
        "__DOT_ENV_FILE": ".i-dont-exist",
    },
    clear=True,
)
def test_clowdapp_public_endpoints():
    from common.config import config

    assert config("ENDPOINT__ADVISOR_BACKEND__API__URL") == "http://n-api.svc:8000"
    assert config("ENDPOINT__NOTIFICATIONS_GW__SERVICE__URL") == "http://n-gw.svc:1337"


@mock.patch.dict(
    os.environ,
    {
        "ACG_CONFIG": path_to_resource("clowdapp.json"),
        "__DOT_ENV_FILE": ".i-dont-exist",
    },
    clear=True,
)
def test_clowdapp_public_endpoints_not_found():
    from common.config import config

    with pytest.raises(UndefinedValueError):
        assert config("ENDPOINT__ADVISOR_BACKEND__COOL__URL") == "http://n-api.svc:8000"


@mock.patch.dict(
    os.environ,
    {
        "ACG_CONFIG": path_to_resource("clowdapp.json"),
        "__DOT_ENV_FILE": ".i-dont-exist",
    },
    clear=True,
)
def test_clowdapp_public_endpoints_invalid():
    from common.config import config

    with pytest.raises(ValueError):
        assert config("ENDPOINT__ADVISOR_BACKEND__API__PORT") == "http://n-api.svc:8000"


@mock.patch.dict(
    os.environ,
    {
        "ACG_CONFIG": path_to_resource("clowdapp.json"),
        "__DOT_ENV_FILE": ".i-dont-exist",
    },
    clear=True,
)
def test_clowdapp_private_endpoints():
    from common.config import config

    assert (
        config("PRIVATE_ENDPOINT__VIRTUAL_ASSISTANT__ACTIONS__URL")
        == "http://my-virtual-assistant-actions:10000"
    )


@mock.patch.dict(
    os.environ,
    {
        "ACG_CONFIG": path_to_resource("clowdapp.json"),
        "__DOT_ENV_FILE": ".i-dont-exist",
    },
    clear=True,
)
def test_database():
    from common.config import config

    assert config("DB_ADMIN_PASSWORD") == "s3cr3t"
    assert config("DB_ADMIN_USERNAME") == "postgres"
    assert config("DB_HOSTNAME") == "some.host"
    assert config("DB_NAME") == "some-db"
    assert config("DB_PASSWORD") == "secret"
    assert config("DB_PORT") == 15432
    assert config("DB_SSL_MODE") == "require"
    assert config("DB_USERNAME") == "aUser"

    with pytest.raises(UndefinedValueError):
        assert config("DB_CA_PATH") is None


@mock.patch.dict(
    os.environ,
    {
        "ACG_CONFIG": path_to_resource("clowdapp.json"),
        "__DOT_ENV_FILE": ".i-dont-exist",
    },
    clear=True,
)
def test_logging():
    from common.config import config

    assert config("LOGGING_CLOUDWATCH_ACCESS_KEY_ID") == "my-key-id"
    assert config("LOGGING_CLOUDWATCH_SECRET_ACCESS_KEY") == "very-secret"
    assert config("LOGGING_CLOUDWATCH_REGION") == "eu-central-1"
    assert config("LOGGING_CLOUDWATCH_LOG_GROUP") == "my-log-group"


@mock.patch.dict(
    os.environ,
    {
        "ACG_CONFIG": path_to_resource("clowdapp.json"),
        "__DOT_ENV_FILE": ".i-dont-exist",
    },
    clear=True,
)
def test_redis():
    from common.config import config

    assert config("REDIS_HOSTNAME") == "my-hostname"
    assert config("REDIS_PORT") == 99137
    assert config("REDIS_USERNAME") == "my-username"
    assert config("REDIS_PASSWORD") == "my-s3cret"
    with pytest.raises(ValueError):
        config("REDIS_DOMINATION_PLANS")


@mock.patch.dict(
    os.environ,
    {
        "ACG_CONFIG": path_to_resource("clowdapp.json"),
        "__DOT_ENV_FILE": ".i-dont-exist",
    },
    clear=True,
)
def test_other_params():
    from common.config import config

    assert config("METRICS_PATH") == "/metrics"
    assert config("METRICS_PORT") == 9000
    assert config("PRIVATE_PORT") == 10000
    assert config("PUBLIC_PORT") == 8000
    assert config("WEB_PORT") == 8000


@mock.patch.dict(
    os.environ,
    {
        "ACG_CONFIG": path_to_resource("clowdapp-with-db-ca.json"),
        "__DOT_ENV_FILE": ".i-dont-exist",
    },
    clear=True,
)
def test_with_db_ca():
    def get_contents_of_file(path: str):
        buff = []
        with open(path, "r") as f:
            for line in f:
                buff.append(line)

        return "".join(buff)

    from common.config import config

    assert config("DB_USERNAME") == "aUser"
    assert get_contents_of_file(config("DB_CA_PATH")) == "some-stuff-in-here"


@mock.patch.dict(
    os.environ,
    {"IS_RUNNING_LOCALLY": "1", "__DOT_ENV_FILE": ".i-dont-exist"},
    clear=True,
)
def test_openshift_namespace():
    with mock.patch(
        "builtins.open",
        MagicMock(return_value=mock.mock_open(read_data="my-cool-namespace"))(),
    ) as mocked_open:
        from common.config import config

        assert config("NAMESPACE") == "my-cool-namespace"
        mocked_open.assert_called_once_with(
            "/var/run/secrets/kubernetes.io/serviceaccount/namespace", "r"
        )


def test_openshift_namespace_has_cache():
    with mock.patch(
        "builtins.open",
        MagicMock(return_value=mock.mock_open(read_data="my-cool-namespace"))(),
    ) as mocked_open:
        from common.config import config

        assert config("NAMESPACE") == "my-cool-namespace"
        assert config("NAMESPACE") == "my-cool-namespace"
        assert config("NAMESPACE") == "my-cool-namespace"
        mocked_open.assert_called_once_with(
            "/var/run/secrets/kubernetes.io/serviceaccount/namespace", "r"
        )


@mock.patch.dict(
    os.environ,
    {"__DOT_ENV_FILE": ".i-dont-exist", "I_AM_AN_ENV_VARIABLE": "yes"},
    clear=True,
)
def test_defaults_to_env():
    from common.config import config

    assert config("I_AM_AN_ENV_VARIABLE") == "yes"


@mock.patch.dict(
    os.environ,
    {
        "ONE": "1",
        "TWO": "two",
        "true": "true",
    },
)
def test_logger():
    from common.config import config, log_config

    mlogger = MagicMock()

    def module(): ...

    module.__dict__ = {
        "one": config("ONE"),
        "__private_one": config("ONE"),
        "oneToken": config("ONE"),
        "onePasswordStuff": config("ONE"),
        "oneKeyEtc": config("ONE"),
        "secretOfMonkeyIsland": config("ONE"),
        "two": config("TWO"),
        "myBool": config("true"),
    }

    with mock.patch("logging.getLogger", lambda _: mlogger):
        log_config(module)
        assert mlogger.info.call_count == 7
        mlogger.info.assert_any_call("Using one: 1")
        mlogger.info.assert_any_call("Using oneToken: *********")
        mlogger.info.assert_any_call("Using onePasswordStuff: *********")
        mlogger.info.assert_any_call("Using oneKeyEtc: *********")
        mlogger.info.assert_any_call("Using secretOfMonkeyIsland: *********")
        mlogger.info.assert_any_call("Using two: two")
        mlogger.info.assert_any_call("Using myBool: true")
