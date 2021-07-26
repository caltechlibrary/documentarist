#!/usr/local/bin/python3

from clize import run
from sigtools.wrappers import decorator


@decorator
def no_color(wrapped, *args, no_color=False):
    """
    Formatting options:

    :param uppercase: Print output in capitals
    """
    return wrapped


@no_color
def credentials(service, path):
    '''Store credentials for accessing remote service.

    :param service: The service for which credentials will be stored
    :param file: Path to JSON file containing the credentials

    '''

    return word


def config(show = False, basename = 'document', outputdir = '.'):
    '''Configure Documentarist.

    :param show: Describe the current configuration
    :param basename: The basename
    :param outputdir: Where to write the output
    '''

    return False


def help_text():
    return '''
This is the main documentation.

There's a lot here. There's a lot here.
There's a lot here. There's a lot here.
There's a lot here. There's a lot here.
There's a lot here. There's a lot here.

Command summary
~~~~~~~~~~~~~~~
'''


def func(*, param:int='p'):
    print('par', par)


if __name__ == '__main__':
    run(credentials, config, func, description = help_text())
