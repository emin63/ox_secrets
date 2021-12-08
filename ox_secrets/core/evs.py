"""Environment variable server.

This module provides a secret server using environment variables
This is helpful for local testing and very simple operation.
"""


import logging
import os
import re

from ox_secrets.core import common


class EnvVarSecretServer(common.SecretServer):
    """Class to handle getting secrets from env variables.

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
    def load_cache(cls):
        "Implement loading cache from a file."
        return cls.load_secrets_data()
