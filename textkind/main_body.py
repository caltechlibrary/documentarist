'''
main_body.py: implement central logic and control of TextKind

Authors
-------

Michael Hucka <mhucka@caltech.edu> -- Caltech Library

Copyright
---------

Copyright (c) 2020 by the California Institute of Technology.  This code
is open-source software released under a 3-clause BSD license.  Please see the
file "LICENSE" for more information.
'''

from   commonpy.data_utils import DATE_FORMAT, timestamp, plural
from   commonpy.file_utils import readable, writable
from   humanize import intcomma
import json
from   os import path
from   sidetrack import log
import sys
from   typing import Generator

import textkind

from   common.exceptions import *
from   common.exit_codes import ExitCode
from   common.ui import UI, inform, warn, alert, alert_fatal

from   .classify import TextKindClassifier


# Class definitions.
# .............................................................................

class MainBody():
    '''Main body of TextKind.'''

    def __init__(self, **kwargs):
        '''Initialize internal state.'''

        # Assign parameters to self to make them available within this object.
        for key, value in kwargs.items():
            setattr(self, key, value)

        # We expose attribute "exception" that callers can use to find out if
        # the thread finished normally or with an exception.
        self.exception = None


    def run(self):
        '''Run the main body.'''

        if __debug__: log('running MainBody')
        try:
            self._do_preflight()
            self._do_main_work()
        except Exception as ex:
            if __debug__: log(f'exception in main body: {str(ex)}')
            self.exception = sys.exc_info()
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
            alert_fatal(f'Unrecognized option in arguments. {hint}')
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


    def _do_main_work(self):
        '''Performs the core work of this program.'''

        num_files = len(self.input_files)
        inform(f'Will analyze {intcomma(num_files)} {plural("image", num_files)}.')

        classifier = TextKindClassifier()
        results = classifier.classify(self.input_files)

        # The classify.py code in seutrm's printed_vs_handwritten normalizes
        # the scores, but I don't think it's necessary b/c the larger value of
        # 'printed' and 'handwritten' will always produce the higher score.

        if self.output_file == sys.stdout:
            if isinstance(results, Generator):
                for item in results:
                    self._inform_of_result(item)
            else:
                self._inform_of_result(results)
        else:
            # JSON format can't really be written incrementally, so we have to
            # generate all the results first.
            results = list(results)
            with open(self.output_file, 'w') as outfile:
                json.dump(results, outfile, indent = 4)
            inform(f'Results writtent to {self.output_file}')


    def _inform_of_result(self, item):
        if self.extended:
            details = f" (handwritten: {item['handwritten']:.4f}, printed: {item['printed']:.4f})"
        else:
            details = ''
        inform(f'{item["file"]}: {item["text kind"]} {details}', force = True)
