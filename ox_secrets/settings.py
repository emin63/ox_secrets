"""Settings for how to use ox_secrets
"""

import os

# Specifies which type of secret server you
# want to use. Can change this at run-time
# or override with environment variable OX_SECRETS_MODE
OX_SECRETS_MODE = 'FILE'

# Specifies default location of secrets file for server from
# file system in fss.py. Default is ~/.ox_secrets. You can
# override either with environment variable OX_SECRETS_FILE
# or by changing below at run-time.
OX_SECRETS_FILE = os.path.join(os.environ.get('HOME', '/'), '.ox_secrets.csv')
