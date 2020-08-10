'''
exit_codes.py: define exit codes for program return values

Authors
-------

Michael Hucka <mhucka@caltech.edu> -- Caltech Library

Copyright
---------

Copyright (c) 2020 by the California Institute of Technology.  This code is
open-source software released under a 3-clause BSD license.  Please see the
file "LICENSE" for more information.
'''

from aenum import Enum, unique

@unique
class ExitCode(Enum):
    success        = 0, 'success -- program completed normally'
    no_net         = 1, 'no network detected'
    bad_arg        = 2, 'encountered a bad or missing value for an option'
    file_error     = 3, 'encountered a problem with a file'
    user_interrupt = 4, 'the user interrupted execution'
    exception      = 5, 'an exception or fatal error occurred'
