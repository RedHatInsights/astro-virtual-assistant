from decouple import RepositoryEmpty


class RepositoryOpenshift(RepositoryEmpty):
    """
    Retrieves values from openshift
    """

    def __init__(self):
        self.cache = {}

    def __contains__(self, item):
        if item in self.cache:
            return self.cache.get(item) is not None

        if item == "NAMESPACE":
            self.cache[item] = _get_namespace()
            return self.cache[item] is not None

        return False

    def __getitem__(self, item):
        if item in self.cache:
            return self.cache.get(item)

        if item == "NAMESPACE":
            self.cache[item] = _get_namespace()
            return self.cache[item]

        raise KeyError(item)


def _get_namespace():
    try:
        with open("/var/run/secrets/kubernetes.io/serviceaccount/namespace", "r") as f:
            namespace = f.read()
        return namespace
    except EnvironmentError:
        return None
