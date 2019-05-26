#!/usr/bin/env python3
'''
Functions and classes for handling LZSS compression
Niema Moshiri 2019
'''
from . import BITS_PER_BYTE,NULL_BYTE
from struct import pack,unpack

# constants
MIN_REF_LEN =  3 # Minimum Reference Length
MAX_REF_LEN = 18 # Maximum Reference Length
LEFT_NIBBLE_MASK  = 0b11110000
RIGHT_NIBBLE_MASK = 0b00001111
WINDOW_MASK = 0x0FFF
WINDOW_SIZE = 0x1000
BITS_PER_BYTE = 8

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
    if len(ref) == 1: # some files have a reference of `OOOOLLLL` instead of `OOOOOOOO OOOOLLLL`, e.g. in RIDE_0.NPK
        return ((ref[0] & RIGHT_NIBBLE_MASK) + MIN_REF_LEN), ((ref[0] & LEFT_NIBBLE_MASK) >> 4)
    if len(ref) != SIZE['REF']:
        raise ValueError("Reference must be %d bytes, but it was %d bytes" % (SIZE['REF'],len(ref)))
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
    return tail - ((tail - 18 - raw_offset) & WINDOW_MASK)

def decompress_lzss(data):
    '''Decompress an LZSS file

    Args:
        ``input_lzz`` (``bytes``): The input LZSS-compressed file

    Returns:
        ``bytes``: The resulting decompressed file
    '''
    # prepare and read header
    if isinstance(data,str): # if filename instead of bytes, read bytes
        with open(data,'rb') as f:
            data = f.read()
    elif not isinstance(data, bytes) and not isinstance(data, bytearray):
        raise TypeError(ERROR_NOT_FILENAME_OR_BYTES)
    datasize = unpack('I', data[:SIZE['HEADER']])[0]
    if len(data) - 4 != datasize:
        raise ValueError("Size of compressed data (%d) does not match header size (%d)" % (len(data)-4, datasize))

    # decompress file
    out = bytearray()
    inpos = SIZE['HEADER'] # already read the header
    while inpos < len(data):
        flags = control_to_flags(data[inpos]); inpos += 1 # read control byte
        for flag in flags:
            if inpos >= len(data):
                break
            if flag: # True = literal data
                out.append(data[inpos]); inpos += 1
            else:    # False = reference
                offset, length = ref_to_offset_len(data[inpos:inpos+SIZE['REF']]); inpos += SIZE['REF']
                pos = correct_offset(offset, len(out))
                if pos < 0: # negative index = NULL byte
                    chunk = bytearray(NULL_BYTE * min(abs(pos),length)); pos += len(chunk)
                else:
                    chunk = bytearray()
                chunk += out[pos:pos+length-len(chunk)]; out += chunk
                for i in range(len(chunk), length): # out-of-bounds offset = repeated runs
                    if len(chunk) == 0: # RIDE_0.NPK had some file(s) with empty chunks. I imagine this means NULL_BYTE?
                        out += NULL_BYTE
                    else:
                        out.append(chunk[i%len(chunk)])
    return out

class Dictionary:
    '''Dictionary for LZSS compression'''
    def __init__(self, ptr):
        '''``Dictionary`` constructor'''
        self.ptr = ptr

        # For each reference length there is one dictionary mapping substrings
        # to dictionary offsets.
        self.d = [{} for i in range(0, MAX_REF_LEN + 1)]

        # For each reference length there is also a reverse dictionary
        # mapping dictionary offsets to substrings. This makes removing
        # dictionary entries more efficient.
        self.r = [{} for i in range(0, MAX_REF_LEN + 1)]

    # Add all initial substrings of a string to the dictionary.
    def add(self, s):
        # Generate all substrings
        for length in range(MIN_REF_LEN, min(len(s),MAX_REF_LEN) + 1):
            substr = s[:length]

            # Remove obsolete mapping, if present
            try:
                prevOffset = self.d[length][substr]
                del self.r[length][prevOffset]
            except KeyError:
                pass

            try:
                prevSubstr = self.r[length][self.ptr]
                del self.d[length][prevSubstr]
            except KeyError:
                pass

            # Add new mapping
            self.d[length][substr] = self.ptr
            self.r[length][self.ptr] = substr

        # Advance dictionary pointer
        self.ptr = (self.ptr + 1) & WINDOW_MASK

    # Find any of the initial substrings of a string in the dictionary,
    # looking for long matches first. Returns an (offset, length) tuple if
    # found. Raises KeyError if not found.
    def find(self, s):
        maxLength = MAX_REF_LEN
        if maxLength > len(s):
            maxLength = len(s)

        for length in range(maxLength, MIN_REF_LEN - 1, -1):
            substr = s[:length]

            try:
                offset = self.d[length][substr]
                if offset != self.ptr:  # the FF7 LZSS decompressor can't handle this case
                    return (offset, length)
            except KeyError:
                pass

        raise KeyError


# Compress an 8-bit string to LZSS format.
def compress_lzss(data):
    if isinstance(data,str): # if filename instead of bytes, read bytes
        with open(data,'rb') as f:
            data = f.read()
    elif not isinstance(data, bytes) and not isinstance(data, bytearray):
        raise TypeError(ERROR_NOT_FILENAME_OR_BYTES)
    dictionary = Dictionary(WINDOW_SIZE - 2*MAX_REF_LEN)

    # Prime the dictionary
    for i in range(MAX_REF_LEN):
        dictionary.add(NULL_BYTE * (MAX_REF_LEN - i) + data[:i])

    # Output data
    output = bytearray()

    i = 0
    dataSize = len(data)

    while i < dataSize:

        # Accumulated output chunk
        accum = bytearray()

        # Process 8 literals or references at a time
        flags = 0
        for bit in range(8):
            if i >= dataSize:
                break

            # Next substring in dictionary?
            try:
                substr = data[i:i + MAX_REF_LEN]
                offset, length = dictionary.find(substr)

                # Yes, append dictionary reference
                accum += bytes([offset & 0xFF]) + bytes([(((offset >> 4) & 0xf0) | (length - MIN_REF_LEN))])

                # Update dictionary
                for j in range(length):
                    dictionary.add(data[i + j:i + j + MAX_REF_LEN])

                i += length

            except KeyError:

                # Append literal value
                v = bytes([data[i]])
                accum += v

                flags |= (1 << bit)

                # Update dictionary
                dictionary.add(data[i:i + MAX_REF_LEN])

                i += 1

        # Chunk complete, add to output
        output += bytes([flags])
        output += accum

    return pack('I', len(output)) + output
