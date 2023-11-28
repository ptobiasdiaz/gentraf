#!/usr/bin/env python3

'''
    GenTraf: tools
'''

import os
import random
import string
from pathlib import Path


def generate_random_str(size: int) -> str:
    '''Generate random string of given size'''
    return ''.join(random.choice(string.ascii_letters + string.digits) for i in range(size))


def generate_random_bytes(size: int) -> bytes:
    '''Generate random bytes of given size'''
    return os.urandom(size)


def generate_file(destination: [str|Path], size: int) -> str:
    '''Generate file and return absolute filename'''
    if isinstance(destination, str):
        destination = Path(destination)
    if destination.is_dir:
        destination = destination.joinpath(generate_random_str(10))
    with open(destination, 'wb') as contents:
        contents.write(generate_random_bytes(size))
    return destination.absolute()
