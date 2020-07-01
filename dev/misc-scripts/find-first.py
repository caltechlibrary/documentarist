#!/usr/bin/env python3

import os
import time

for n in range(0, 11177):
    url = 'https://digital.archives.caltech.edu/islandora/object/hale:{:05d}'.format(n)
    stream = os.popen('curl -s ' + url)
    output = stream.read()
    if 'Page not found' not in output:
        print(url)
    else:
        print(n)
    time.sleep(0.25)
