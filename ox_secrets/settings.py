"""Settings for how to use ox_secrets
"""

import os

# Specifies which type of secret server you
# want to use. Can change this at run-time
# or override with environment variable OX_SECRETS_MODE
OX_SECRETS_MODE = os.environ.get('OX_SECRETS_MODE', 'FILE')

# Specifies default location of secrets file for server from
# file system in fss.py. Default is ~/.ox_secrets. You can
# override either with environment variable OX_SECRETS_FILE
# or by changing below at run-time.
OX_SECRETS_FILE = os.path.join(os.environ.get(
    'OX_SECRETS_FILE', os.environ.get('HOME', '/')), '.ox_secrets.csv')


# Used for the aws secrets manager. Specifies the profile name in your ~/.aws.
OX_SECRETS_AWS_PROFILE_NAME = None

# If you use '^prod/' for OX_SECRETS_CATEGORY_REGEXP and
# use 'test/' for OX_SECRETS_CATEGORY_REPLACE then you will
# automatically have the all categories starting with 'prod/' replaced
# with 'test/' in calls to get_secret.
OX_SECRETS_CATEGORY_REGEXP = os.environ.get(
    'OX_SECRETS_CATEGORY_REGEXP', None)
OX_SECRETS_CATEGORY_REPLACE = os.environ.get(
    'OX_SECRETS_CATEGORY_REPLACE', None)
