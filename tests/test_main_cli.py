import subprocess
import sys
sys.path.append('..')
from documentarist.exceptions import *


def test_main_help(capsys):
    result = subprocess.run(['bin/dm'], capture_output = True)
    assert result.stdout.startswith(b'usage: dm [-h]')

    result = subprocess.run(['bin/dm', '-h'], capture_output = True)
    assert result.stdout.startswith(b'usage: dm [-h]')

    result = subprocess.run(['bin/dm', 'help'], capture_output = True)
    assert result.stdout.startswith(b'"dm" is the command-line interface for')

    result = subprocess.run(['bin/dm', 'help', 'version'], capture_output = True)
    assert result.stdout.startswith(b'Print Documentarist version information, and exit.')


def test_main_version(capsys):
    result = subprocess.run(['bin/dm', 'version'], capture_output = True)
    assert result.stdout.startswith(b'Documentarist version')
