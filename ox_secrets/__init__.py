"""Simple secret server.

The ox_secrets package provides a simple secret server with various
back-ends. The following illustrates example usage.

First we setup an example secrets file:

>>> import os, tempfile, csv
>>> fn = tempfile.mktemp(suffix='_ox_secrets.csv')
>>> writer = csv.writer(open(fn, 'w')).writerows([
... ['name', 'category', 'value', 'notes'],
... ['example_name', 'root', 'super_secret', 'example secret'],
... ['example_pw', 'prod/data', 'super_secret_pw', 'example secret_pw'],
... ['example_pw', 'test/data', 'unsecret_test_pw', 'example secret test pw']])
>>> print(open(fn).read().strip())
name,category,value,notes
example_name,root,super_secret,example secret
example_pw,prod/data,super_secret_pw,example secret_pw
example_pw,test/data,unsecret_test_pw,example secret test pw

>>> from ox_secrets import settings, server as oss
>>> oss.settings.OX_SECRETS_FILE = fn # default is ~/.ox_secrets.csv
>>> oss.forget_secrets()  # Clear it to make sure we start fresh
>>> oss.get_secret('example_name')
'super_secret'

Sometimes it is nice to be able to just pass a dictionary of
credential information to get_secret:

>>> creds = {'name': 'example_name', 'category': 'root', 'server': 'fss'}
>>> oss.get_secret(**creds)
'super_secret'

You can also puts secrets into the environment variables:

>>> os.environ['OX_SECRETS_ROOT_EXAMPLE_NAME'] = 'other'
>>> oss.get_secret('example_name')
'other'

Finally, you can use the OX_SECRETS_CATEGORY_REGEXP and
the OX_SECRETS_CATEGORY_REPLACE either in the settings file
or environment variables (before starting python) to automatically
switch from production to testing secrets:

>>> oss.get_secret('example_pw', 'prod/data')
'super_secret_pw'
>>> oss.forget_secrets()  # Clear it to make sure we start fresh
>>> oss.settings.OX_SECRETS_CATEGORY_REGEXP = '^prod/'
>>> oss.settings.OX_SECRETS_CATEGORY_REPLACE = 'test/'
>>> oss.get_secret('example_pw', 'prod/data')
'unsecret_test_pw'

Now cleanup

>>> os.remove(fn)

"""

VERSION = '0.3.7'
