#!/usr/bin/env python3
'''
Functions and classes for handling save files
Niema Moshiri 2019
'''
from .text import decode_field_text
from struct import pack,unpack

# constants
SAVE_SLOT_SIZE = 4340

# start offsets of various items in a save file (in bytes, with respect to start of slot data)
START = {
    'SLOT_CHECKSUM':          0x0000, # Save Slot: Checksum
    'SLOT_PREVIEW-LEVEL':     0x0004, # Save Slot: Preview: Lead Character's Level
    'SLOT_PREVIEW-PORTRAIT1': 0x0005, # Save Slot: Preview: Portrait 1
    'SLOT_PREVIEW-PORTRAIT2': 0x0006, # Save Slot: Preview: Portrait 2
    'SLOT_PREVIEW-PORTRAIT3': 0x0007, # Save Slot: Preview: Portrait 3
    'SLOT_PREVIEW-NAME':      0x0008, # Save Slot: Preview: Lead Character's Name
    'SLOT_PREVIEW-HP-CURR':   0x0018, # Save Slot: Preview: Lead Character's Current HP
    'SLOT_PREVIEW-HP-MAX':    0x001A, # Save Slot: Preview: Lead Character's Maximum HP
    'SLOT_PREVIEW-MP-CURR':   0x001C, # Save Slot: Preview: Lead Character's Current MP
    'SLOT_PREVIEW-MP-MAX':    0x001E, # Save Slot: Preview: Lead Character's Maximum MP
}

# size of various items in a save file (in bytes)
SIZE = {
    # Final Fantasy VII Save Slot
    'SLOT_CHECKSUM':          2, # Save Slot: Checksum
    'SLOT_PREVIEW-HP-CURR':   2, # Save Slot: Preview: Lead Character's Current HP
    'SLOT_PREVIEW-HP-MAX':    2, # Save Slot: Preview: Lead Character's Maximum HP
    'SLOT_PREVIEW-LEVEL':     1, # Save Slot: Preview: Lead Character's Level
    'SLOT_PREVIEW-MP-CURR':   2, # Save Slot: Preview: Lead Character's Current MP
    'SLOT_PREVIEW-MP-MAX':    2, # Save Slot: Preview: Lead Character's Maximum MP
    'SLOT_PREVIEW-NAME':     16, # Save Slot: Preview: Lead Character's Name
    'SLOT_PREVIEW-PORTRAIT1': 1, # Save Slot: Preview: Portrait 1
    'SLOT_PREVIEW-PORTRAIT2': 1, # Save Slot: Preview: Portrait 2
    'SLOT_PREVIEW-PORTRAIT3': 1, # Save Slot: Preview: Portrait 3
}

# translate portrait number to character name
PORTRAIT_TO_NAME = {
      0: 'Cloud',
      1: 'Barret',
      2: 'Tifa',
      3: 'Aerith',
      4: 'Red XIII',
      5: 'Yuffie',
      6: 'Cait Sith',
      7: 'Vincent',
      8: 'Cid',
      9: 'Young Cloud',
     10: 'Sephiroth',
     11: 'Chocobo',
    255: 'None',
}

# format-dependant properties
PROP = {
    'DEX': {
        'file_id': b"\x31\x32\x33\x2D\x34\x35\x36\x2D\x53\x54\x44",
        'file_size': 134976,
        'header_size': 12096,
        'label': "DEX Format",
        'num_slots': 15,
        'slot_footer_size': 3340,
        'slot_header_size': 512,
    },
    'MC': {
        'file_id': b"\x4D\x43",
        'file_size': 131072,
        'header_size': 8192,
        'label': "Mem Card Format",
        'num_slots': 15,
        'slot_footer_size': 3340,
        'slot_header_size': 512,
    },

    'PC': {
        'file_id': b"\x71\x73",
        'file_size': 65109,
        'header_size': 9,
        'label': "PC Version",
        'num_slots': 15,
        'slot_footer_size': 0,
        'slot_header_size': 0,
    },

    'PSP': {
        'file_id': b"\x00\x50\x4D\x56",
        'file_size': 131200,
        'header_size': 8320,
        'label': "PSP Version",
        'num_slots': 15,
        'slot_footer_size': 3340,
        'slot_header_size': 512,
    },

    'PSV': {
        'file_id': b"\x00\x56\x53\x50",
        'file_size': 8324,
        'header_size': 132,
        'label': "PS Vita Version",
        'num_slots': 1,
        'slot_footer_size': 3340,
        'slot_header_size': 512,
    },

    'PSX': {
        'file_id': b"\x53\x43\x11\x01\x82\x65\x82\x65\x82\x56\x81\x5E\x82\x72\x82\x60",
        'file_size': 8192,
        'header_size': 0,
        'label': "PSX Version",
        'num_slots': 1,
        'slot_footer_size': 3340,
        'slot_header_size': 512,
    },

    'VGM': {
        'file_id': b"\x56\x67\x73\x4D",
        'file_size': 131136,
        'header_size': 8256,
        'label': "VGM Format",
        'num_slots': 15,
        'slot_footer_size': 3340,
        'slot_header_size': 512,
    },
}
FILESIZE_TO_FORMAT = {PROP[k]['file_size']:k for k in PROP}

# other defaults

# error messages
ERROR_INVALID_SAVE_FILE = "Invalid save file"

def parse_slot_data(data):
    '''Parse the bytes of a save slot

    Args:
        ``data`` (``bytes``): The input save slot data

    Returns:
        ``dict``: The parsed save slot
    '''
    if len(data) != SAVE_SLOT_SIZE:
        raise ValueError(ERROR_INVALID_SAVE_FILE)
    out = {'preview':dict()}
    out['checksum'] = unpack('H', data[START['SLOT_CHECKSUM']:START['SLOT_CHECKSUM']+SIZE['SLOT_CHECKSUM']])[0]
    out['preview']['level'] = unpack('B', data[START['SLOT_PREVIEW-LEVEL']:START['SLOT_PREVIEW-LEVEL']+SIZE['SLOT_PREVIEW-LEVEL']])[0]
    for i in [1,2,3]:
        out['preview']['portrait%d'%i] = unpack('B', data[START['SLOT_PREVIEW-PORTRAIT%d'%i]:START['SLOT_PREVIEW-PORTRAIT%d'%i]+SIZE['SLOT_PREVIEW-PORTRAIT%d'%i]])[0]
    out['preview']['name'] = decode_field_text(data[START['SLOT_PREVIEW-NAME']:START['SLOT_PREVIEW-NAME']+SIZE['SLOT_PREVIEW-NAME']])
    out['preview']['curr_hp'] = unpack('H', data[START['SLOT_PREVIEW-HP-CURR']:START['SLOT_PREVIEW-HP-CURR']+SIZE['SLOT_PREVIEW-HP-CURR']])[0]
    out['preview']['max_hp'] = unpack('H', data[START['SLOT_PREVIEW-HP-MAX']:START['SLOT_PREVIEW-HP-MAX']+SIZE['SLOT_PREVIEW-HP-MAX']])[0]
    out['preview']['curr_mp'] = unpack('H', data[START['SLOT_PREVIEW-MP-CURR']:START['SLOT_PREVIEW-MP-CURR']+SIZE['SLOT_PREVIEW-MP-CURR']])[0]
    out['preview']['max_mp'] = unpack('H', data[START['SLOT_PREVIEW-MP-MAX']:START['SLOT_PREVIEW-MP-MAX']+SIZE['SLOT_PREVIEW-MP-MAX']])[0]
    return out

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
        if len(data) not in FILESIZE_TO_FORMAT:
            raise ValueError(ERROR_INVALID_SAVE_FILE)

        # parse save type
        self.save_type = FILESIZE_TO_FORMAT[len(data)]; prop = PROP[self.save_type]; file_id = prop['file_id']
        if data[:len(file_id)] != file_id:
            raise ValueError(ERROR_INVALID_SAVE_FILE)
        ind = 0

        # load data
        self.header = data[ind:ind+prop['header_size']]; ind += prop['header_size']
        self.save_slots = list()
        for _ in range(prop['num_slots']):
            slot = dict()
            slot['header'] = data[ind:ind+prop['slot_header_size']]; ind += prop['slot_header_size']
            slot['data'] = parse_slot_data(data[ind:ind+SAVE_SLOT_SIZE]); ind += SAVE_SLOT_SIZE
            slot['footer'] = data[ind:ind+prop['slot_footer_size']]; ind += prop['slot_footer_size']
            self.save_slots.append(slot)

    def __len__(self):
        return len(self.save_slots)

    def __iter__(self):
        for s in self.save_slots:
            yield s
