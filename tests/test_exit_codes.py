import sys
sys.path.append('../common')
from common.exit_codes import *

def test_exit_code():
    assert ExitCode.bad_arg.value[0] == 2
    assert ExitCode.exception.value[0] == 4
    assert ExitCode.success.value[1] == 'success -- program completed normally'
