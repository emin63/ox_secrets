"""AWS Secret Manager.

This module provides a secret server using the AWS system.
"""

import os
import logging
import typing
import json


try:
    import boto3
except Exception as problem:  # pylint: disable=broad-except
    logging.warning(
        'Unable to import boto3 because %s; aws secrets unavailable',
        str(problem))


from ox_secrets import settings
from ox_secrets.core import common


class AWSSecretServer(common.SecretServer):
    """Class to handle getting secrets from AWS.
    """

    @classmethod
    def load_secret_from_aws(
            cls, secret_id: str, profile_name: typing.Optional[
                str] = None, **kwargs) -> typing.Dict[str, str]:
        """Helper to load given secret_id from AWS.
        """
        storage = kwargs.pop('storage', os.path.splitext(
            secret_id)[-1]).lower().lstrip('.')
        if profile_name is None:
            profile_name = settings.OX_SECRETS_AWS_PROFILE_NAME
        logging.warning(
            'Connecting to boto3 for profile %s to read secrets for %s',
            profile_name, secret_id)
        service_name = kwargs.pop('service_name', 'secretsmanager')
        session = boto3.Session(profile_name=profile_name, **kwargs)
        client = session.client(service_name=service_name)
        if service_name == 'secretsmanager':
            get_secret_value_response = client.get_secret_value(
                SecretId=secret_id)
            secret_data = get_secret_value_response['SecretString']
        elif service_name == 'ssm':
            get_secret_value_response = client.get_parameter(Name=secret_id)
            secret_data = get_secret_value_response['Parameter']['Value']
        else:
            raise ValueError(f'Invalid service_name: {service_name}')

        if storage == 'json':
            secret_dict = json.loads(secret_data)
        else:
            if storage != 'raw':
                logging.warning('Intpereting unknown storage as raw.')
            secret_dict = {secret_id: secret_data}

        return secret_dict

    @classmethod
    def load_cache(cls, name: typing.Optional[str] = None,
                   category: typing.Optional[str] = None,
                   loader_params: typing.Optional[dict] = None):
        """Load secrets and cache them from back-end store.

        :param name:  String name of secret desired. If this is None, then
                      all secrets for given category are loaded.

        :param category:  String name of secret desired. Same as secret-id for
                          AWS command line interface.


        ~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

        PURPOSE:  Fill cls._cache with data from secrets store.
                  Sub-classes must implement.

        """
        loader_params = loader_params if loader_params is not None else {}
        data = cls.load_secret_from_aws(secret_id=category, **loader_params)
        assert isinstance(data, dict)
        with cls._lock:
            cdict = cls._cache.get(category, {})
            if not cdict:
                cls._cache[category] = cdict
            cdict.update(data)

    @classmethod
    def store_secrets(cls, new_secret_dict: typing.Dict[str, str],
                      category: str, **storage_params):
        """Implement as required by parent class.
        """
        cls.store_secrets_to_aws(new_secret_dict, category, **storage_params)

    @classmethod
    def store_secrets_to_aws(
            cls, new_secret_dict: typing.Dict[str, str], category: str,
            profile_name: typing.Optional[str] = None, **kwargs):
        """Helper to store secrets to back-end file as required by parent.

        :param new_secret_dict:  Dictionary or name value pairs for secrets.

        :param category:  String category for secrets to store.

        ~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

        PURPOSE:  Store the secrets in new_secret_dict to AWS.

        """
        logging.warning('Reading original secrets for "%s"', category)
        my_secrets = cls.load_secret_from_aws(
            category, profile_name, **kwargs)

        service_name = kwargs.pop('service_name', 'secretsmanager')
        session = boto3.Session(profile_name=profile_name, **kwargs)
        client = session.client(service_name=service_name)

        with cls._lock:
            my_secrets.update(new_secret_dict)
            secret_data = json.dumps(my_secrets)
            if service_name == 'secretsmanager':
                response = client.put_secret_value(
                    SecretId=category, SecretString=secret_data)
                logging.debug('Got response %s from AWS.', response)
            elif service_name == 'ssm':
                response = client.put_parameter(
                    Name=category, Value=secret_data, Type='String',
                    Overwrite=True)
            else:
                raise ValueError(f'Invalid service_name: {service_name}')
            cls._cache[category] = my_secrets
