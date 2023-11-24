import os
from typing import Text

from decouple import RepositoryEmpty


class RepositoryClowdapp(RepositoryEmpty):
    """
    Retrieves option keys from clowdapp

    - Endpoint format is:
        ENDPOINT__${APP_NAME}__${SERVICE_NAME}__${PARAM}
        e.g. ENDPOINT__ADVISOR_BACKEND__API
    - DB format is
        DB_${PROP}
    - REDIS format is
        REDIS_${PROP}
    - Logging cloud watch format is:
        LOGGING_CLOUDWATCH_${PROP}
    - All other properties are:
        ${PROP]

    All the PROPs are converted to camel case by replacing underscores. All except the last will
    fail if the PROP is not found in the object.
    """

    __ENDPOINT_PREFIX = "ENDPOINT__"
    __DATABASE_PREFIX = "DB_"
    __INMEMORY_PREFIX = "REDIS_"
    __LOGGING_PREFIX = "LOGGING_CLOUDWATCH_"

    def __init__(self, config):
        self.config = config

    def __contains__(self, item):
        if self.config is None:
            return False

        return self.__get_item(item) is not None

    def __getitem__(self, item):
        if self.config is None:
            return None

        return self.__get_item(item)

    def __get_item(self, item: Text):
        if os.getenv(item, None) is not None:
            return os.getenv(item)

        if item.startswith(self.__ENDPOINT_PREFIX):
            elements = item.split("__")
            if len(elements) == 4:
                app = _kebab_case(elements[1].lower())
                service = _kebab_case(elements[2].lower())
                what = _kebab_case(elements[3].lower())

                endpoint = self.__get_endpoint(app, service)
                if endpoint is not None:
                    if what == "url":
                        return _get_endpoint_url(endpoint)
                    else:
                        raise ValueError("Invalid configuration %s" % item)
        elif item.startswith(self.__DATABASE_PREFIX):
            return _get_item_with_param(
                self.__DATABASE_PREFIX, item, self.config.database
            )
        elif item.startswith(self.__INMEMORY_PREFIX):
            return _get_item_with_param(
                self.__INMEMORY_PREFIX, item, self.config.inMemoryDb
            )
        elif item.startswith(self.__LOGGING_PREFIX):
            return _get_item_with_param(
                self.__LOGGING_PREFIX, item, self.config.logging.cloudwatch
            )
        else:
            return _get_item_with_param("", item, self.config, fail_if_not_found=False)

        return None

    def __get_endpoint(self, app, service):
        for endpoint in self.config.endpoints:
            if endpoint.app == app and endpoint.name == service:
                return endpoint

        return None


def _get_item_with_param(prefix: Text, item: Text, config, fail_if_not_found=True):
    if config is None:
        return None

    element = item.replace(prefix, "", 1)
    if len(element) > 0:
        what = _camel_case(element)
        if hasattr(config, what):
            return getattr(config, what)
        elif fail_if_not_found:
            raise ValueError(
                "Invalid configuration attribute %s for %s. Valid attributes: %s"
                % (what, item, config.__dict__.keys())
            )

    return None


def _kebab_case(value: Text) -> Text:
    return value.replace("_", "-")


def _camel_case(value: Text) -> Text:
    value = value.replace("_", " ").title().replace(" ", "")
    return value.replace(value[0], value[0].lower(), 1)


def _get_endpoint_url(endpoint):
    return "http://%s:%s" % (endpoint.hostname, endpoint.port)
