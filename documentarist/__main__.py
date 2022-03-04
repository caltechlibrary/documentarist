'''
Documentarist: analyze scanned documents in Caltech archives

Authors
-------

Michael Hucka <mhucka@caltech.edu> -- Caltech Library

Copyright
---------

Copyright (c) 2020-2021 by the California Institute of Technology.  This code
is open-source software released under a 3-clause BSD license.  Please see the
file "LICENSE" for more information.
'''

from   argparse import ArgumentParser, RawDescriptionHelpFormatter
from   commonpy.data_utils import timestamp
from   commonpy.file_utils import readable
from   commonpy.module_utils import module_path
from   inspect import cleandoc
import os
from   os.path import exists, join, dirname
import re
import sys
from   sys import exit as exit
from   textwrap import wrap, fill, dedent

import documentarist
from   documentarist import print_version
from   documentarist.command import Command, docstring_summary, command_list
from   documentarist.command import available_commands
from   documentarist.config import Config, ConfigCommand
from   documentarist.exceptions import UserCancelled, FileError, CannotProceed
from   documentarist.exit_codes import ExitCode
from   documentarist.log import enable_logging, log
from   documentarist.ui import UI, inform, warn, alert


# The main function.
# .............................................................................
# This implements the top level of the command parser and is used as the entry
# point for Documentarist. This is what is invoked as the user command "dm".
#
# The dispatch approach used here was inspired by C. Seibert's 2014 blog post:
# https://chase-seibert.github.io/blog/2014/03/21/python-multilevel-argparse.html

class Main(Command):
    '''"dm" is the command-line interface for Documentarist, a system that
    takes images of documents and photos, and extracts text and other data
    using a combination of cloud-based services and local computation.  The
    command-line interface allows you to configure and run Documentarist
    interactively as well as from shell scripts.
    '''

    def __init__(self):
        # Note we deliberately do not call super().__init__() here. We need to
        # set up the parser a little bid differently, with additional options.
        parser = ArgumentParser(description = docstring_summary(self),
                                formatter_class = RawDescriptionHelpFormatter)
        parser.add_argument('-c', '--configfile', action = 'store', metavar = 'C',
                            help = 'override configuration with values from file C')
        parser.add_argument('-q', '--quiet', action = 'store_true',
                            help = 'only print important messages while working')
        parser.add_argument('-V', '--version', action = 'store_true',
                            help = 'print version info and exit')
        parser.add_argument('-@', '--debug', action = 'store', metavar = 'OUT',
                            help = 'write trace to destination ("-" means console)')
        parser.add_argument('command', nargs='*',
                            help = 'Available commands: ' + available_commands(self))
        self._parser = parser


    def _run(self, arg_list):
        '''Process command-line arguments and run Documentarist functions.'''

        # Handle special arguments and early exits ----------------------------

        args = self._parser.parse_args(arg_list[1:]) # Skip the program name.

        if args.version:                # User supplied -V.
            args.command = ['version']

        config_debug(args.debug)

        # Do the real work ----------------------------------------------------

        log('▼'*3 + f' started {timestamp()} ' + '▼'*3)
        log('command line: ' + str(sys.argv))

        ui = UI('Documentarist', show_banner = False, be_quiet = args.quiet)
        ui.start()

        if args.configfile:
            if not exists(args.configfile):
                alert(f'Config file does not exist: {args.configfile}')
                exit(int(ExitCode.bad_arg))
            elif not readable(args.configfile):
                alert(f'Config file is not readable: {args.configfile}')
                exit(int(ExitCode.file_error))

        exception = None
        exit_code = ExitCode.success
        try:
            Config.load(args.configfile)
            Config.set('debug', args.debug)
            Config.set('quiet', args.quiet)
            Config.log_settings()

            if args.command:
                command_name = args.command[0]
                command_args = args.command[1:]
                if command_name in command_list(self):
                    # Use the dispatch pattern to delegate to a command handler.
                    log(f'dispatching to command "{command_name}"')
                    getattr(self, command_name)(command_args)
                else:
                    alert(f'Unrecognized command: "{command_name}"')
                    self._parser.print_help()
                    exit_code = ExitCode.bad_arg
            else:
                self._parser.print_help()
        except Exception as ex:
            exception = sys.exc_info()
        finally:
            log('▲'*3 + f' stopped {timestamp()} ' + '▲'*3)

        # Try to deal with exceptions gracefully ------------------------------

        if exception:
            if exception[0] == CannotProceed:
                exit_code = exception[1].args[0]
            elif exception[0] in [KeyboardInterrupt, UserCancelled]:
                log(f'received {exception.__class__.__name__}')
                warn('Interrupted.')
                exit_code = ExitCode.user_interrupt
            else:
                ex_cls = exception[0]
                ex = exception[1]
                alert(f'An error occurred ({ex_cls.__name__}): {str(ex)}')
                # Return a better error code for some common cases.
                if ex_cls in [FileNotFoundError, FileExistsError, PermissionError]:
                    exit_code = ExitCode.file_error
                else:
                    exit_code = ExitCode.exception
                from traceback import format_exception
                details = ''.join(format_exception(*exception))
                log(f'Exception: {str(ex)}\n{details}')

        # And exit ------------------------------------------------------------

        if exit_code == ExitCode.user_interrupt:
            # This is a sledgehammer, but it kills everything including ongoing
            # network calls. I haven't found a more reliable way to interrupt.
            os._exit(int(exit_code))
        else:
            exit(int(exit_code))


    def version(self, args):
        '''Print Documentarist version information, and exit.'''
        print_version()


    def config(self, args):
        '''Configure Documentarist's behavior.'''
        ConfigCommand(args)


    def label(self, args):
        '''Label documents with tags describing their content.'''
        LabelCommand(args)


    def extract(self, args):
        '''Extract text and other information from documents.'''
        ExtractCommand(args)


# Miscellaneous utilities local to this module.
# .............................................................................

def config_debug(debug_destination):
    '''Takes the value of the --debug flag & configures debugging accordingly.'''
    if debug_destination:
        enable_logging(debug_destination)
        import faulthandler
        faulthandler.enable()
        if not os.name == 'nt':     # Can't use next part on Windows.
            import signal
            from boltons.debugutils import pdb_on_signal
            pdb_on_signal(signal.SIGUSR1)


# Main entry point.
# .............................................................................

# The following entry point definition is for the console_scripts keyword
# option to setuptools.  The entry point for console_scripts has to be a
# function that takes zero arguments.
def console_scripts_main():
    Main()._run(sys.argv)


# The following allows users to invoke this using "python3 -m documentarist".
if __name__ == '__main__':
    Main()._run(sys.argv)
