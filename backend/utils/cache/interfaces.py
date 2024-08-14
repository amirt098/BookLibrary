import abc


class AbstractCache(abc.ABC):

    def set(self, cache_key: str, value, timeout=None):
        raise NotImplementedError

    def get(self, cache_key, default=None):
        raise NotImplementedError

    def delete(self, cache_key):
        raise NotImplementedError
