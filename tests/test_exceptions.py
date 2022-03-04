import sys
sys.path.append('..')
from documentarist.exceptions import *

def test_exceptions():
    try:
        raise InternalError('foo')
    except Exception as ex:
        assert isinstance(ex, DocumentaristException)
