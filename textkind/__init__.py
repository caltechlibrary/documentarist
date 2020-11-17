'''
textform: report whether image contains printed or handwritten text

This module implements a classifier that takes an image (usually a region
extracted from a larger image) believed to contain text, and evaluates whether
the text appears to be printed or handwritten in form.


Authors
-------

Michael Hucka <mhucka@caltech.edu> -- Caltech Library

Copyright
---------

Copyright (c) 2020 by the California Institute of Technology.  This code
is open-source software released under a 3-clause BSD license.  Please see the
file "LICENSE" for more information.
'''

from .classify import TextKindClassifier
