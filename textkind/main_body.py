from   os import path
import sys

import textkind

from   common.data_utils import DATE_FORMAT, timestamp
from   common.debug import log
from   common.exceptions import *
from   common.exit_codes import ExitCode
from   common.file_utils import readable, writable
from   common.ui import UI, inform, warn, alert, alert_fatal


class MainBody():
    '''Main body of TextKind.'''

    def __init__(self, **kwargs):
        # Assign parameters to self to make them available within this object.
        for key, value in kwargs.items():
            setattr(self, key, value)

        # We expose attribute "exception" that callers can use to find out if
        # the thread finished normally or with an exception.
        self.exception = None


    def run(self):
        '''Run the main body, using user interface object "ui".'''

        if __debug__: log('running MainBody')
        self._do_preflight()
        self._do_main_work()
        if __debug__: log('finished MainBody')


    def _do_preflight(self):
        '''Check the option values given by the user, and do other prep.'''

        prefix = '/' if sys.platform.startswith('win') else '-'
        hint = f'(Hint: use {prefix}h for help.)'

        if not self.files:
            alert_fatal(f'Must supply an input image. {hint}')
            raise CannotProceed(ExitCode.bad_arg)
        elif any(item.startswith('-') for item in self.files):
            alert(f'Unrecognized option in arguments. {hint}')
            raise CannotProceed(ExitCode.bad_arg)
        else:
            for file in self.files:
                if not path.exists(file):
                    alert_fatal(f'File not found: {file}')
                    raise CannotProceed(ExitCode.file_error)
                if not readable(file):
                    alert_fatal(f'File not readable: {file}')
                    raise CannotProceed(ExitCode.file_error)

        if self.output and not writable(self.output):
            alert_fatal(f'File not writable: {self.output}')
            raise CannotProceed(ExitCode.file_error)
        elif self.output is None:
            self.output = sys.stdout


    def _do_main_work(self):
        '''Performs the core work of this program.'''
        pass
