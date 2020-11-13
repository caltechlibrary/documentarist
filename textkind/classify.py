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
from   sidetrack import log, logr
import sys

sys.path.append('../common')

from   common.ui import UI, inform, warn, alert, alert_fatal
from   common.exceptions import *

this_directory = path.dirname(path.abspath(__file__))
sys.path.append(path.join(this_directory, 'printed_vs_handwritten'))

from   printed_vs_handwritten import ocrd_typegroups_classifier
from   printed_vs_handwritten.ocrd_typegroups_classifier.typegroups_classifier import TypegroupsClassifier


# Constants.
# .............................................................................

_TGC_MODEL_FILE = 'classifier.tgc'


# Class definitions.
# .............................................................................

class TextKindClassifier():

    def __init__(self):
        pickled_class = path.join(this_directory,
                                  'printed_vs_handwritten',
                                  'ocrd_typegroups_classifier',
                                  'models', 'classifier.tgc')
        self._classifier = TypegroupsClassifier.load(pickled_class)


    def classify(self, inputs):
        '''Analyzes images for handwritten or printed text.

        If given a single image or file, analyzes it and returns a single
        result.  If given a list, returns an iterator over the results of
        analyzing each individual image or file.
        '''

        if isinstance(inputs, (list, tuple)):
            return self.classify_list(inputs)
        elif isinstance(inputs, Image.Image):
            return self.classify_image(inputs)
        else:
            return self.classify_file(inputs)


    def classify_list(self, inputs):
        for item in inputs:
            yield self.classify(item)


    def classify_file(self, file):
        if __debug__: log(f'classifying file {file}')
        with Image.open(file, 'r') as image:
            return self.classify_image(image)


    def classify_image(self, image):
        file = image.filename if hasattr(image, 'filename') else None
        if __debug__: log(f'classifying image {image} (from {file})')
        # The classifier has a hardwired assumption that the inputs have
        # 3 channels.  If we get a grayscale image, we have to convert it.
        image = image.convert('RGB')
        data = self._classifier.classify(image, 75, 64, False)
        kind = 'printed' if data['printed'] > data['handwritten'] else 'handwritten'
        results = {'text kind': kind,
                   'printed': data['printed'],
                   'handwritten': data['handwritten']}
        if file:
            results['file'] = file
        if __debug__: log('image classification results = {}', results)
        return results
