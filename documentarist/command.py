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
from   functools import partial
from   inspect import cleandoc
import re
from   shutil import get_terminal_size
from   textwrap import wrap, fill, dedent

from   documentarist.exceptions import CannotProceed
from   documentarist.exit_codes import ExitCode
from   documentarist.log import log
from   documentarist.ui import UI, inform, warn, alert


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

    def __init__(self, name):
        '''Create the parser, parse the arguments, and dispatch commands.'''
        # Set up a parser to intercept the command name and help requests.
        usage = f'%(prog)s {name}{" " if name else ""}[subcommand]'
        parser = ArgumentParser(description = docstring_summary(self, name),
                                formatter_class = RawDescriptionHelpFormatter,
                                add_help = False, usage = usage)
        parser.add_argument('subcommand', nargs = '?', help = available_commands(self))
        self._parser = parser
        self._command = name


    def _invoke_with(self, arg_list):
        '''Invoke this command's parser on the arguments in arg_list.'''
        # First check if the command is help. If so, handle it, and we're done.
        if not arg_list or arg_list[0] == 'help':
            self._parser.print_help()
            return

        # Separate the command from its arguments & invoke the corresp. method
        command, args = self._parser.parse_known_args(arg_list)
        if command.subcommand:
            command_name = command.subcommand
            if hasattr(self, command_name):
                log(f'dispatching to {command_name}')
                getattr(self, command_name)(args)
            else:
                alert(f'Unrecognized command: "{command_name}"')
                parser.print_help()
                raise CannotProceed(ExitCode.bad_arg)


    def help(self, args):
        '''Print detailed help information, and exit.'''
        usage = '%(prog)s {self._name}{" " if self._name else ""}help [name]'
        parser = ArgumentParser(description = 'Print help', usage = usage)
        parser.add_argument('name', nargs = '?', action = 'store')
        subargs = parser.parse_args(args)
        log('printing help text')
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
    return [name for name in dir(cls) if not name.startswith('_')]


def available_commands(cls, conjunction = 'or'):
    '''Return a string with a comma-separated list of commands on this class.

    A conjunction is added before the final command. By default, "or" is used,
    leading to a string of the form "foo, bar, or baz". The optional argument
    'conjunction' can be used to change this. Setting the value to an empty
    string will result in no conjunction being added.
    '''
    commands = command_list(cls)
    if len(commands) > 1:
        text_list = commands[0:-1] + [conjunction + ' ' + commands[-1]]
    else:
        text_list = [commands[0]]
    # The strip() removes extra whitespace that results if conjunction = ''.
    return ', '.join(f'{item.strip()}' for item in text_list)


def docstring_summary(cls, cmd_name = ''):
    text = safely_wrapped(cleandoc(cls.__class__.__doc__))
    text += '\n\nThe following commands are available:\n\n'

    # Find the longest name, to help compute the indentation of the 2nd column.
    commands = command_list(cls)
    longest = max(len(name) for name in commands)
    indent = longest + 2
    for name in commands:
        docstring = getattr(cls, name).__doc__
        if not docstring:
            continue
        first_line = docstring.split('\n')[0].rstrip('.')
        text += f'  {name}{" "*(indent - len(name))}{first_line}\n'
    return text


def method_help(method):
    return safely_wrapped(cleandoc(method.__doc__))


def class_help(cls, cmd_name = ""):
    text = docstring_summary(cls)
    for name in command_list(cls):
        if cmd_name:
            text += '\n' + cmd_name + ' ' + name + '\n'
            text += '~'*(len(cmd_name) + len(name) + 1) + '\n\n'
        else:
            text += '\n' + name + '\n'
            text += '~'*len(name) + '\n\n'
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


def method_parser(method_function, summary, **kwargs):
    return ArgumentParser(description = method_help(method_function),
                          usage = '%(prog)s ' + summary,
                          formatter_class = RawDescriptionHelpFormatter,
                          add_help = False, **kwargs)
