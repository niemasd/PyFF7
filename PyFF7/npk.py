#!/usr/bin/env python3
'''
Functions and classes for handling NPK archives
Niema Moshiri 2019
'''
from . import NULL_BYTE,NULL_STR
from .lzss import compress_lzss,decompress_lzss
from struct import pack,unpack

# size of various items in an NPK archive (in bytes)
SIZE = {
    'BLOCK':                1024, # Block
    'BLOCK_NUM-SUBBLOCKS':     4, # Block: Number of Sub-Blocks in this Block
    'BLOCK_SIZE-COMPRESSED':   2, # Block: Size of Compressed Data (in bytes)
    'BLOCK_SIZE-DECOMPRESSED': 2, # Block: Size of Decompressed Data (in bytes) (not 100% sure)
}

# start positions of various items in an NPK archive (in bytes)
START = {
    'BLOCK_NUM-SUBBLOCKS': 0,
    'BLOCK_SIZE-COMPRESSED': SIZE['BLOCK_NUM-SUBBLOCKS'],
    'BLOCK_SIZE-DECOMPRESSED': SIZE['BLOCK_NUM-SUBBLOCKS'] + SIZE['BLOCK_SIZE-COMPRESSED'],
    'BLOCK_DATA': SIZE['BLOCK_NUM-SUBBLOCKS'] + SIZE['BLOCK_SIZE-COMPRESSED'] + SIZE['BLOCK_SIZE-DECOMPRESSED']
}

# error messages
ERROR_INVALID_NPK_FILE = "Invalid NPK file"

class NPK:
    '''NPK archive class'''
    def __init__(self, filename):
        '''``NPK`` constructor

        Args:
            ``filename`` (``str``): The filename of the NPK archive
        '''
        self.files = list()
        f = open(filename,'rb'); data = f.read(); f.close(); block_start = 0; curr_file = bytearray()
        while block_start < len(data):
            block = data[block_start:block_start+SIZE['BLOCK']]; block_start += SIZE['BLOCK']
            num_subblocks = unpack('I', block[START['BLOCK_NUM-SUBBLOCKS'] : START['BLOCK_NUM-SUBBLOCKS']+SIZE['BLOCK_NUM-SUBBLOCKS']])[0]
            size_compressed = unpack('H', block[START['BLOCK_SIZE-COMPRESSED'] : START['BLOCK_SIZE-COMPRESSED']+SIZE['BLOCK_SIZE-COMPRESSED']])[0]
            size_decompressed = unpack('H', block[START['BLOCK_SIZE-DECOMPRESSED'] : START['BLOCK_SIZE-DECOMPRESSED']+SIZE['BLOCK_SIZE-DECOMPRESSED']])[0]
            if num_subblocks != 0:
                curr_file += block[START['BLOCK_DATA'] : size_compressed]
            if num_subblocks <= 1 and len(curr_file) != 0:
                curr_file = pack('I', len(curr_file)) + curr_file # the data's LZSS-compressed, minus the file header (4-byte integer denoting its compressed size)
                self.files.append(decompress_lzss(curr_file))
                curr_file = bytearray()

    def __len__(self):
        return len(self.files)

    def __iter__(self):
        for f in self.files:
            yield f

def pack_npk(files, npk_filename):
    '''
    Pack the files in ``files`` into an NPK archive ``npk_filename``

    Args:
        ``files`` (iterable of ``str``): The filenames to pack

        ``npk_filename`` (``str``): The filename to write the packed NPK archive
    '''
    files = list(files)
    with open(npk_filename, 'wb') as npk_f:
        for file_num, disk_path in enumerate(files):
            print("Compressing file %d of %d..." % (file_num+1, len(files)))
            with open(disk_path, 'rb') as curr_f:
                curr_data = curr_f.read()
            lzss_chunks = compress_lzss(curr_data, include_header=False, merge_chunks=False)
            npk_blocks = [list()] # list of blocks (each block is list of (uncomp_size, lzss_chunk) tuples)
            for chunk_ind in range(len(lzss_chunks)):
                uncomp_offset, comp_chunk = lzss_chunks[chunk_ind]
                if chunk_ind == 0:
                    uncomp_size = uncomp_offset
                else:
                    uncomp_size = uncomp_offset - lzss_chunks[chunk_ind-1][0]
                if sum(len(lc) for us, lc in npk_blocks[-1]) + len(comp_chunk) > 1016:
                    npk_blocks.append(list())
                npk_blocks[-1].append((uncomp_size, comp_chunk))
            for npk_block_ind, npk_block in enumerate(npk_blocks):
                written = 0
                written += npk_f.write(pack('I', len(npk_blocks)-npk_block_ind))
                written += npk_f.write(pack('H', START['BLOCK_DATA'] + sum(len(lc) for us, lc in npk_block)))
                written += npk_f.write(pack('H', sum(us for us, lc in npk_block)))
                for us, lc in npk_block:
                    written += npk_f.write(lc)
                while written < 1024:
                    written += npk_f.write(b'\00')
