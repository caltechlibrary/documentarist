#!/usr/local/bin/python3

import base64
from functools import reduce
from nuclear import CliBuilder, argument, flag, parameter, subcommand

documentarist_description = '''This is some long help text.

Long long long. Longer. Long long long. Longer. Long long long.
Longer. Long long long. Longer.'''


def credentials(name: str, decode: bool, repeat: int):
    if decode:
        name = base64.b64decode(name).decode('utf-8')
    print(' '.join([f"I'm a {name}!"] * repeat))

def calculate_factorial(n: int):
    print(reduce(lambda x, y: x * y, range(1, n + 1)))

def calculate_primes(n: int):
    print(sorted(reduce((lambda r, x: r - set(range(x ** 2, n, x)) if (x in r) else r),
                        range(2, int(n ** 0.5)), set(range(2, n)))))

CliBuilder(help = documentarist_description).has(
    flag('-q', '--quiet', help = 'be quiet'),
    flag('-@', '--debug', help = 'debug'),
    subcommand('credentials', run = credentials).has(
        argument('name'),
        flag('decode', help='Decode name as base64'),
        parameter('repeat', type=int, default=1),
    ),
    subcommand('config').has(
        subcommand('show', help='Show the configuration', run=calculate_factorial).has(
            argument('n', type=int),
        ),
        subcommand('basename', help='Set the base name', run=calculate_primes).has(
            argument('n', type=int, required=False, default=100, help='maximum number to check'),
        ),
    ),
).run()
