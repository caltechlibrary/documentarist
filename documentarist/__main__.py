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

from   argparse import ArgumentParser, RawDescriptionHelpFormatter
from   bun import UI, inform, warn, alert, alert_fatal
from   commonpy.data_utils import timestamp
from   inspect import cleandoc
import re
from   shutil import get_terminal_size
import sys
from   sys import exit as exit
from   textwrap import wrap, fill, dedent

from common.exceptions import UserCancelled, FileError, CannotProceed
from common.exit_codes import ExitCode

import documentarist
from documentarist import print_version

if __debug__:
    from sidetrack import set_debug, log, logr


# Definition of argument parser.
# .............................................................................

# The dispatch approach used here was inspired by C. Seibert's 2014 blog post:
# https://chase-seibert.github.io/blog/2014/03/21/python-multilevel-argparse.html

class Main():
    '''Command-line interface for Documentarist.

    Documentarist takes images of documents and photos, and extracts text and
    other data using a combination of cloud-based services and local
    computation.
    '''

    def __init__(self, arg_list):
        '''Create the parser, parse the arguments, and dispatch commands.'''

        parser = ArgumentParser(description = summary_from_docstring(self),
                                formatter_class = RawDescriptionHelpFormatter)
        parser.add_argument('-C', '--no-color', action = 'store_true',
                            help = 'do not color-code terminal output')
        parser.add_argument('-q', '--quiet', action = 'store_true',
                            help = 'only print important messages while working')
        parser.add_argument('-V', '--version', action = 'store_true',
                            help = 'print version info and exit')
        parser.add_argument('-@', '--debug', action = 'store', metavar = 'OUT',
                            help = 'write trace to destination ("-" means console)')
        parser.add_argument('command', nargs='*',
                            help = 'Available commands: ' + command_list(self))

        # Process arguments and handle early exits ----------------------------

        args = parser.parse_args(arg_list[1:]) # Skip the program name.
        if __debug__: log(f'given args: {args}')

        ui = UI('Documentarist', show_banner = False, be_quiet = args.quiet,
                use_color = not args.no_color)
        ui.start()

        if args.debug:
            if __debug__: set_debug(True, args.debug, extra = '%(threadName)s')
            from rich.traceback import install as install_rich_traceback
            install_rich_traceback()
            import faulthandler
            faulthandler.enable()

        if args.version:
            print_version()
            exit(int(ExitCode.success))

        # Do the real work ----------------------------------------------------

        if __debug__: log('='*8 + f' started {timestamp()} ' + '='*8)
        exception = None
        try:
            if args.command:
                command_name = args.command[0]
                if hasattr(self, command_name):
                    # Use the dispatch pattern to delegate to a command handler.
                    if __debug__: log(f'dispatching to {command_name}')
                    getattr(self, command_name)(parser, args.command[1:])
                else:
                    alert_fatal(f'Unrecognized command: "{command_name}"')
                    parser.print_help()
                    exit_code = ExitCode.bad_arg
            else:
                parser.print_help()
        except Exception as ex:
            exception = sys.exc_info()

        # Try to deal with exceptions gracefully ----------------------------------

        exit_code = ExitCode.success
        if exception:
            if exception[0] == CannotProceed:
                exit_code = exception[1].args[0]
            elif exception[0] in [KeyboardInterrupt, UserCancelled]:
                if __debug__: log(f'received {exception.__class__.__name__}')
                warn('Interrupted.')
                exit_code = ExitCode.user_interrupt
            else:
                msg = str(exception[1])
                alert_fatal(f'Encountered error {exception[0].__name__}: {msg}')
                exit_code = ExitCode.exception
                if __debug__:
                    from traceback import format_exception
                    details = ''.join(format_exception(*exception))
                    logr(f'Exception: {msg}\n{details}')

        # And exit ----------------------------------------------------------------

        if __debug__: log('_'*8 + f' stopped {timestamp()} ' + '_'*8)
        if exit_code == ExitCode.user_interrupt:
            # This is a sledgehammer, but it kills everything, including ongoing
            # network get/post. I have not found a more reliable way to interrupt.
            os._exit(int(exit_code))
        else:
            exit(int(exit_code))


    def help(self, parent, args):
        '''Print detailed help information, and exit.'''
        parser = ArgumentParser(description = 'Print help for main commands',
                                usage = '%(prog)s help [name]')

        parser.add_argument('name', nargs = '?', action = 'store')
        subargs = parser.parse_args(args)
        if subargs.name is None:
            print(class_help(self))
        elif subargs.name in dir(self):
            docstring = getattr(self, subargs.name).__doc__
            print(safely_wrapped(cleandoc(docstring)))
        else:
            alert(f'Unrecognized command: "{subargs.name}"')
            print(class_help(self))


    def version(self, parent, args):
        '''Print Documentarist version information, and exit.'''
        print_version()


    def extract(self, parent, args):
        '''Process document images to extract text and other information.'''
        pass


    def config(self, parent, args):
        '''Configure Documentarist's behavior.'''
        Config(parent, args)


class Config():
    '''Set or show Documentarist's configuration.

    Documentarist stores settings in a file named "documentarist.ini", and it
    looks for the file in the following locations each time it runs, in order:

      1. the current directory
      2. the directory ~/.config/documentarist/
      3. the directory where Documentarist is installed on the system

    The "config" commands can be used to display current configuration values
    as well as set configuration values.
    '''

    def __init__(self, parent, arg_list):
        parser = ArgumentParser(description = summary_from_docstring(self),
                                formatter_class = RawDescriptionHelpFormatter,
                                add_help = False,
                                usage = '%(prog)s config [subcommand]')

        parser.add_argument('subcommand', nargs = '*',
                            help = 'Available subcommands: ' + command_list(self))

        # Skip the command name in the argument list.
        args = parser.parse_args(arg_list)
        if args.subcommand:
            command_name = args.subcommand[0]
            if hasattr(self, command_name):
                if __debug__: log(f'dispatching to {command_name}')
                getattr(self, command_name)(parser, args.subcommand[1:])
            else:
                alert_fatal(f'Unrecognized command: "{command_name}"')
                parser.print_help()
                raise CannotProceed(ExitCode.bad_arg)
        else:
            parser.print_help()


    def help(self, parent, args):
        '''Print detailed help information, and exit.'''
        parser = ArgumentParser(description = 'Print help for config commands',
                                usage = '%(prog)s config help [name]')

        parser.add_argument('name', nargs = '?', action = 'store')
        subargs = parser.parse_args(args)
        if subargs.name is None:
            print(class_help(self))
        elif subargs.name in dir(self):
            docstring = getattr(self, subargs.name).__doc__
            print(safely_wrapped(cleandoc(docstring)))
        else:
            alert(f'Unrecognized command: "{subargs.name}"')
            print(class_help(self))


    def show(self, parent, args):
        '''Print the current configuration and exit.'''
        print('invoked config show')


    def basename(self, parent, args):
        '''Set the basename for files downloaded over the network.

        When the inputs are URLs, Documentarist must download a copy of the
        image located at the network address (because it is not possible to
        write the results in the network locations represented by the URLs).
        The image at networked locations will be converted to ordinary PNG
        format for maximum compatibility with the different OCR services and
        written to files whose root names have the form "document-N.png",
        where "N" is an integer.  The URL corresponding to each document will
        be written in a file named "document-N.url" so that it is possible to
        connect each "document-N.png" to the URL it came from.

        The root name can be changed to something other than "document" using
        the "config basename" command.  For example,

            dm config basename someothername

        will change the naming pattern to "someothername-N".
        '''

        print(f'in basename got {args}')
        parser = ArgumentParser(description = 'Set the basename for downloaded files',
                                usage = '%(prog)s config basename [-h] name')

        parser.add_argument('name', action = 'store')
        subargs = parser.parse_args(args)
        print(f'result = {subargs}')


    def outputdir(self, parent, args):
        '''Set the output directory where files will be written.

        When processing images, Documentarist writes the results to new files
        that it creates either in the same directories as the original files,
        or alternatively, to a directory set by the command "config
        outputdir".  When an output directory has not been set and the input
        images are given as URLs, then the files are written to the current
        working directory instead.  The "config outputdir" command takes a
        directory path as its argument.  For example,

            dm config outputdir /tmp

        will change the output directory to /tmp.
        '''
        print('invoked config outputdir')


    def auth(self, parent, args):
        '''Configure credentials for cloud services.

        Before a given service (Google or Microsoft) can be used,
        Documentarist needs to be supplied with user credentials for
        accessing that service.  The credentials must be stored in a JSON
        file with a certain format; see the Documentarist documentation for
        details about the formats for each service.  To add a new credentials
        file, use the "config auth" option in combination with the name of a
        service and a single file path on the command line.  The name
        supplied right after the "config auth" option must be the name of a
        recognized service (Google or Microsoft), and the file argument must
        be a JSON file containing the credentials data in the required format
        for that service.  Here is an example of adding credentials for
        Google (assuming you created the JSON file as described in the docs):

          dm config auth google mygooglecreds.json

        Run dm with the "config auth" command separately to install
        credentials for each service.  Documentarist will copy the
        credentials to its configuration file and exit without doing anything
        else.
        '''
        print('invoked config auth')


def command_list(cls):
    methods = [name for name in dir(cls) if not name.startswith('_')]
    return ', '.join(f'"{name}"' for name in methods)


def summary_from_docstring(cls):
    text = safely_wrapped(cleandoc(cls.__class__.__doc__))
    text += '\n\nThe following commands are available:\n\n'

    # Find the longest name, to help compute the indentation of the 2nd column.
    longest = max(len(name) for name in dir(cls) if not name.startswith('_'))
    indent = longest + 2
    for name in [name for name in dir(cls) if not name.startswith('_')]:
        docstring = getattr(cls, name).__doc__
        if not docstring:
            continue
        first_line = docstring.split('\n')[0].rstrip('.')
        text += f'  {name}{" "*(indent - len(name))}{first_line}\n'
    return text


def class_help(cls):
    class_name = cls.__class__.__name__.lower()
    text = summary_from_docstring(cls)
    for name in [name for name in dir(cls) if not name.startswith('_')]:
        text += '\n' + class_name + ' ' + name + '\n'
        text += '~'*(len(class_name) + len(name) + 1) + '\n\n'
        method_docstring = cleandoc(getattr(cls, name).__doc__)
        text += safely_wrapped(method_docstring) + '\n'
    return text


def wrapped(string, width = get_terminal_size().columns - 4):
    return '\n'.join(wrap(string, width))


def safely_wrapped(content):
    '''Wrap the given content, being careful not to touch indented lines.'''
    # Replace leading blanks w/ special char so we can find them after wrapping.
    indents_saved = re.sub(r'^  +', '⁌', content, flags = re.MULTILINE)
    # Split the text at double newlines (=> paragraphs).
    paras = indents_saved.replace('\n\n', '⁍').split('⁍')
    # Wrap those paras that don't have leading blanks.
    paras = map(lambda s: s if s.startswith('⁌') else wrapped(s), paras)
    # Put back the leading spaces.
    paras = map(lambda s: re.sub('⁌', '  ', s), paras)
    # Put back inter-paragraph line breaks, and we're done.
    return '\n\n'.join(paras)


# Main entry point.
# .............................................................................

# The following entry point definition is for the console_scripts keyword
# option to setuptools.  The entry point for console_scripts has to be a
# function that takes zero arguments.
def console_scripts_main():
    Main(sys.argv)


# The following allows users to invoke this using "python3 -m zowie".
if __name__ == '__main__':
    Main(sys.argv)
