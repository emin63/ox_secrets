"""High-level file to work with secret servers.
"""

import os
import typing

from ox_secrets import settings
from ox_secrets.core import common, fss, evs


def get_server(mode: typing.Optional[str] = None) -> common.SecretServer:
    """Get the default secret server.

    :param mode:  Optional string mode specifying secret server to get. If
                  None, then we try OX_SECRETS_MODE from env and then
                  settings.OX_SECRETS_MODE.

    """
    if not mode:
        mode = os.environ.get('OX_SECRETS_MODE', settings.OX_SECRETS_MODE)
    mode = mode.lower()
    if mode in ['fss', 'file']:
        return fss.FileSecretServer
    if mode in ['evs', 'env']:
        return evs.EnvVarSecretServer
    if mode == 'aws':
        # delayed import so boto3 does not need to be installed if
        # the aws secret server is never used
        from ox_secrets.core import aws  \
            # pylint:disable=import-outside-toplevel
        return aws.AWSSecretServer
    raise ValueError(f'Invalid secret server mode "{mode}"')


def get_secret(name: str, category: str = 'root',
               server: typing.Optional[
                   typing.Union[str, common.SecretServer]] = None) -> str:
    """Return desired secret.

    :param name: str: Name of secret to get

    :param category: str ='root': Category of secret.

    :param server=None:  Optional server to use (either the class or
                         string name for it such as 'fss' or 'aws'. If
                         not provided, then we call get_server() to
                         get it.

    ~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    :return:  Desired secret.

    ~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    PURPOSE:  This is a convenience function and meant to be the main
              function that most applications need to call.

    """
    if server is None or isinstance(server, str):
        server = get_server(mode=server)
    result = server.get_secret(name, category)
    return result


def get_secret_dict(
        mode: typing.Optional[str] = None, category: str = 'root',
        allow_update: bool = True,
        loader_params: typing.Optional[dict] = None,
        service_name: typing.Optional[str] = None) -> typing.Dict[
            str, typing.Any]:
    """Lookup secret with given name and return it.

    :param mode=None:  Optional string mode for calling get_server.

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

    :return:   Dictionary of secrets for given category.

    ~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    PURPOSE:   Simple way to lookup dictionary of secrets.

    """
    server = get_server(mode=mode)
    return server.get_secret_dict(
        category=category, allow_update=allow_update,
        loader_params=loader_params, service_name=service_name)


def forget_secrets(server: common.SecretServer = None) -> str:
    """Forget all secrets.
    """
    if server is None:
        server = get_server()
    server.clear_cache()


def store_secrets(new_secret_dict: typing.Dict[str, str],
                  category: str, server: typing.Optional[
                      typing.Union[str, common.SecretServer]] = None,
                  **storage_params):
    """Store secrets to back-end

    :param new_secret_dict:  Dictionary or name value pairs for secrets.

    :param category:  String category for secrets to store.

    :param server:  Secret server to use.

    :param **storage_params:   Optional storage parameters for back-end.
    ~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    PURPOSE:  Store the secrets in new_secret_dict.

    """
    if server is None:
        server = get_server()
    server.store_secrets(new_secret_dict, category, **storage_params)
