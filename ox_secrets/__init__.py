"""Simple secret server.

The ox_secrets package provides a simple secret server with various
back-ends. The following illustrates example usage.

First we setup an example secrets file:

>>> import os, tempfile, csv
>>> fn = tempfile.mktemp(suffix='_ox_secrets.csv')
>>> writer = csv.writer(open(fn, 'w')).writerows([
... ['name', 'category', 'value', 'notes'],
... ['example_name', 'root', 'super_secret', 'example secret']])
>>> print(open(fn).read().strip())
name,category,value,notes
example_name,root,super_secret,example secret

>>> from ox_secrets import settings, server as oss
>>> oss.settings.OX_SECRETS_FILE = fn # default is ~/.ox_secrets.csv
>>> oss.forget_secrets()  # Clear it to make sure we start fresh
>>> oss.get_secret('example_name')
'super_secret'

You can also puts secrets into the environment variables:

>>> os.environ['OX_SECRETS_ROOT_EXAMPLE_NAME'] = 'other'
>>> oss.get_secret('example_name')
'other'


Now cleanup

>>> os.remove(fn)

"""

VERSION = '0.3.2'
