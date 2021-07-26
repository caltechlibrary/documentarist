'''
Documentarist: analyze scanned documents in Caltech archives

Authors
-------

Michael Hucka <mhucka@caltech.edu> -- Caltech Library

Copyright
---------

Copyright (c) 2020 by the California Institute of Technology.  This code
is open-source software released under a 3-clause BSD license.  Please see the
file "LICENSE" for more information.
'''

from   bun import UI, inform, warn, alert, alert_fatal
from   nuclear import CliBuilder, argument, flag, parameter, subcommand
import signal
import shutil
import sys
from   sys import exit as exit
from   textwrap import wrap

from common.exceptions import UserCancelled, FileError, CannotProceed
from common.exit_codes import ExitCode

if __debug__:
    from sidetrack import set_debug, log, logr


# Help text and description of the user interface.
# .............................................................................

documentarist_description = '''Documentarist

Documentarist takes images of documents and photos, and extracts text and
other data using a combination of cloud-based services and local computation.'''


# User interface
# .............................................................................

# move these to config.py, extract.py
# those files will do what's needed with metaflow

def show_help():
    # use a pager and bold facing and underlining
    pass

def config_show():
    pass

def config_basename():
    pass

def config_auth():
    pass

def config_outputdir():
    pass

def extract_textregions():
    pass

def extract_text():
    pass


# Main entry point.
# .............................................................................

def main_cli():
    CliBuilder(help = documentarist_description).has(
        flag('-q', '--quiet',
             help = 'be less chatty -- only print important messages'),
        flag('-@', '--debug',
             help = 'write trace to destination ("-" means console)'),
        flag('-V', '--version',
             help = 'print version information and exit'),
        subcommand('help', run = show_help,
                   help = 'Display detailed help and quit'),
        subcommand('config').has(
            subcommand('show', run = config_show,
                       help='Show all configuration values'),
            subcommand('outputdir', run = config_outputdir,
                       help='Show or set output directory').has(
                           argument('dir', type = str, required = False,
                                    help = 'Destination directory'),
                       ),
            subcommand('auth', run = config_auth,
                       help='Show or set authorization for a cloud service').has(
                           argument('service', type = str, required = True,
                                    help = 'The name of the service'),
                           argument('file', type = str, required = False,
                                    help = 'JSON file containing credentials'),
                       ),
            subcommand('basename', run = config_basename,
                       help = 'Show or set the base name for downloaded files').has(
                           argument('name', type = str, required = False,
                                    help = 'Documents will be named "name-N", where N is an integer'),
            ),
        ),
        subcommand('extract').has(
            subcommand('textregions', run = extract_textregions,
                       help='Extract regions of text from the document image').has(
                           argument('file', type = str, required = False,
                                    help = 'Image file'),
                       ),
            subcommand('text', run = extract_textregions,
                       help='Extract text from the document image').has(
                           argument('file', type = str, required = False,
                                    help = 'Image file'),
                       ),
        ),
    ).run()


# The following entry point definition is for the console_scripts keyword
# option to setuptools.  The entry point for console_scripts has to be a
# function that takes zero arguments.
def console_scripts_main():
    main_cli()


# The following allows users to invoke this using "python3 -m zowie".
if __name__ == '__main__':
    main_cli()
