"""File system server.

This module provides a secret server using the file system.
This is helpful for local testing and very simple operation.
"""


import logging
import csv
import os
import typing
import json

from ox_secrets import settings
from ox_secrets.core import common


class FileSecretServer(common.SecretServer):
    """Class to handle getting secrets from file.
    """

    @classmethod
    def load_secrets_file(cls, filename=None, encoding='utf8',
                          file_type=None, default_category='root'):
        """Load secrets file from given filename.

        :param filename=None:    Optional filename for secrets. This
                                 defaults to ~/.ox_secrets.csv.
                                 It shall be a CSV file with header
                                 category,name,value,notes. You can also
                                 provide a .json file containing a dict
                                 of name value pairs which will all go
                                 in the default_category.

        :param encoding='utf8':  Default encoding for opening files.

        :param file_type:  Either .csv or .json or None if you want to
                           select based on file extension.

        :param default_category='root':  Category to use when cannot
                                         otherwise find it.

        ~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

        PURPOSE:  Fill cls._cache with data from secrets file.

        """
        if filename is None:
            filename = os.environ.get(
                'OX_SECRETS_FILE', settings.OX_SECRETS_FILE)
        logging.warning('Opening secrets file "%s"', filename)
        with cls._lock, open(filename, 'r', encoding=encoding) as sfd:
            if file_type is None:
                file_type = os.path.splitext(filename)[-1].lower()
            elif file_type == '.raw':
                contents = [{'name': default_category, 'value': sfd.read()}]
            elif file_type == '.csv':
                contents = list(csv.DictReader(sfd))
            elif file_type == '.json':
                contents = [{'name': k, 'value': v}
                            for k, v in json.load(sfd).items()]
            else:
                raise ValueError(f'Cannot handle secrets {file_type=}')
            for line in contents:
                line_category = line.get('category', default_category)
                if line_category not in cls._cache:
                    cls._cache[line_category] = {}
                cls._cache[line_category][line['name']] = line[
                    'value']

    @classmethod
    def load_cache(cls, name: typing.Optional[str] = None,
                   category: typing.Optional[str] = None,
                   loader_params: typing.Optional[dict] = None):
        "Implement loading cache from a file."
        loader_params = loader_params if loader_params is not None else {}
        return cls.load_secrets_file(default_category=category,
                                     **loader_params)

    @classmethod
    def store_secrets(cls, new_secret_dict: typing.Dict[str, str],
                      category: str, **storage_params):
        """Implement as required by parent class.
        """
        cls.store_secrets_to_file(new_secret_dict, category, **storage_params)

    @classmethod
    def store_secrets_to_file(
            cls, new_secret_dict: typing.Dict[str, str], category: str,
            filename: typing.Optional[str] = None,
            encoding: str = 'utf8'):
        """Helper to store secrets to back-end file as required by parent.

        :param new_secret_dict:  Dictionary or name value pairs for secrets.

        :param category:  String category for secrets to store.

        :param filename: Path to store secrets to.

        :param encoding: Encoding for file.
        ~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

        PURPOSE:  Store the secrets in new_secret_dict to filename.

        """
        if filename is None:
            filename = os.environ.get(
                'OX_SECRETS_FILE', settings.OX_SECRETS_FILE)
        logging.warning('Opening secrets file "%s"', filename)
        data = []
        with cls._lock:
            if not os.path.exists(filename):
                logging.warning('Creating empty file for %s.', filename)
                with open(filename, 'a', encoding='utf8') as sfd:
                    pass  # this just creates an empty file if necessary
            with open(filename, 'r', encoding=encoding) as sfd:
                reader = csv.DictReader(sfd)
                for item in reader:
                    if item['name'] in new_secret_dict and item[
                            'category'] == category:
                        logging.info('Replacing old value for %s/%s',
                                     item['name'], item['category'])
                    else:
                        data.append(item)
            with open(filename, 'w', encoding=encoding) as sfd:
                writer = csv.DictWriter(sfd, fieldnames=[
                    pair[0] for pair in cls._data_fields])
                writer.writeheader()
                for line in data:
                    writer.writerow(line)
                for name, value in new_secret_dict.items():
                    writer.writerow({
                        'name': name, 'category': category,
                        'value': value, 'notes': 'via store_secrets'})
                    if category in cls._cache:
                        cls._cache[category][name] = value
