"""Common framework for all secret servers.

This module provides a common core for secret servers.
"""


import logging
import os
import threading
import typing


class SecretServer:
    """Class to handle gettting secrets.
    """

    _env_var_prefix = 'OX_SECRETS'
    _lock = threading.Lock()  # Used to lock access to _cache
    _cache = {}

    @classmethod
    def load_cache(cls, name: typing.Optional[str] = None,
                   category: typing.Optional[str] = None,
                   loader_params: typing.Optional[dict] = None):
        """Load secrets and cache them from back-end store.

        :param name:  String name of secret desired. Some back-ends can load
                      the cache for all secrets at once while others require
                      the name and/or category.

        :param category:  String name of secret desired. Some back-ends can
                          load the cache for all secrets at once while others 
                          require the name and/or category.


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
    def get_secret(cls, name: str, category: str = 'root',
                   allow_env: bool = True,
                   loader_params: typing.Optional[dict] = None) -> str:
        """Lookup secret with given name and return it.

        :param name:     String name of secret to lookup.

        :param category='root:  Optional string category for secret

        :param loader_params: Optional dict of parameters which gets
                              passed to load_cache for back-end. This allows
                              a way to pass back-end specific info if desired.

        ~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

        :return:   Value of secret.

        ~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

        PURPOSE:   Simple way to lookup secrets.

        """
        result = cls.secret_from_env(name, category, allow_env)
        if result is not None:
            return result
        if not cls._cache:
            cls.load_cache(name=name, category=category,
                           loader_params=loader_params)
        with cls._lock:  # get the lock since we are going to modify cache
            cdict = cls._cache.get(category, {})
            result = cdict[name]

        return result

    @classmethod
    def list_secret_names(cls, category: str) -> typing.List[str]:
        "Return list of secret names for given category."

        with cls._lock:  # get the lock to prevent modification while we look
            cdict = cls._cache.get(category, [])
            return list(cdict)
