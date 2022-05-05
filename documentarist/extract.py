'''
extract.py: extract text from an image
'''

from   documentarist.command import Command, docstring_summary
from   documentarist.exceptions import FileError
from   documentarist.log import log
from   documentarist.ui import UI, inform, warn, alert

class ExtractCommand(Command):
    '''Extract text found in files or URLs.'''
