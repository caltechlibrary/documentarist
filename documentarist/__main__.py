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
from   bun import UI, inform, warn, alert, alert_fatal
from   commonpy.data_utils import timestamp
from   commonpy.file_utils import readable
from   commonpy.module_utils import module_path
from   inspect import cleandoc
import os
from   os.path import exists, join, dirname
import re
from   sidetrack import set_debug, log, log, loglist
import sys
from   sys import exit as exit
from   textwrap import wrap, fill, dedent

from   common.exceptions import UserCancelled, FileError, CannotProceed
from   common.exit_codes import ExitCode

import documentarist
from   documentarist import print_version
from   documentarist.command import Command, docstring_summary, command_list
from   documentarist.config import Config, ConfigCommand


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
                            help = 'use the specified configuration file')
        parser.add_argument('-q', '--quiet', action = 'store_true',
                            help = 'only print important messages while working')
        parser.add_argument('-V', '--version', action = 'store_true',
                            help = 'print version info and exit')
        parser.add_argument('-@', '--debug', action = 'store', metavar = 'OUT',
                            help = 'write trace to destination ("-" means console)')
        parser.add_argument('command', nargs='*',
                            help = 'Available commands: ' + command_list(self))
        self._parser = parser


    def run(self, arg_list):
        '''Process command-line arguments and run Documentarist functions.'''

        args = self._parser.parse_args(arg_list[1:]) # Skip the program name.

        ui = UI('Documentarist', show_banner = False, be_quiet = args.quiet)
        ui.start()

        # Handle special arguments and early exits ----------------------------

        if args.debug:
            set_debug(True, args.debug, extra = '%(threadName)s')
            import faulthandler
            faulthandler.enable()

        if args.version:
            print_version()
            exit(int(ExitCode.success))

        if args.configfile:
            if not exists(args.configfile):
                alert_fatal(f'Config file does not exist: {args.configfile}')
                exit(int(ExitCode.bad_arg))
            elif not readable(args.configfile):
                alert_fatal(f'Config file is not readable: {args.configfile}')
                exit(int(ExitCode.file_error))

        # Do the real work ----------------------------------------------------

        exception = None
        exit_code = ExitCode.success
        try:
            Config.load(args.configfile)
            Config.set('debug', args.debug)
            Config.set('quiet', args.quiet)

            log('▼'*3 + f' started {timestamp()} ' + '▼'*3)
            log(f'given args: {args}')
            log(f'configuration:')
            loglist(f'  {var} = {value}' for var, value in Config.settings())

            if args.command:
                command_name = args.command[0]
                methods = {m for m in dir(self) if not m.startswith('_')}
                # "run" is our internal main entry point; don't expose to users
                available_commands = methods - {'run'}
                if command_name in available_commands:
                    # Use the dispatch pattern to delegate to a command handler.
                    log(f'dispatching to command "{command_name}"')
                    getattr(self, command_name)(args.command[1:])
                else:
                    alert_fatal(f'Unrecognized command: "{command_name}"')
                    self._parser.print_help()
                    exit_code = ExitCode.bad_arg
            else:
                self._parser.print_help()

            log('▲'*3 + f' stopped {timestamp()} ' + '▲'*3)
        except Exception as ex:
            exception = sys.exc_info()

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
                alert_fatal(f'An error occurred ({ex_cls.__name__}): {str(ex)}')
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


    def extract(self, args):
        '''Process document images to extract text and other information.'''
        ExtractCommand(args)


    def config(self, args):
        '''Configure Documentarist's behavior.'''
        ConfigCommand(args)


# Main entry point.
# .............................................................................

# The following entry point definition is for the console_scripts keyword
# option to setuptools.  The entry point for console_scripts has to be a
# function that takes zero arguments.
def console_scripts_main():
    Main().run(sys.argv)


# The following allows users to invoke this using "python3 -m documentarist".
if __name__ == '__main__':
    Main().run(sys.argv)
