"""Common framework for all secret servers.

This module provides a common core for secret servers.
"""

import logging
import os
import threading
import typing
import re

from ox_secrets import settings


class SecretServer:
    """Class to handle gettting secrets.
    """

    _env_var_prefix = 'OX_SECRETS'
    _lock = threading.Lock()  # Used to lock access to _cache
    _cache = {}
    _data_fields = (
        ('name', 'Name of the secret.'),
        ('category', 'Category the secret is in.'),
        ('value', 'String value of the secret'),
        ('notes', 'Optional notes about the secret.')
        )

    @classmethod
    def load_cache(cls, name: typing.Optional[str] = None,
                   category: typing.Optional[str] = None,
                   loader_params: typing.Optional[dict] = None):
        """Load secrets and cache them from back-end store.

        :param name:  String name of secret desired. Some back-ends can load
                      the cache for all secrets at once while others require
                      the name and/or category. You should be able to pass
                      None for name to indicate loading everything for
                      the given category.

        :param category:  String name of secret desired. Some back-ends can
                          load the cache for all secrets at once while others
                          require the name and/or category.


        ~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

        PURPOSE:  Fill cls._cache with data from secrets store.
                  Sub-classes must implement.

        *IMPORTANT:  Sub-classes should use `with cls._lock` inside when
                     overriding load_cache to be thread safe.
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
                   allow_update: bool = True,
                   loader_params: typing.Optional[dict] = None,
                   service_name: typing.Optional[str] = None):
        """Lookup secret with given name and return it.

        :param name:     String name of secret to lookup.

        :param category='root':  Optional string category for secret

        :param allow_env=True:  Whether to allow checking env var first.

        :param allow_update=True:  Whether to loading cache if secret not
                                   found.

        :param loader_params: Optional dict of parameters which gets
                              passed to load_cache for back-end. This allows
                              a way to pass back-end specific info if desired.

        :param service_name: Optional string to add as
                             loader_params['service_name']. The
                             service_name is used by the AWS secret manager
                             and parameter store and nice to be able to
                             specify directly.

        ~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

        :return:   Value of secret.

        ~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

        PURPOSE:   Simple way to lookup secrets.

        """
        category = cls.maybe_replace_category(category)
        result = cls.secret_from_env(name, category, allow_env)
        if result is not None:
            return result
        with cls._lock:
            cdict = cls._cache.get(category, {})
            if name in cdict:
                return cdict[name]
            # Secret not found so clear cache to rebuild
            cls._cache[category] = None
            del cls._cache[category]
        cls._prepare_secrets_dict(category, allow_update,
                                  loader_params, service_name)

        with cls._lock:  # must lock since cdict may refernce cls._cdict
            cdict = cls._cache[category]
            return cdict[name]

    @classmethod
    def get_secret_dict(cls, category: str = 'root',
                        allow_update: bool = True,
                        loader_params: typing.Optional[dict] = None,
                        service_name: typing.Optional[str] = None):
        """Lookup secret with given name and return it.

        :param category='root':  Optional string category for secret

        :param allow_update=True:  Whether to loading cache if secret not
                                   found.

        :param loader_params: Optional dict of parameters which gets
                              passed to load_cache for back-end. This allows
                              a way to pass back-end specific info if desired.

        :param service_name: Optional string to add as
                             loader_params['service_name']. The service_name
                              is used by the AWS secret manager and parameter
                             store and nice to be able to specify directly.

        ~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

        :return:   Value of secret.

        ~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

        PURPOSE:   Simple way to lookup secrets.

        """
        category = cls.maybe_replace_category(category)
        cls._prepare_secrets_dict(category, allow_update, loader_params,
                                  service_name)
        with cls._lock:
            return dict(cls._cache[category])  # return shallow copy

    @classmethod
    def _prepare_secrets_dict(
            cls, category: str, allow_update: bool,
            loader_params: typing.Optional[dict] = None,
            service_name: typing.Optional[str] = None):
        """Help prepare secrets in cls._cache for get_secret and get_secret.

        :param category:  String category for secrets.

        :param allow_update=True:  Whether to loading cache if secret not
                                   found.

        :param loader_params: Optional dict of parameters which gets
                              passed to load_cache for back-end. This allows
                              a way to pass back-end specific info if desired.

        :param service_name: Optional string to add as
                             loader_params['service_name']. The service_name
                              is used by the AWS secret manager and parameter
                             store and nice to be able to specify directly.

        ~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

        PURPOSE:   This is a helper function to only be called by
                   get_secret and get_secret_dict. If cls._cache[category]
                   is non-empty, then this does nothign since we assume
                   we already have secrets loaded

        """

        if cls._cache.get(category):  # have something so no need to reload
            return
        if not allow_update:
            with cls._lock:
                cdict = cls._cache.get(category, None)
                if cdict is not None:   # did have something there
                    return              # so stop processing
                logging.error(          # otherwise indicate an error
                    'Unable to find category %s for secret manager class %s',
                    category, cls.__name__)
                raise KeyError(category)  # no data and no update allowed
        if service_name is not None:
            if loader_params is None:
                loader_params = {}
            loader_params['service_name'] = service_name
        cls.load_cache(name=None, category=category,
                       loader_params=loader_params)

    @staticmethod
    def maybe_replace_category(category):
        """Replace input based on OX_SECRETS_CATEGORY_REGEXP.

Meant to be called by get_secret.
        """
        if settings.OX_SECRETS_CATEGORY_REGEXP:
            return re.sub(settings.OX_SECRETS_CATEGORY_REGEXP,
                          settings.OX_SECRETS_CATEGORY_REPLACE, category)
        return category

    @classmethod
    def list_secret_names(cls, category: str) -> typing.List[str]:
        "Return list of secret names for given category."

        with cls._lock:  # get the lock to prevent modification while we look
            cdict = cls._cache.get(category, [])
            return list(cdict)

    @classmethod
    def store_secrets(cls, new_secret_dict: typing.Dict[str, str],
                      category: str, **storage_params):
        """Store secrets to back-end

        :param new_secret_dict:  Dictionary or name value pairs for secrets.

        :param category:  String category for secrets to store.

        :param **storage_params:   Optional storage parameters for back-end.
        ~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

        PURPOSE:  Store the secrets in new_secret_dict.

        """
        raise NotImplementedError


class SecretInfo:
    """Class to hold information about a secret and convert to/from string.

The SecretInfo class is useful as a way to hold information about a
secret in a way which can be serialized to/from a string.

The following illustrates example usage:

>>> import tempfile, os                  # first do some boilerplate
>>> from ox_secrets.core import common   # imports of various things
>>> from ox_secrets import server
>>> tfile = tempfile.mktemp(suffix='.csv')  # setup a temp file
>>> open(tfile, 'wb').write(                # and write example secrets
... '''name,category,value,notes            # with an ususual encoding
... cool,thing,here,example'''.encode('UTF-32'))
352
>>> sstr = (  # create a secret serialized as a string
...   f'name=cool:category=thing:mode=fss:filename={tfile}:encoding=utf32')
>>> sec = common.SecretInfo.from_str(sstr)  # parse the string
>>> sec  # show pretty representation  doctest: +ELLPISIS
SecretInfo(name='cool',
  category='thing',
  mode='fss',
  filename='....csv',
  encoding='utf32')
>>> sstr == str(sec)  # verify we can convert back to string
True
>>> server.get_server(mode=sec.mode).get_secret(  # read secret
...     name=sec.name, category=sec.category, loader_params=sec.loader_params)
'here'
>>> os.remove(tfile)  # remove temp file

    """

    def __init__(self, name, category, mode=None, **kwargs):
        self.name = name
        self.category = category
        self.mode = mode
        self.loader_params = kwargs

    @classmethod
    def from_str(cls, my_str):
        """Convert a string representation of the secret to this class.

        :param my_str:   String representation of a secret.

        ~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

        :return:  Instance of class

        """
        kwargs = {}
        data = my_str.split(':')
        for item in data:
            key, value = item.split('=')
            kwargs[key.strip()] = value.strip()
        result = cls(**kwargs)
        return result

    def make_info(self):
        """Return list of name value pairs for data in self.
        """
        info = [('name', self.name), ('category', self.category)]
        if self.mode is not None:
            info.append(('mode', self.mode))
        for name, value in self.loader_params.items():
            info.append((name, value))
        return info

    def pretty(self):
        "Return pretty string reprsentation."
        info = self.make_info()
        arg_info = ",\n  ".join([f'{k}={repr(v)}' for k, v in info])
        return self.__class__.__name__ + f'({arg_info})'

    def __str__(self):
        info = self.make_info()
        return ':'.join([f'{k}={v}' for k, v in info])

    def __repr__(self):
        return self.pretty()
