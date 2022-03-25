Introduction
============

The ``ox_secrets`` package provides a simple secret server for python.
You can use simple file based secret storage in development and testing
and then add more sophisticated secret storage in production. Similarly,
you can use it to switch which type of secret manager you are using by
changing only the mode for ``ox_secerts`` without having to re-write the
rest of your code.

Think of it similar to an ORM for secrets.

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
