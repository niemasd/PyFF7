#!/usr/bin/env python3
'''
Functions and classes for handling save files
Niema Moshiri 2019
'''
from struct import pack,unpack

# size of various items in a save file (in bytes)
SIZE = {
}

# format-dependant properties
PROP = {
    'DEX': {
        'file_id': b"\x31\x32\x33\x2D\x34\x35\x36\x2D\x53\x54\x44",
        'file_size': 134976,
        'header_size': 12096,
        'label': "DEX Format",
        'num_slots': 15,
    },
    'MC': {
        'file_id': b"\x4D\x43",
        'file_size': 131072,
        'header_size': 8192,
        'label': "Mem Card Format",
        'num_slots': 15,
    },

    'PC': {
        'file_id': b"\x71\x73",
        'file_size': 65109,
        'header_size': 9,
        'label': "PC Version",
        'num_slots': 15,
    },

    'PSP': {
        'file_id': b"\x00\x50\x4D\x56",
        'file_size': 131200,
        'header_size': 8320,
        'label': "PSP Version",
        'num_slots': 15,
    },

    'PSV': {
        'file_id': b"\x00\x56\x53\x50",
        'file_size': 8324,
        'header_size': 132,
        'label': "PS Vita Version",
        'num_slots': 1,
    },

    'PSX': {
        'file_id': b"\x53\x43\x11\x01\x82\x65\x82\x65\x82\x56\x81\x5E\x82\x72\x82\x60",
        'file_size': 8192,
        'header_size': 0,
        'label': "PSX Version",
        'num_slots': 1,
    },

    'VGM': {
        'file_id': b"\x56\x67\x73\x4D",
        'file_size': 131136,
        'header_size': 8256,
        'label': "VGM Format",
        'num_slots': 15,
    },
}
FILESIZE2FORMAT = {PROP[k]['file_size']:k for k in PROP}

# other defaults

# error messages
ERROR_INVALID_SAVE_FILE = "Invalid save file"

class Save:
    '''Save file class'''
    def __init__(self, data):
        '''``Save`` constructor

        Args:
            ``data`` (``bytes``): The input Save file
        '''
        # if data is filename, load actual bytes
        if isinstance(data,str): # if filename instead of bytes, read bytes
            with open(data,'rb') as f:
                data = f.read()
        if len(data) not in FILESIZE2FORMAT:
            raise ValueError(ERROR_INVALID_SAVE_FILE)

        # parse save type
        self.save_type = FILESIZE2FORMAT[len(data)]; prop = PROP[self.save_type]; file_id = prop['file_id']
        if data[:len(file_id)] != file_id:
            raise ValueError(ERROR_INVALID_SAVE_FILE)
        ind = 0

        # load data
        self.header = data[ind:ind+prop['header_size']]; ind += prop['header_size']
        self.save_slots = list()
        for _ in range(prop['num_slots']):
            slot = dict()
            self.save_slots.append(slot)
        self.footer = None # TODO

    def __len__(self):
        return len(self.save_slots)

    def __iter__(self):
        for s in self.save_slots:
            yield s
