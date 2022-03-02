'''
ui.py: user interface functions for Documentarist

This is mostly based on my package Bun.  I wanted to experiment with some
changes without having to modify Bun itself (which is used by other software).

Authors
-------

Michael Hucka <mhucka@caltech.edu> -- Caltech Library

Copyright
---------

Copyright (c) 2020-2022 by the California Institute of Technology.  This code
is open-source software released under a 3-clause BSD license.  Please see the
file "LICENSE" for more information.
'''
from   commonpy.string_utils import antiformat
from   queue import Queue
from   rich import box
from   rich.box import HEAVY, DOUBLE_EDGE, ASCII
from   rich.console import Console
from   rich.panel import Panel
from   rich.style import Style
from   rich.theme import Theme
import shutil
import sys

from   documentarist.log import log


# Constants.
# .............................................................................

# I haven't found a reasonable way to switch colors based on whether the
# user's terminal background color is dark or light -- there seems to be no
# universal way to get that information for every terminal emulator, due to
# how they are implemented.  So, the following is an attempt to pick a single
# set of colors that will work on both dark and bright color backgrounds.
# The switch on Windows-versus-other is because when testing on Windows, I
# get noticeably different color shades and brightness if I use cmd.exe vs
# Cmder, and those are different *again* from my iTerm2 defaults on macOS.
# So here I'm trying to find some compromise that will work in most cases.

if sys.platform.startswith('win'):
    # Note: Microsoft's Terminal (and I guess some others on Windows) can't show
    # bold (2021-06-29). C.f. https://github.com/microsoft/terminal/issues/109
    # The following style still uses bold in case that changes in the future.
    _THEME = Theme({
        'info'        : 'green3',
        'warn'        : 'orange1',
        'warning'     : 'orange1',
        'alert'       : 'red',
        'alert_fatal' : 'bold red',
        'fatal'       : 'bold red',
        'standout'    : 'bold dark_sea_green2',
        'banner'      : 'green3',
    })
else:
    _THEME = Theme({
        'info'        : 'dark_sea_green4',
        'warn'        : 'orange1',
        'warning'     : 'orange1',
        'alert'       : 'red',
        'alert_fatal' : 'bold red',
        'fatal'       : 'bold red',
        'standout'    : 'bold chartreuse3',
        'banner'      : 'dark_sea_green4',
    })


# Exported classes.
# .............................................................................
# This class implements a singleton instance, and provides a method to access
# that instance.

class UI():
    '''Wrapper class for the user interface.'''

    __instance = None

    def __new__(cls, name, subtitle = None, show_banner = True,
                use_color = True, be_quiet = False):
        if cls.__instance is None:
            log('creating UI object')
            cls.__instance = super(UI, cls).__new__(cls)
            cls.__instance._started = False

            # If another thread was eager to send messages before we finished
            # initialization, msgs will get queued up on this internal queue.
            cls.__instance._queue = Queue()

            # Initialize output configuration.
            color = "auto" if use_color else None
            cls.__instance._console = Console(theme = _THEME, color_system = color)

            if show_banner and not be_quiet:
                cls.__instance.print_banner(name, subtitle, use_color)

        return cls.__instance


    def _print_banner(name, subtitle, use_color):
        # We need the plain_text version in any case, to calculate length.
        subtitle_part = f': {subtitle}' if subtitle else ''
        plain_text = f'Welcome to {name}{subtitle_part}'
        fancy_text = f'Welcome to [standout]{name}[/]{subtitle_part}'
        text = fancy_text if use_color else plain_text
        terminal_width = shutil.get_terminal_size().columns or 80
        odd_adjustment = 0 if (terminal_width % 2 == 0) else 2
        padding = (terminal_width - len(plain_text) - 2 - odd_adjustment) // 2
        # Queueing up this message now will make it the 1st thing printed.
        box_style = DOUBLE_EDGE if use_color else ASCII
        self._print_or_queue(Panel(text, style = 'banner', box = box_style,
                                   padding = (0, padding)), style = 'info')


    @classmethod
    def instance(cls):
        return cls.__instance


    def start(self):
        '''Start the user interface.'''
        log('starting UI')
        while not self._queue.empty():
            (text, style) = self._queue.get()
            self._console.print(text, style = style, highlight = False)
            sys.stdout.flush()
        self._started = True


    def stop(self):
        '''Stop the user interface.'''
        pass


    def _print_or_queue(self, text, style):
        if self._started:
            log(antiformat(text))
            self._console.print(text, style = style, highlight = False)
        else:
            log(f'queueing message "{antiformat(text)}"')
            self._queue.put((text, style))


    def inform(self, text, *args, **kwargs):
        '''Print an informational message.

        By default, the message will not be printed if the UI has been given
        the "quiet" flag.  However, if this method is passed the keyword
        argument "force" with a value of True, then the "quiet" setting will
        be overridden and the message printed anyway.'''
        if ('force' in kwargs and kwargs['force']) or not self._be_quiet:
            self._print_or_queue(text.format(*args), 'info')
        else:
            log(text, *args)


    def warn(self, text, *args):
        '''Print a nonfatal, noncritical warning message.'''
        self._print_or_queue(text.format(*args), style = 'warn')


    def alert(self, text, *args):
        '''Print a message reporting an error.'''
        self._print_or_queue(text.format(*args), style = 'alert')


# Exported functions.
# .............................................................................
# These methods get an instance of the UI by themselves and do not require
# callers to do it.  They are meant to be used largely like basic functions
# such as "print()" are used in Python.

def inform(text, *args, **kwargs):
    '''Inform the user about something.

    Argument 'text' can contain string format placeholders such as "{}", and
    the additional arguments in args are values to use in those placeholders.

    By default, the message will not be printed if the UI has been given
    the "quiet" flag.  However, if this method is passed the keyword
    argument "force" with a value of True, then the "quiet" setting will
    be overridden and the message printed anyway.
    '''
    ui = UI.instance()
    ui.inform(text, *args, **kwargs)


def warn(text, *args):
    '''Warn the user that something is not right.

    This should be used in situations where the problem is not fatal nor will
    prevent continued execution.  (For problems that prevent continued
    execution, use the alert(...) method instead.)
    '''
    ui = UI.instance()
    ui.warn(text, *args)


def alert(text, *args):
    '''Alert the user to an error.

    This should be used in situations where there is a problem that will
    prevent normal execution.
    '''
    ui = UI.instance()
    ui.alert(text, *args)
