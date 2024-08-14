import logging
from django.core.cache import cache as django_cache
from . import interfaces

logger = logging.getLogger(__name__)


class DjangoCacheProxy(interfaces.AbstractCache):
    def get(self, cache_key, default=None):
        logger.info(f"cache key:{cache_key},default:{default}")
        result = django_cache.get(cache_key)
        if result is None:
            result = default
        logger.info(f"result:{result}")
        return result

    def set(self, cache_key: str, value, timeout=None):
        logger.info(f"cache key:{cache_key},value:{value},timeout:{timeout}")
        django_cache.set(cache_key, value, timeout=timeout)

    def delete(self, cache_key: str):
        logger.info(f"cache key:{cache_key}")
        django_cache.delete(cache_key)

