'''
log.py

This is basically a modified version of my Sidetrack package code from
https://github.com/caltechlibrary/sidetrack but changed to use Loguru.  Loguru
interacts more conventionally with the Python logging package, plus offers some
features like being able to change configuration using environment variables.
I wasn't prepared to rewrite Sidetrack at this time, because other things
depend on it, so instead I wrote this.

Authors
-------

Michael Hucka <mhucka@caltech.edu> -- Caltech Library

Copyright
---------

Copyright (c) 2020-2022 by the California Institute of Technology.  This code
is open-source software released under a 3-clause BSD license.  Please see the
file "LICENSE" for more information.
'''

from   inspect import currentframe
from   loguru import logger
from   os import path
import sys


# Constants
# .............................................................................

# {file}:<c>{func}</c>:{lineno} <w>' + msg + '</w>'

FORMAT = ('<d>{thread.name}</d> {extra[package]} '
          '{extra[filename]}:<b>{extra[func]}</b>:<c>{extra[lineno]}</c> '
          '<w>{message}</w>')


# Module code.
# .............................................................................

def enable_logging(dest = '-'):
    '''Turns on debug logging and use the given destination.

    Optional argument 'dest' directs the output to the given destination.
    The value can be a file path, or a single dash ('-') to indicate the
    standard error stream (i.e., sys.stderr).  The default destination is the
    standard error stream.  For simplicity, only one destination is allowed at
    given a time; calling this function multiple times with different
    destinations simply switches the destination to the latest one.
    '''

    # Set a marker that logging is enabled.
    setattr(sys.modules[__package__], '_logging', True)

    logger.remove()
    # We treat empty dest values as meaning "the default output".
    if dest in ['-', '', 'stderr', None] or type(dest) == type(sys.stderr):
        logger.add(sys.stderr, level = 'TRACE', format = FORMAT)
    else:
        logger.add(dest, level = 'TRACE', format = FORMAT)


# You might think that the way to get the current caller info when the log
# function is called would be to use logger.findCaller(). I tried that, and it
# produced very different information, even when using various values of
# stacklevel as the argument. The code below instead uses the Python inspect
# module to get the correct stack frame at run time.

def log(msg):
    '''Logs a debug message in raw form, without further interpretation.

    The text string 'msg' is taken as-is; unlike the function logf(...), this
    function does not apply str.format to the string.
    '''
    if __debug__:
        if getattr(sys.modules[__package__], '_logging', False):
            __write_log(msg, currentframe().f_back)


def loglist(msg_list):
    '''Logs a list of strings as individual debug message.

    The text strings in the list are taken as-is.  This is a shorthand for
    doing roughly the following:

        for msg in msg_list:
            log(msg)
    '''
    if __debug__:
        if getattr(sys.modules[__package__], '_logging', False):
            for msg in msg_list:
                __write_log(msg, currentframe().f_back)


# Internal helper functions.
# .............................................................................

def __write_log(msg, frame):
    func     = frame.f_code.co_name
    lineno   = frame.f_lineno
    package  = frame.f_globals['__package__']
    filename = path.basename(frame.f_code.co_filename)
    logger.debug(msg, package = package, filename = filename,
                 lineno = lineno, func = func)
