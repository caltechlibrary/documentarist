import sys
sys.path.append('..')
from documentarist.exit_codes import *

def test_exit_code():
    assert int(ExitCode.success) == 0
    assert int(ExitCode.bad_arg) == 2
