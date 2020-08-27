'''
__main__: main command-line interface to TextKind

Authors
-------

Michael Hucka <mhucka@caltech.edu> -- Caltech Library

Copyright
---------

Copyright (c) 2020 by the California Institute of Technology.  This code
is open-source software released under a 3-clause BSD license.  Please see the
file "LICENSE" for more information.
'''

import os
from   os import path
import plac
import sys

sys.path.append('../common')

import textkind
from   .main_body import MainBody

from   common.data_utils import DATE_FORMAT, timestamp
from   common.debug import set_debug, log
from   common.exceptions import *
from   common.exit_codes import ExitCode
from   common.file_utils import readable
from   common.interruptions import interrupt, interrupted
from   common.ui import UI, inform, warn, alert, alert_fatal


# Main program.
# ......................................................................

@plac.annotations(
    extended = ('produce extended results (as JSON data)',            'flag',   'e'),
    output   = ('write output to destination "O" (default: console)', 'option', 'o'),
    debug    = ('write detailed trace to "OUT" ("-" means console)',  'option', '@'),
    files    = 'file(s)',
)

def main(extended = False, output = 'O', debug = 'OUT', *files):
    '''Report if an image contains printed or handwritten text.

The results of the analysis are printed to the terminal's standard output
stream by default.  If given the option -o (or /o on Windows), the results
are instead written to the file indicated as the value of the option.  For
example, "-o results.txt" will cause the analysis results to be written,
one line per file, in "results.txt".

The output by default is simply a classification of the content, given as
one of the following words:

   handwritten -- the text is judged to be handwritten
   printed     -- the text is judged to be printed
   none        -- no text could be found

If the option -e (or /e on Windows) is given, then the output will also
include percentages indicating the strength of the assessment.
    '''

    # Set up debugging as soon as possible, if requested ----------------------

    debugging = debug != 'OUT'
    if debugging:
        set_debug(True, debug)
        from rich.traceback import install as install_rich_traceback
        install_rich_traceback()
        import faulthandler
        faulthandler.enable()

    # Do the real work --------------------------------------------------------

    if __debug__: log('='*8 + f' started {timestamp()} ' + '='*8)
    ui = body = exception = None
    try:
        ui = UI('TextKind', 'report whether text in image is handwritten or printed')
        body = MainBody(files = files,
                        output = None if output == 'O' else output,
                        extended = extended)
        ui.start()
        body.run()
        exception = body.exception
    except (KeyboardInterrupt, UserCancelled) as ex:
        # In Python, the main thread (i.e., this one) is the one that gets ^C.
        alert('Quit received; shutting down ...')
        interrupt()
        body.stop()
        exception = sys.exc_info()
    except Exception as ex:
        # MainBody exceptions are caught in its thread, so this is something else.
        exception = sys.exc_info()

    # Try to deal with exceptions gracefully ----------------------------------

    exit_code = ExitCode.success
    if exception:
        if type(exception[1]) == CannotProceed:
            exit_code = exception[1].args[0]
        elif type(exception[1]) in [KeyboardInterrupt, UserCancelled]:
            if __debug__: log(f'received {exception[1].__class__.__name__}')
            exit_code = ExitCode.user_interrupt
        else:
            exit_code = ExitCode.exception
            from traceback import format_exception
            ex_type = str(exception[1])
            details = ''.join(format_exception(*exception))
            if __debug__: log(f'Exception: {ex_type}\n{details}')
            if debugging:
                import pdb; pdb.set_trace()
    if __debug__: log('_'*8 + f' stopped {timestamp()} ' + '_'*8)
    exit(exit_code.value[0])


# Main entry point.
# ......................................................................

# On windows, we want plac to use slash intead of hyphen for cmd-line options.
if sys.platform.startswith('win'):
    main.prefix_chars = '/'

# The following allows users to invoke this using "python3 -m textkind".
if __name__ == '__main__':
    plac.call(main)


# For Emacs users
# ......................................................................
# Local Variables:
# mode: python
# python-indent-offset: 4
# End:
