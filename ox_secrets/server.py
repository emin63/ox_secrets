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
        from ox_secrets.core import aws
        return aws.AWSSecretServer
    raise ValueError('Invalid secret server mode "%s"' % mode)


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


def forget_secrets(server: common.SecretServer = None) -> str:
    """Forget all secrets.
    """
    if server is None:
        server = get_server()
    server.clear_cache()
