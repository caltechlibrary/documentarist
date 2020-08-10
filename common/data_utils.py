'''
data_utils: data manipulation utilities
'''

import dateparser
import datetime
from   datetime import datetime as dt
from   tzlocal import get_localzone


# Constants.
# .............................................................................

DATE_FORMAT = '%b %d %Y %H:%M:%S %Z'
'''Format in which lastmod date is printed back to the user. The value is used
with datetime.strftime().'''


# Functions.
# .............................................................................

def slice(lst, n):
    # Original algorithm from Jurgen Strydom posted 2019-02-21 Stack Overflow
    # https://stackoverflow.com/a/54802737/743730
    '''Yield n number of slices from lst.'''
    for i in range(0, n):
        yield lst[i::n]


def ordinal(n):
    '''Print a number followed by "st" or "nd" or "rd", as appropriate.'''
    # Spectacular algorithm by user "Gareth" at this posting:
    # http://codegolf.stackexchange.com/a/4712
    return '{}{}'.format(n, 'tsnrhtdd'[(n/10%10!=1)*(n%10<4)*n%10::4])


def expand_range(text):
    '''Return individual numbers for a range expressed as X-Y.'''
    # This makes the range 1-100 be 1, 2, ..., 100 instead of 1, 2, ..., 99
    if '-' in text:
        range_list = text.split('-')
        range_list.sort(key = int)
        return [*map(str, range(int(range_list[0]), int(range_list[1]) + 1))]
    else:
        return text


def timestamp():
    '''Return a string describing the date and time right now.'''
    return dt.now(get_localzone()).strftime(DATE_FORMAT)


def parse_datetime(string):
    '''Parse a human-written time/date string using dateparser's parse()
function with predefined settings.'''
    return dateparser.parse(string, settings = {'RETURN_AS_TIMEZONE_AWARE': True})


def plural(word, count):
    '''Simple pluralization; adds "s" to the end of "word" if count > 1.'''
    if isinstance(count, int):
        return word + 's' if count > 1 else word
    elif isinstance(count, (list, set, dict)):
        return word + 's' if len(count) > 1 else word
    else:
        # If we don't recognize the kind of thing it is, return it unchanged.
        return word