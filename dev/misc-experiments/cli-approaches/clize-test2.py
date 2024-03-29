#!/usr/local/bin/python3

import base64
from functools import reduce
from nuclear import CliBuilder, argument, flag, parameter, subcommand

def say_hello(name: str, decode: bool, repeat: int):
    if decode:
        name = base64.b64decode(name).decode('utf-8')
    print(' '.join([f"I'm a {name}!"] * repeat))

def calculate_factorial(n: int):
    print(reduce(lambda x, y: x * y, range(1, n + 1)))

def calculate_primes(n: int):
    print(sorted(reduce((lambda r, x: r - set(range(x ** 2, n, x)) if (x in r) else r),
                        range(2, int(n ** 0.5)), set(range(2, n)))))

CliBuilder().has(
    subcommand('hello', run=say_hello).has(
        argument('name'),
        flag('decode', help='Decode name as base64'),
        parameter('repeat', type=int, default=1),
    ),
    subcommand('calculate').has(
        subcommand('factorial', help='Calculate factorial', run=calculate_factorial).has(
            argument('n', type=int),
        ),
        subcommand('primes', help='List prime numbers using Sieve of Eratosthenes', run=calculate_primes).has(
            argument('n', type=int, required=False, default=100, help='maximum number to check'),
        ),
    ),
).run()
