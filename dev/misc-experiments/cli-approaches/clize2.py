#!/usr/local/bin/python3

from clize import run
from sigtools.wrappers import decorator

from sigtools.wrappers import decorator


@decorator
def no_color(wrapped, *args, no_color:'C'=False, **kwargs):
    """
    Formatting options:

    :param no_color: Do not color output
    """
    ret = wrapped(*args, **kwargs)
    if no_color:
        print('n')
    else:
        print('y')


@no_color
def credentials(service, path = 'F'):
    '''Store credentials for accessing remote service.

    :param service: The service for which credentials will be stored
    :param file: Path to JSON file containing the credentials

    '''

    return service


if __name__ == '__main__':
    run(credentials)
