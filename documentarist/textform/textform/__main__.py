'''
__main__: main command-line interface to TextForm

Authors
-------

Michael Hucka <mhucka@caltech.edu> -- Caltech Library

Copyright
---------

Copyright (c) 2020 by the California Institute of Technology.  This code
is open-source software released under a 3-clause BSD license.  Please see the
file "LICENSE" for more information.
'''

from   datetime import datetime as dt
import os
from   os import path
from   PIL import Image, ImageFile
import plac
from   rich.traceback import install as install_rich_traceback
import sys

import textform
from   .data_helpers import DATE_FORMAT
from   .debug import set_debug, log
from   .exceptions import *
from   .exit_codes import ExitCode
from   .files import readable


# Main program.
# ......................................................................

@plac.annotations(
    image = ('input file (an image)',                             'option', 'i'),
    debug = ('write detailed trace to "OUT" ("-" means console)', 'option', '@'),
)

def main(image = 'I', debug = 'OUT'):
    # Preprocess arguments and handle early exits -----------------------------

    debugging = debug != 'OUT'
    if debugging:
        set_debug(True, debug)
        install_rich_traceback()
        import faulthandler
        faulthandler.enable()

    if image == 'I':
        exit('Must supply an input image')
    elif not readable(image):
        exit('File unreadable: {image}')

    # Do the real work --------------------------------------------------------

    if __debug__: log('='*8 + ' started {}' + '='*8, dt.now().strftime(DATE_FORMAT))
    exception = None
    try:
        pass
    except Exception as ex:
        # MainBody exceptions are caught in its thread, so this is something else.
        exception = sys.exc_info()

    # Try to deal with exceptions gracefully ----------------------------------

    exit_code = ExitCode.success
    if exception:
        if type(exception[1]) == CannotProceed:
            exit_code = exception[1].args[0]
        elif type(exception[1]) in [KeyboardInterrupt, UserCancelled]:
            if __debug__: log('received {}', exception[1].__class__.__name__)
            exit_code = ExitCode.user_interrupt
        else:
            exit_code = ExitCode.exception
            from traceback import format_exception
            ex_type = str(exception[1])
            details = ''.join(format_exception(*exception))
            if __debug__: log('Exception: {}\n{}', ex_type, details)
            if debugging:
                import pdb; pdb.set_trace()
    if __debug__: log('exiting')
    exit(exit_code.value[0])


# Main entry point.
# ......................................................................

# On windows, we want plac to use slash intead of hyphen for cmd-line options.
if sys.platform.startswith('win'):
    main.prefix_chars = '/'

# The following allows users to invoke this using "python3 -m eprints2archives".
if __name__ == '__main__':
    plac.call(main)


# For Emacs users
# ......................................................................
# Local Variables:
# mode: python
# python-indent-offset: 4
# End:
