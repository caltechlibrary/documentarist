import sys
sys.path.append('../common')
from common.exceptions import *

def test_exceptions():
    try:
        raise InternalError('foo')
    except Exception as ex:
        assert isinstance(ex, DocumentaristException)
