#!/usr/bin/env python3
'''
Global functions and classes
Niema Moshiri 2019
'''
NULL_BYTE = b'\x00'
NULL_STR = NULL_BYTE.decode()

def read_bytes(filename, chunksize=None):
    '''Stream the bytes from a given file one-by-one

    Args:
        ``filename`` (``str``): The name of the file to open

        ``chunksize`` (``int``): The size of the buffer (``None`` = entire file)
    '''
    with open(filename, 'rb') as f:
        while True:
            buf = f.read(chunksize)
            if not buf:
                break
            for b in buf:
                yield b
