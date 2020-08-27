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


    def stop(self):
        pass


    def _do_preflight(self):
        '''Check the option values given by the user, and do other prep.'''

        prefix = '/' if sys.platform.startswith('win') else '-'
        hint = f'(Hint: use {prefix}h for help.)'

        if not self.input_files:
            alert_fatal(f'Must supply an input image. {hint}')
            raise CannotProceed(ExitCode.bad_arg)
        elif any(item.startswith('-') for item in self.input_files):
            alert(f'Unrecognized option in arguments. {hint}')
            raise CannotProceed(ExitCode.bad_arg)
        else:
            for file in self.input_files:
                if not path.exists(file):
                    alert_fatal(f'File not found: {file}')
                    raise CannotProceed(ExitCode.file_error)
                if not readable(file):
                    alert_fatal(f'File not readable: {file}')
                    raise CannotProceed(ExitCode.file_error)

        if self.output_file and not writable(self.output_file):
            alert_fatal(f'File not writable: {self.output_file}')
            raise CannotProceed(ExitCode.file_error)
        elif self.output_file is None:
            self.output_file = sys.stdout

        # Fixme: put classifier in separate file classifier.py
        # Have an object that has method to initialize and load model


    def _do_main_work(self):
        '''Performs the core work of this program.'''

        for file in self.input_files:
            inform(f'Analyzing file: {file}')

            # classifier should have method that takes image and returns json

            with open(self.output_file, 'w') as outfile:
                outfile.write('typed\n')

        inform('Done')
