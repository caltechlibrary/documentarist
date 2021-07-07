'''
command.py: base class for command-line command interfaces

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
from   inspect import cleandoc
import re
from   shutil import get_terminal_size
from   sidetrack import set_debug, log, logr
from   textwrap import wrap, fill, dedent

from   common.exit_codes import ExitCode


# Exported classes.
# .............................................................................

# Command is designed to work both for the top-level command parser created
# by the Main class in __main__.py and for subcommands.  All command parser
# classes should all inherit from this class.  However, Main must NOT call
# this __init__() function in its own __init__(), because Main adds its own
# command arguments explicitly and is set up a little differently.  Only
# subcommand classes should invoke Command's init, using super().__init__().

class Command():
    '''Base class for Documentarist command-line command parsers.'''

    _name = ''

    def __init__(self, name, arg_list):
        '''Create the parser, parse the arguments, and dispatch commands.'''
        self._name = name

        usage = f'%(prog)s {name}{" " if name else ""}[subcommand]'
        parser = ArgumentParser(description = docstring_summary(self, name),
                                formatter_class = RawDescriptionHelpFormatter,
                                add_help = False, usage = usage)

        parser.add_argument('subcommand', nargs = '*',
                            help = 'Available subcommands: ' + command_list(self))

        # Skip the command name in the argument list.
        args = parser.parse_args(arg_list)
        if args.subcommand:
            command_name = args.subcommand[0]
            if hasattr(self, command_name):
                log(f'dispatching to {command_name}')
                getattr(self, command_name)(args.subcommand[1:])
            else:
                alert_fatal(f'Unrecognized command: "{command_name}"')
                parser.print_help()
                raise CannotProceed(ExitCode.bad_arg)
        else:
            parser.print_help()


    def help(self, args):
        '''Print detailed help information, and exit.'''
        usage = '%(prog)s {self._name}{" " if self._name else ""}help [name]'
        parser = ArgumentParser(description = 'Print help', usage = usage)
        parser.add_argument('name', nargs = '?', action = 'store')
        subargs = parser.parse_args(args)
        if subargs.name is None:
            print(class_help(self, self._name))
        elif subargs.name in dir(self):
            docstring = getattr(self, subargs.name).__doc__
            print(safely_wrapped(cleandoc(docstring)))
        else:
            alert(f'Unrecognized command: "{subargs.name}"')
            print(class_help(self, self._name))


# Utility functions.
# .............................................................................

def command_list(cls):
    methods = [name for name in dir(cls) if not name.startswith('_')]
    return ', '.join(f'"{name}"' for name in methods)


def docstring_summary(cls, cmd_name = ''):
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


def class_help(cls, cmd_name = ""):
    text = docstring_summary(cls)
    for name in [name for name in dir(cls) if not name.startswith('_')]:
        if cmd_name:
            text += '\n' + cmd_name + ' ' + name + '\n'
            text += '~'*(len(cmd_name) + len(name) + 1) + '\n\n'
        else:
            text += '\n' + name + '\n'
            text += '~'*(len(name) + 1) + '\n\n'
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
