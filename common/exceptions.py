'''
exceptions.py: exceptions defined by textform

Authors
-------

Michael Hucka <mhucka@caltech.edu> -- Caltech Library

Copyright
---------

Copyright (c) 2020 by the California Institute of Technology.  This code is
open-source software released under a 3-clause BSD license.  Please see the
file "LICENSE" for more information.
'''

class CannotProceed(Exception):
    '''A recognizable condition caused an early exit from the program.'''
    pass

class UserCancelled(Exception):
    '''The user elected to cancel/quit the program.'''
    pass

class CorruptedContent(Exception):
    '''Content corruption has been detected.'''
    pass

class InternalError(Exception):
    '''Unrecoverable problem involving textform itself.'''
    pass
