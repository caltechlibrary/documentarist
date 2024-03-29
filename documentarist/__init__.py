'''
Documentarist: analyze scanned documents in Caltech archives

Authors
-------

Michael Hucka <mhucka@caltech.edu> -- Caltech Library

Copyright
---------

Copyright (c) 2020 by the California Institute of Technology.  This code
is open-source software released under a 3-clause BSD license.  Please see the
file "LICENSE" for more information.
'''

# Package metadata ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#  ╭────────────────────── Notice ── Notice ── Notice ─────────────────────╮
#  |    The following values are automatically updated at every release    |
#  |    by the Makefile. Manual changes to these values will be lost.      |
#  ╰────────────────────── Notice ── Notice ── Notice ─────────────────────╯

__version__     = '0.0.1'
__description__ = 'Extract text and other info from scanned documents'
__url__         = 'https://github.com/caltechlibrary/documentarist'
__author__      = 'Michael Hucka'
__email__       = 'mhucka@caltech.edu'
__license__     = 'BSD 3-clause'


# Miscellaneous utilities.
# .............................................................................

def print_version():
    print(f'Documentarist version {__version__}')
    print(f'Authors: {__author__}')
    print(f'URL: {__url__}')
    print(f'License: {__license__}')


# Miscellaneous constants.
# .............................................................................

# Output format for the files we write.
_OUTPUT_FORMAT = 'png'
_OUTPUT_EXT = '.png'
