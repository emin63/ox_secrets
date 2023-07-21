"""Simple Command Line Interface to get secrets.
"""

import logging
import argparse

from ox_secrets import server


def prep_parser():
    """Prepare parser for command line.
    """
    parser = argparse.ArgumentParser(
        prog='ox_secrets',
        description='Command Line Interface to lookup secrets.')
    parser.add_argument(
        'name', help='Name of the secret to lookup.')
    parser.add_argument(
        '--raise-error', action='store_true',
        help='Force raising exception to see stack trace.')
    parser.add_argument('--loglevel', default='ERROR', help=(
        'Log level to use (e.g., DEBUG, INFO, WARNING, ERROR).'))
    parser.add_argument(
        '--category', default='root', help=(
            'Category of the secret to lookup (default is "root")'))
    parser.add_argument(
        '--mode', default=None, help=(
            'Mode to use in finding secret server.'))
    parser.add_argument(
        '--loader', action='append', help=(
            'Loader params (e.g., service_name/ssm)'
            ' to use AWS parameter store'
            ))

    return parser


def main():
    """Main implementation of command line.
    """
    parser = prep_parser()
    args = parser.parse_args()
    result = 'unknown error'
    try:
        logging.getLogger('').setLevel(getattr(logging, args.loglevel))
        my_server = server.get_server(mode=args.mode)
        loader_params = {}
        for item in (args.loader or []):
            param_name, *param_value = item.split('/')
            param_value = '/'.join(param_value)
            loader_params[param_name] = param_value
        result = my_server.get_secret(
            name=args.name, category=args.category,
            loader_params=loader_params)
    except Exception as problem:  # pylint: disable=broad-except
        if args.raise_error:
            raise
        msg = (f'Error in CLI: {problem}.\n'
               'Pass --raise-error to force raising to see stack trace.')
        logging.error(msg)
        result = 'Error in CLI.'

    print(result)


if __name__ == '__main__':
    main()
