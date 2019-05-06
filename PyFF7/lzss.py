#!/usr/bin/env python3
'''
Functions and classes for handling LZSS compression
Niema Moshiri 2019
'''
from . import BITS_PER_BYTE,NULL_BYTE
from struct import unpack

# constants
MIN_REF_LEN =  3 # Minimum Reference Length
MAX_REF_LEN = 18 # Maximum Reference Length
LEFT_NIBBLE_MASK  = 0b11110000
RIGHT_NIBBLE_MASK = 0b00001111
MOD_4096_MASK = 0xFFF

# sizes
SIZE = {
    'HEADER':  4, # File Header (size of compressed data)
    'REF':     2, # Reference (12-bit offset and 4-bit length)
}

# error messages
ERROR_NOT_FILENAME_OR_BYTES = "Input must be a filename (str) or bytes"
ERROR_REF_SIZE = "Reference must be %d bytes" % SIZE['REF']

def control_to_flags(control):
    '''Convert a Control Byte to 8 flags (``True`` = literal data, ``False`` = reference)

    Args:
        ``control`` (``bytes``): The control byte

    Returns:
        ``flags`` (``list`` of ``bool``): 8 booleans denoting the flags of the next 8 pieces of data (``True`` = literal data, ``False`` = reference)
    '''
    return tuple(bool(control & (1 << i)) for i in range(BITS_PER_BYTE))

def ref_to_offset_len(ref):
    '''Convert a reference (2 bytes) to an offset and length

    Args:
        ``ref`` (``bytes``): The reference

    Returns:
        ``offset`` (``int``): The corresponding offset

        ``length`` (``int``): The corresponding length
    '''
    if len(ref) != SIZE['REF']:
        raise ValueError(ERROR_REF_TOO_LONG)
    length = (ref[1] & RIGHT_NIBBLE_MASK) + MIN_REF_LEN
    offset = ((ref[1] & LEFT_NIBBLE_MASK) << 4) | ref[0]
    return offset,length

def correct_offset(raw_offset, tail):
    '''Convert a raw offset to a real offset (i.e., not using 4-KiB bufer)

    Args:
        ``raw_offset`` (``int``): The raw offset to correct

        ``tail`` (``int``): Tail offset in file

    Returns:
        ``int``: The corrected offset
    '''
    return tail - ((tail - 18 - raw_offset) & MOD_4096_MASK)

def decompress_lzss(input_lzss):
    '''Decompress an LZSS file

    Args:
        ``input_lzz`` (``bytes``): The input LZSS-compressed file

    Returns:
        ``bytes``: The resulting decompressed file
    '''
    # prepare and read header
    if isinstance(input_lzss,str): # if filename instead of bytes, read bytes
        with open(input_lzss,'rb') as f:
            input_lzss = f.read()
    elif not isinstance(input_lzss, bytes):
        raise TypeError(ERROR_NOT_FILENAME_OR_BYTES)
    datasize = unpack('I', input_lzss[:SIZE['HEADER']])[0]
    if len(input_lzss) - 4 != datasize:
        raise ValueError("Size of compressed data (%d) does not match header size (%d)" % (len(input_lzss)-4, datasize))

    # decompress file
    out = bytearray()
    inpos = SIZE['HEADER'] # already read the header
    while inpos < len(input_lzss):
        flags = control_to_flags(input_lzss[inpos]); inpos += 1 # read control byte
        for flag in flags:
            if inpos >= len(input_lzss):
                break
            if flag: # True = literal data
                out.append(input_lzss[inpos]); inpos += 1
            else:    # False = reference
                offset, length = ref_to_offset_len(input_lzss[inpos:inpos+SIZE['REF']]); inpos += SIZE['REF']
                pos = correct_offset(offset, len(out))
                if pos < 0: # negative index = NULL byte
                    chunk = bytearray(NULL_BYTE * min(abs(pos),length)); pos += len(chunk)
                else:
                    chunk = bytearray()
                chunk += out[pos:pos+length-len(chunk)]; out += chunk
                for i in range(len(chunk), length): # out-of-bounds offset = repeated runs
                    out.append(chunk[i%len(chunk)])
    return out
