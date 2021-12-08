"""File system server.

This module provides a secret server using the file system.
This is helpful for local testing and very simple operation.
"""


import logging
import csv
import os

from ox_secrets import settings
from ox_secrets.core import common


class FileSecretServer(common.SecretServer):
    """Class to handle getting secrets from file.
    """

    @classmethod
    def load_secrets_file(cls, filename=None, encoding='utf8'):
        """Load secrets file from given filename.

        :param filename=None:    Optional filename for secrets. This
                                 defaults to ~/.ox_secrets.csv.
                                 It shall be a CSV file with header
                                 category,name,value,notes.

        ~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

        PURPOSE:  Fill cls._cache with data from secrets file.

        """
        if filename is None:
            filename = os.environ.get(
                'OX_SECRETS_FILE', settings.OX_SECRETS_FILE)
        logging.warning('Opening secrets file "%s"', filename)
        with open(filename, 'r', encoding=encoding) as sfd:
            reader = csv.DictReader(sfd)
            with cls._lock:
                for line in reader:
                    if line['category'] not in cls._cache:
                        cls._cache[line['category']] = {}
                    cls._cache[line['category']][line['name']] = line[
                        'value']

    @classmethod
    def load_cache(cls):
        "Implement loading cache from a file."
        return cls.load_secrets_file()
