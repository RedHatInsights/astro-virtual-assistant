from pipeline.dummy_graph_component import DummyGraphComponent
import logging


logger = logging.getLogger(__name__)


def allow_disable(real_class):
    """
    This is a dirty  hack to decide if we want to disable this component without actually
    updating the config file. It does so by checking an env variable and replacing the
    component with a dummy one.
    """
    import os
    if os.getenv(f"DISABLE_{real_class.__name__.upper()}") is None:
        return real_class

    logger.warning(f"Disabling component: {real_class.__name__}")
    return DummyGraphComponent
