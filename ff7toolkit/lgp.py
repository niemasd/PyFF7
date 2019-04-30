#!/usr/bin/env python3
'''
Functions and classes for handling LGP archives
Niema Moshiri 2019
'''
from . import read_bytes
from struct import unpack

# size of various items in an LGP archive (in bytes)
SIZE = {
    # Header
    'HEADER_FILE-CREATOR': 12, # File Creator
    'HEADER_NUM-FILES':     4, # Number of Files in Archive

    # Table of Contents Entries
    'TOC-ENTRY_FILENAME':  20, # ToC Entry: Filename
    'TOC-ENTRY_DATA-START':  4, # ToC Entry: Data Start Position
    'TOC-ENTRY_CHECK':       1, # ToC Entry: Check Code
    'TOC-ENTRY_DUP-IDENT':   2, # ToC Entry: Duplicate Filename Identifier

    # CRC
    'CRC-DEFAULT':        3602, # CRCs are usually 3602, but not necessarily
}
SIZE['HEADER'] = sum(SIZE[k] for k in SIZE if k.startswith('HEADER_'))
SIZE['TOC-ENTRY'] = sum(SIZE[k] for k in SIZE if k.startswith('TOC-ENTRY_'))

# start positions of various items in an LGP archive (in bytes)
START = {
    # Header
    'HEADER_FILE-CREATOR': 0,
    'HEADER_NUM-FILES': SIZE['HEADER_FILE-CREATOR'],

    # Table of Contents
    'TOC': SIZE['HEADER'],
}
# ToC entries (0 = start of entry)
START['TOC-ENTRY_FILENAME'] = 0
START['TOC-ENTRY_DATA-START'] = START['TOC-ENTRY_FILENAME'] + SIZE['TOC-ENTRY_FILENAME']
START['TOC-ENTRY_CHECK'] = START['TOC-ENTRY_DATA-START'] + SIZE['TOC-ENTRY_DATA-START']
START['TOC-ENTRY_DUP-IDENT'] = START['TOC-ENTRY_CHECK'] + SIZE['TOC-ENTRY_CHECK']

class LGP:
    '''LGP Archive class'''
    def __init__(self, filename):
        '''``LGP`` constructor

        Args:
            ``filename`` (``str``): The filename of the LGP archive
        '''
        self.filename = filename
        with open(filename, 'rb') as f:
            # read header
            tmp = f.read(SIZE['HEADER'])
            self.header = {
                'file_creator': tmp[START['HEADER_FILE-CREATOR']:START['HEADER_FILE-CREATOR']+SIZE['HEADER_FILE-CREATOR']].decode(),
                'num_files': unpack('i', tmp[START['HEADER_NUM-FILES']:START['HEADER_NUM-FILES']+SIZE['HEADER_NUM-FILES']])[0],
            }

            # read table of contents
            self.toc = list()
            for i in range(self.header['num_files']):
                tmp = f.read(SIZE['TOC-ENTRY'])
                start = START['TOC'] + (i * SIZE['TOC-ENTRY'])
                self.toc.append({
                    'filename': tmp[START['TOC-ENTRY_FILENAME']:START['TOC-ENTRY_FILENAME']+SIZE['TOC-ENTRY_FILENAME']].decode(),
                    'data_start': unpack('i', tmp[START['TOC-ENTRY_DATA-START']:START['TOC-ENTRY_DATA-START']+SIZE['TOC-ENTRY_DATA-START']])[0],
                    'check': ord(tmp[START['TOC-ENTRY_CHECK']:START['TOC-ENTRY_CHECK']+SIZE['TOC-ENTRY_CHECK']]),
                    'dup-ident': unpack('h', tmp[START['TOC-ENTRY_DUP-IDENT']:START['TOC-ENTRY_DUP-IDENT']+SIZE['TOC-ENTRY_DUP-IDENT']])[0],
                })
        self.crc = None
        self.data = None

def read_lgp_info(filename):
    '''Read the information about an LGP archive

    Args:
        ``filename`` (``str``): Name of the LGP archive from which to read info

    Returns:
        ``dict``: Archive Header (keys are ``"file_creator"`` and ``"num_files"``)

        ``dict``: Archive Table of Contents (list of ToC entries)

        ``bytes``: CRC byte representation
    '''
    lgp_archive = LGP(filename)
    return lgp_archive.header, lgp_archive.toc, lgp_archive.crc
