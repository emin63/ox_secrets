Introduction
============

The ``ox_secrets`` package provides a simple secret manager for python.
You can think ``ox_secrets`` like an ORM for secrets with the following
goals:

-  Simple, light-weight management of secrets.
-  Handle various back-ends for storing secrets:

   -  environment variables
   -  Amazon Web Services (AWS)
   -  local files

-  Easy to switch secrets for dev, testing, or production.

   -  You can use simple file based secret storage in development and
      testing and then add more sophisticated secret storage in
      production. Similarly, you can use it to switch which type of
      secret manager you are using by changing only the mode for
      ``ox_secerts`` (e.g., by setting ``OX_SECRETS_MODE`` environment
      variable or setting the value of
      ``ox_secrets.settings.OX_SECRETS_MODE`` in python) without having
      to re-write the rest of your code.

Currently, the following back ends are supported:

-  ``fss``: File secret server

   -  Reads secrets from a local file.
   -  Useful for development and testing.

-  ``evs``: Environment variable server.

   -  While other modes back ends can use environment variables to
      override, this mode **ONLY** looks at environment variables.

-  ``aws``: Uses the AWS Secret Manager or AWS Parameter Store

   -  By default the ``aws`` back-end will use the AWS Secrets Manager.
      If you want to use the parameter store instead, provide
      ``service_name='ssm'``.

The main secret server can merge and cache secrets from multiple
back-ends in case your secrets are split across various places.

Usage
=====

To get started, you can simply ``pip install ox_secrets`` as usual and
then see either the `Usage in Python <#usage-in-python>`__ section for
how to use in python or the `Usage in Command
Line <#usage-in-command-line>`__ for the CLI.

Usage in Python
---------------

.. code:: python


   #The =ox_secrets= package provides a simple secret server with various
   #back-ends. The following illustrates example usage.

   # First we setup an example secrets file:

   >>> import os, tempfile, csv
   >>> fn = tempfile.mktemp(suffix='_ox_secrets.csv')
   >>> writer = csv.writer(open(fn, 'w')).writerows([
   ... ['name', 'category', 'value', 'notes'],
   ... ['example_name', 'root', 'super_secret', 'example secret'],
   ... ['example_pw', 'prod/data', 'super_secret_pw', 'example secret_pw'],
   ... ['example_pw', 'test/data', 'unsecret_test_pw', 'example secret test pw'],
   ... ['example_pw', 'alt', 'alt_unsecret_test_pw', 'alt secret test pw']])
   >>> print(open(fn).read().strip())
   name,category,value,notes
   example_name,root,super_secret,example secret
   example_pw,prod/data,super_secret_pw,example secret_pw
   example_pw,test/data,unsecret_test_pw,example secret test pw
   example_pw,alt,alt_unsecret_test_pw,alt secret test pw

   >>> from ox_secrets import settings, server as oss
   >>> oss.settings.OX_SECRETS_FILE = fn # default is ~/.ox_secrets.csv
   >>> oss.forget_secrets()  # Clear it to make sure we start fresh
   >>> oss.get_secret('example_name')
   'super_secret'

   #  We can also get a dictionary of all the secrets for a given category:

   >>> oss.get_secret_dict(category='test/data')
   {'example_pw': 'unsecret_test_pw'}

   #  We can also setup our environment variables from a secret dictionary
   #  using the setup_env_from_secrets for a given secret server:

   >>> oss.get_server().setup_env_from_secrets(category='test/data')
   >>> os.environ['example_pw']
   'unsecret_test_pw'


   #  Sometimes it is nice to be able to just pass a dictionary of
   #  credential information to get_secret:

   >>> creds = {'name': 'example_name', 'category': 'root', 'server': 'fss'}
   >>> oss.get_secret(**creds)
   'super_secret'

   #  You can also puts secrets into the environment variables:

   >>> os.environ['OX_SECRETS_ROOT_EXAMPLE_NAME'] = 'other'
   >>> oss.get_secret('example_name')
   'other'

   #  You can use the OX_SECRETS_CATEGORY_REGEXP and
   #  the OX_SECRETS_CATEGORY_REPLACE either in the settings file
   #  or environment variables (before starting python) to automatically
   #  switch from production to testing secrets:

   >>> oss.get_secret('example_pw', 'prod/data')
   'super_secret_pw'
   >>> oss.forget_secrets()  # Clear it to make sure we start fresh
   >>> oss.settings.OX_SECRETS_CATEGORY_REGEXP = '^prod/'
   >>> oss.settings.OX_SECRETS_CATEGORY_REPLACE = 'test/'
   >>> oss.get_secret('example_pw', 'prod/data')
   'unsecret_test_pw'


   #  If desired, you can also store secrets (assuming
   #  you have appropriate permissions):

   >>> oss.store_secrets({'example_pw': 'foobar'}, category='alt')
   >>> oss.get_secret('example_pw', category='alt')
   'foobar'

   #  Now cleanup

   >>> os.remove(fn)


   #  If you have an account with the appropriate permissions (e.g.,
   #  you may need to set the AWS_PROFILE environment variable to
   #  to such an account), you can also store secrets and parameters
   #  to aws.
   #  
   #  For example, you could do something like:
   #  
   #      oss.get_server(mode='aws').store_secrets(
   #          {'test_storage':'foobar'}, category=AWS_SECRET_ID)
   #  
   #  to store a secret to the existing secret with secret ID
   #  `AWS_SECRET_ID` on Amazon Web Services. You could also proide the
   #  `service_name='ssm'` argument if you wanted to use the parameter store
   #  instead of the secret store via something like:
   #  
   #      oss.get_server(mode='aws').store_secrets(
   #          {'test_storage':'foobar', category=AWS_PARAM_NAME,
   #          service_name='ssm')

Usage in Command Line
---------------------

You can also use ``ox_secrets`` from the command line.

For example, if you setup a secrets file in ``~/.ox_secrets.csv``
similar to the example in the `Usage in Python <#usage-in-python>`__
section, you can do something like

.. code:: shell

   ox_secrets example_name --category root

to extract the desired secret.

You can also pass other parameters (run ``ox_secrets --help`` for
details).
