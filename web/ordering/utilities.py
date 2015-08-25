'''
Purpose: Junk drawer for common functions
Author: David V. Hill
'''

import logging
import datetime

logger = logging.getLogger(__name__)


class Timer:
    '''Class to support closures, allowing Python code to be timed using the
    "with" statement.

    Example:
    with Timer() as t:
        do_something()
        do_something_else()

    print("Something and something_else took %f seconds" % t.interval.seconds)
    '''

    def __enter__(self):
        self.start = datetime.datetime.now()
        return self

    def __exit__(self, *args):
        self.end = datetime.datetime.now()
        self.interval = self.end - self.start


def date_from_doy(year, doy):
    '''Returns a python date object given a year and day of year'''

    d = datetime.datetime(int(year), 1, 1) + datetime.timedelta(int(doy) - 1)

    if int(d.year) != int(year):
        raise Exception("doy [%s] must fall within the specified year [%s]" %
                        (doy, year))
    else:
        return d


def is_number(s):
    '''Determines if a string value is a float or int.

    Keyword args:
    s -- A string possibly containing a float or int

    Return:
    True if s is a float or int
    False if s is not a float or int
    '''
    try:
        float(s)
        return True
    except (ValueError, TypeError):
        return False

#TODO: Remove this and replace with calls to str().lstrip('0')
def strip_zeros(value):
    '''
    Description:
      Removes all leading zeros from a string
    '''

    while value.startswith('0'):
        value = value[1:len(value)]
    return value
