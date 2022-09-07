"""Environment variable server.

This module provides a secret server using environment variables
This is helpful for local testing and very simple operation.
"""

import typing
import logging
import os
import re

from ox_secrets.core import common


class EnvVarSecretServer(common.SecretServer):
    """Class to handle getting secrets from env variables.

Most of the other secret servers will check the environment for
a secret first by default. This class is mainly useful if
you *ONLY* want to get secrets from the environment variables.

The following illustrates example usage:

>>> import os
>>> os.environ['OX_SECRETS_SOMECATEGORY_EXAMPLE_NAME'] = 'example_1'
>>> os.environ['OX_SECRETS_WEB_EXAMPLE_URL'] = 'https://localhost/foo'
>>> from ox_secrets.core.evs import EnvVarSecretServer as secrets
>>> secrets.clear_cache()  # Clear it to make sure we start fresh
>>> secrets.get_secret('EXAMPLE_NAME', category='SOMECATEGORY')
'example_1'
>>> secrets.get_secret('EXAMPLE_URL', category='WEB')
'https://localhost/foo'
    """

    @classmethod
    def load_secrets_data(cls, prefix: str = 'OX_SECRETS'):
        """Load secrets file from environment variables.

        :param prefix='OX_SECRETS':  Prefix for environment variables to
                                     intrepret as secrets. Anything of
                                     the form {prefix}_{category}_{name} will
                                     be stored.

        ~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

        PURPOSE:  Fill cls._cache with data from secrets vars.

        """
        logging.warning(
            'Reading secrets from env variables with prefix "%s"', prefix)
        my_re = re.compile(f'^{prefix}_(?P<category>[^_]+)_(?P<secname>.+)$')
        for var_name, value in os.environ.items():
            match = my_re.match(var_name)
            if match:
                category = match.group('category')
                secname = match.group('secname')
                logging.info('Matched %s as %s in category %s', secname,
                             category, secname)
                if category not in cls._cache:
                    cls._cache[category] = {}
                cls._cache[category][secname] = value

    @classmethod
    def load_cache(cls, name: typing.Optional[str] = None,
                   category: typing.Optional[str] = None,
                   loader_params: typing.Optional[dict] = None):
        "Implement loading cache from a file."
        if loader_params:
            logging.warning('Ignoring loader_params in %s', cls.__name__)
        with cls._lock:
            return cls.load_secrets_data()

    @classmethod
    def store_secrets(cls, new_secret_dict: typing.Dict[str, str],
                      category: str, **storage_params):
        """Implement as required by parent class.
        """
        return cls.store_secrets_to_env(
            new_secret_dict, category, **storage_params)

    @classmethod
    def store_secrets_to_env(cls, new_secret_dict: typing.Dict[str, str],
                             category: str, prefix: str = 'OX_SECRETS'):
        """Store secrets in environment variables.

        :param new_secret_dict:  Dictionary of secrets to store.

        :param category:str:     Category for storing secrets in env.

        :param prefix='OX_SECRETS':  Prefix for environment variables to
                                     intrepret as secrets. Anything of
                                     the form {prefix}_{category}_{name} will
                                     be stored.

        ~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

        PURPOSE:  Store secrets in environment variables.  This is mainly
                  only useful for testing since the secrets are effectively
                  only stored in memory and get forgotten once the process
                  exits.
        """
        if new_secret_dict:
            logging.warning(
                'Storing to env will be forgotten when pricess exits.')
        with cls._lock:
            if category not in cls._cache:
                cls._cache[category] = {}
            for name, value in new_secret_dict.items():
                full_name = f'{prefix}_{category.upper()}_{name.upper()}'
                os.environ[full_name] = value
                cls._cache[category][name] = value
