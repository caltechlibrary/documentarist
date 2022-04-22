'''
label.py: label an image
'''

from   argparse import ArgumentParser, RawDescriptionHelpFormatter
from   commonpy.data_utils import pluralized
from   commonpy.file_utils import filename_extension, filename_basename
from   commonpy.file_utils import files_in_directory, readable, writable
from   os.path import isfile, isdir, exists

from   documentarist import _OUTPUT_EXT
from   documentarist.command import Command, docstring_summary
from   documentarist.log import log, loglist
from   documentarist.services import ACCEPTED_FORMATS
from   documentarist.ui import UI, inform, warn, alert


class LabelCommand(Command):
    '''Label images found in files or URLs.

    If no arguments are given to this command, it prints a help summary.  If
    arguments are given to this command (and none of them is the literal word
    "help"), they are processed as follows:

      * If the flag -f is given, the value following it is assumed to be a
        file containing one or more file names, directory names, or URLs (or
        a mixture thereof)

      * If no -f flag is given, the arguments are assumed to be file names,
        directory names, or URLs.

    If an argument value looks like a URL, then it's interpreted as an image
    location to be downloaded and then sent to the labeling system. If an
    argument value does not look like a URL, but does have a file name
    extension corresponding to an image format (e.g., .jpg), then it is
    assumed to be an image file to be sent to the labeling system. If an
    argument value is a directory, then it is recursively scanned for image
    files and other directories. If an argument value is a file name but not
    an image file, it is ignored.
    '''

    def __init__(self, arg_list):
        super().__init__('label')
        parser = ArgumentParser(description = docstring_summary(self, 'label'),
                                formatter_class = RawDescriptionHelpFormatter,
                                usage = '%(prog)s label <documents>')
        parser.add_argument('-f', '--from-file', action = 'store', metavar = 'F',
                            help = 'read list of inputs from file F')
        parser.add_argument('sources', nargs = '*', action = 'store',
                            help = 'image files, directories, or URLs')

        # Parse the command line and handle early exits -----------------------

        if not arg_list or 'help' in arg_list:
            parser.print_help()
            return
        args = parser.parse_args(arg_list)

        # Do the real work ----------------------------------------------------

        # Gather list of individual items. This may be mixed files, dirs, urls.
        if args.from_file:
            targets = self._targets_from_file(args.from_file)
        else:
            targets = self._targets_from_arguments(args.sources)
        log(f'we have {pluralized("target", targets, True)} to label')
        breakpoint()


    def _targets_from_file(self, input_file):
        if not exists(input_file):
            raise FileError('File does not exist: ' + input_file)
        if not isfile(input_file):
            raise FileError('Not a file: ' + input_file)
        if not readable(input_file):
            raise FileError('File is not readable: ' + input_file)

        log(f'reading targets from file {input_file}')
        lines = filter(None, open(input_file).read().splitlines())
        log(f'read {pluralized("line", lines, True)} from {input_file}')
        return lines


    def _targets_from_arguments(self, args):
        # Validator_collection takes a long time to load.  Delay loading it
        # until needed, so that overall application startup time is faster.
        from validator_collection.checkers import is_url

        candidates = []
        for item in args:
            if is_url(item):
                log('found url ' + item)
                candidates.append(item)
            elif isfile(item) and filename_extension(item) in ACCEPTED_FORMATS:
                log('found candidate file ' + item)
                candidates.append(item)
            elif isdir(item):
                # It's a directory, so look for files within.
                log('looking for files in directory ' + item)
                candidates += files_in_directory(item, extensions = ACCEPTED_FORMATS)
            else:
                warn(f'"{item}" not a file or directory')

        # Filter files created in past runs.
        candidates = filter(lambda name: '.documentarist' not in name, candidates)

        # If there is both a file in the format we generate and another
        # format of that file, ignore the other formats and just use ours.
        # Note: candidates is an iterator, but because it's tested inside
        # the loop, a separate list is needed else get unexpected results.
        candidates = list(candidates)
        kept = []
        for item in candidates:
            ext  = filename_extension(item)
            base = filename_basename(item)
            if ext != _OUTPUT_EXT and (base + _OUTPUT_EXT in candidates):
                # png version of file is also present => skip this other version
                log('ignoring file because we have it another format: ' + item)
                continue
            kept.append(item)

        return kept
