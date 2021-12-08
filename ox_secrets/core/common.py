"""Common framework for all secret servers.

This module provides a common core for secret servers.
"""


import logging
import os
import threading


class SecretServer:
    """Class to handle gettting secrets.
    """

    _lock = threading.Lock()  # Used to lock access to _cache
    _cache = {}

    @classmethod
    def load_cache(cls):
        """Load secrets and cache them from back-end store.

        ~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

        PURPOSE:  Fill cls._cache with data from secrets store.
                  Sub-classes must implement.

        """
        raise NotImplementedError

    @classmethod
    def clear_cache(cls):
        "Clear the cache (i.e., forget all secrets)."
        cls._cache = {}

    @classmethod
    def get_secret(cls, name, category='root'):
        """Lookup secret with given name and return it.

        :param name:     String name of secret to lookup.

        :param category=None:  Optional string category for secret

        ~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

        :return:   Value of secret.

        ~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

        PURPOSE:   Simple way to lookup secrets.

        """
        key = '%s/%s' % (category if category is not None else '', name)
        result = os.environ.get(key, None)
        if result is not None:
            logging.info('Secret extracted from env var "%s"', key)
            return result
        if not cls._cache:
            cls.load_cache()
        with cls._lock:  # get the lock since we are going to modify cache
            cdict = cls._cache.get(category, {})
            result = cdict[name]

        return result
