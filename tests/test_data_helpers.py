import sys
sys.path.append('../common')
from common.data_utils import *

def test_slice():
    assert list(slice([1, 2, 3, 4], 2)) == [[1, 3], [2, 4]]
    assert list(slice([1, 2, 3, 4, 5], 2)) == [[1, 3, 5], [2, 4]]


def test_expand_range():
    assert expand_range('1-5') == ['1', '2', '3', '4', '5']
    assert expand_range('2-10') == ['2', '3', '4', '5', '6', '7', '8', '9', '10']