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

from   boltons.debugutils import pdb_on_signal
from   commonpy.data_utils import DATE_FORMAT, timestamp
from   commonpy.file_utils import readable
from   commonpy.interrupt import config_interrupt
from   commonpy.system_utils import system_profile
import os
from   os import path
import plac
from   sidetrack import set_debug, log, logr
import signal
import sys

sys.path.append('../common')

import textkind
from   .main_body import MainBody

from   common.exceptions import *
from   common.exit_codes import ExitCode
from   common.interruptions import interrupt, interrupted
from   common.ui import UI, inform, warn, alert, alert_fatal


# Main program.
# ......................................................................

@plac.annotations(
    extended = ('produce extended results (as JSON data)',             'flag',   'e'),
    output   = ('write output to destination "O" (default: console)',  'option', 'o'),
    quiet    = ('do not print informational messages while working',   'flag',   'q'),
    no_color = ('do not color-code terminal output',                   'flag',   'C'),
    debug    = ('write detailed trace to "OUT" ("-" means console)',   'option', '@'),
    files    = 'file(s)',
)

def main(extended = False, output = 'O', quiet = False,
         no_color = False, debug = 'OUT', *files):
    '''Report if an image contains printed or handwritten text.

The results of the analysis are printed to the terminal's standard output
stream by default.  If given the option -o (or /o on Windows), the results
are instead written to the file indicated as the value of the option.  For
example, "-o results.json" will cause the analysis results to be written
to file "results.json".

The output by default is simply a classification of the content, given as
one of the following words:

   handwritten -- the text is judged to be handwritten
   printed     -- the text is judged to be printed
   none        -- no text could be found

If the option -e (or /e on Windows) is given, then the output will also
include percentages indicating the strength of the assessment.
'''
    # Set up debug logging as soon as possible, if requested ------------------

    if debug != 'OUT':
        set_debug(True, debug, extra = "%(threadName)s")
        import faulthandler
        faulthandler.enable()
        if not sys.platform.startswith('win'):
            # Even with a different signal, I can't get this to work on Win.
            pdb_on_signal(signal.SIGUSR1)

    # Do the real work --------------------------------------------------------

    if __debug__: log('='*8 + f' started {timestamp()} ' + '='*8)
    if __debug__: log('system details:\n{}', system_profile())
    ui = body = exception = None
    try:
        ui = UI('TextKind', 'report whether text in image is handwritten or printed',
                use_color = not no_color, be_quiet = quiet)
        ui.start()
        body = MainBody(input_files = files, extended = extended,
                        output_file = None if output == 'O' else output)
        config_interrupt(body.stop, UserCancelled(ExitCode.user_interrupt))
        body.run()
        exception = body.exception
    except Exception as ex:
        # MainBody exceptions are caught in its thread, so this is something else.
        exception = sys.exc_info()

    # Try to deal with exceptions gracefully ----------------------------------

    exit_code = ExitCode.success
    if exception:
        if exception[0] == CannotProceed:
            exit_code = exception[1].args[0]
        elif exception[0] in [KeyboardInterrupt, UserCancelled]:
            if __debug__: log(f'received {exception[0].__name__}')
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
    else:
        inform('Done.')

    # And exit ----------------------------------------------------------------

    if __debug__: log('_'*8 + f' stopped {timestamp()} ' + '_'*8)
    if __debug__: log(f'exiting with exit code {exit_code}')
    exit(int(exit_code))


# Main entry point.
# ......................................................................

# On windows, we want plac to use slash intead of hyphen for cmd-line options.
if sys.platform.startswith('win'):
    main.prefix_chars = '/'

# The following allows users to invoke this using "python3 -m textkind".
if __name__ == '__main__':
    plac.call(main)
