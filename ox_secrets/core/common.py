"""Common framework for all secret servers.

This module provides a common core for secret servers.
"""


import logging
import os
import threading


class SecretServer:
    """Class to handle gettting secrets.
    """

    _env_var_prefix = 'OX_SECRETS'
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
    def make_env_var_key(cls, name: str, category: str):
        """Create key to lookup environment variable for given name/category.
        """

        key = f'{cls._env_var_prefix}_{category}_{name}'.upper()
        return key

    @classmethod
    def secret_from_env(cls, name: str, category: str, allow_env: bool):
        """Try to extract secret from environment variable.

        :param name:  String name of secret.

        :param category:  String category.

        :param allow_env:  If False, return None.
        """
        if not allow_env:
            logging.debug('allow_env is false so not checking env')
            return None
        key = cls.make_env_var_key(name, category)
        result = os.environ.get(key, None)
        if result is not None:
            logging.info('Secret extracted from env var "%s"', key)
        return result

    @classmethod
    def get_secret(cls, name, category='root', allow_env=True):
        """Lookup secret with given name and return it.

        :param name:     String name of secret to lookup.

        :param category=None:  Optional string category for secret

        ~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

        :return:   Value of secret.

        ~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

        PURPOSE:   Simple way to lookup secrets.

        """
        result = cls.secret_from_env(name, category, allow_env)
        if result is not None:
            return result
        if not cls._cache:
            cls.load_cache()
        with cls._lock:  # get the lock since we are going to modify cache
            cdict = cls._cache.get(category, {})
            result = cdict[name]

        return result
