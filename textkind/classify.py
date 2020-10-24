'''
classify.py: interface to classifier engine

Authors
-------

Michael Hucka <mhucka@caltech.edu> -- Caltech Library

Copyright
---------

Copyright (c) 2020 by the California Institute of Technology.  This code
is open-source software released under a 3-clause BSD license.  Please see the
file "LICENSE" for more information.
'''

from   math import exp
from   os import path
import pickle
from   PIL import Image
from   sidetrack import log
import sys

sys.path.append('../common')

from   common.ui import UI, inform, warn, alert, alert_fatal
from   common.exceptions import *

sys.path.append('printed_vs_handwritten')

from   printed_vs_handwritten import ocrd_typegroups_classifier
from   printed_vs_handwritten.ocrd_typegroups_classifier.typegroups_classifier import TypegroupsClassifier


# Constants.
# .............................................................................

_TGC_MODEL_FILE = 'classifier.tgc'


# Class definitions.
# .............................................................................

class TextKindClassifier():

    def __init__(self):
        pickled_class = path.join('printed_vs_handwritten',
                                  'ocrd_typegroups_classifier',
                                  'models', 'classifier.tgc')
        self._classifier = TypegroupsClassifier.load(pickled_class)


    def classify(self, file):
        inform(f'Analyzing {file}')
        # The classifier has a hardwired assumption that the inputs have
        # 3 channels.  If we get a grayscale image, we have to convert it.
        with Image.open(file, 'r').convert('RGB') as img:
            data = self._classifier.classify(img, 75, 64, False)
            kind = 'printed' if data['printed'] > data['handwritten'] else 'handwritten'
            return {'file': file, 'text kind': kind,
                    'printed': data['printed'],
                    'handwritten': data['handwritten']}
