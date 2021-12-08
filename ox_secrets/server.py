"""High-level file to work with secret servers.
"""

import os

from ox_secrets import settings
from ox_secrets.core import common, fss


def get_server() -> common.SecretServer:
    """Get the default secret server.

You can set the OX_SECRETS_MODE environment variable or the
ox_secrets.settings.OX_SECRETS_MODE python variable to be a string
indicating the type of server you want to use.

    """
    mode = os.environ.get('OX_SECRETS_MODE', settings.OX_SECRETS_MODE)
    mode = mode.lower()
    if mode in ['fss', 'file']:
        return fss.FileSecretServer
    raise ValueError('Invalid secret server mode "%s"' % mode)


def get_secret(name: str, category: str = 'root',
               server: common.SecretServer = None) -> str:
    """Return desired secret.

    :param name: str: Name of secret to get

    :param category: str ='root': Category of secret.

    :param server=None:  Optional server to use. If not provided, then
                         we call get_server() to get it.

    ~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    :return:  Desired secret.

    ~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    PURPOSE:  This is a convenience function and meant to be the main
              function that most applications need to call.

    """
    if server is None:
        server = get_server()
    result = server.get_secret(name, category)
    return result


def forget_secrets(server: common.SecretServer = None) -> str:
    """Forget all secrets.
    """
    if server is None:
        server = get_server()
    server.clear_cache()
