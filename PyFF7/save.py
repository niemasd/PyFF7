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
    # Final Fantasy VII Save Slot
    'SLOT_CHECKSUM':          0x0000, # Save Slot: Checksum
    'SLOT_UNKNOWN1':          0x0002, # Save Slot: Unknown 1
    'SLOT_PREVIEW-LEVEL':     0x0004, # Save Slot: Preview: Lead Character's Level
    'SLOT_PREVIEW-PORTRAIT1': 0x0005, # Save Slot: Preview: Portrait 1
    'SLOT_PREVIEW-PORTRAIT2': 0x0006, # Save Slot: Preview: Portrait 2
    'SLOT_PREVIEW-PORTRAIT3': 0x0007, # Save Slot: Preview: Portrait 3
    'SLOT_PREVIEW-NAME':      0x0008, # Save Slot: Preview: Lead Character's Name
    'SLOT_PREVIEW-HP-CURR':   0x0018, # Save Slot: Preview: Lead Character's Current HP
    'SLOT_PREVIEW-HP-MAX':    0x001A, # Save Slot: Preview: Lead Character's Maximum HP
    'SLOT_PREVIEW-MP-CURR':   0x001C, # Save Slot: Preview: Lead Character's Current MP
    'SLOT_PREVIEW-MP-MAX':    0x001E, # Save Slot: Preview: Lead Character's Maximum MP
    'SLOT_PREVIEW-GIL':       0x0020, # Save Slot: Preview: Total Gil
    'SLOT_PREVIEW-PLAYTIME':  0x0024, # Save Slot: Preview: Total Playtime
    'SLOT_PREVIEW-LOCATION':  0x0028, # Save Slot: Preview: Save Location
    'SLOT_WINDOW-COLOR-UL':   0x0048, # Save Slot: Window Color, Upper-Left Corner (RGB)
    'SLOT_WINDOW-COLOR-UR':   0x004B, # Save Slot: Window Color, Upper-Right Corner (RGB)
    'SLOT_WINDOW-COLOR-LL':   0x004E, # Save Slot: Window Color, Lower-Left Corner (RGB)
    'SLOT_WINDOW-COLOR-LR':   0x0051, # Save Slot: Window Color, Lower-Right Corner (RGB)
    'SLOT_RECORD-CLOUD':      0x0054, # Save Slot: Character Record: Cloud

    # Character Record
    'RECORD_SEPHIROTH-FLAG':    0x00, # Character Record: Vincent -> Sephiroth Flag
    'RECORD_LEVEL':             0x01, # Character Record: Level (0-99)
    'RECORD_STAT-STRENGTH':     0x02, # Character Record: Status: Strength (0-255)
    'RECORD_STAT-VITALITY':     0x03, # Character Record: Status: Vitality (0-255)
    'RECORD_STAT-MAGIC':        0x04, # Character Record: Status: Magic (0-255)
    'RECORD_STAT-SPIRIT':       0x05, # Character Record: Status: Spirit (0-255)
    'RECORD_STAT-DEXTERITY':    0x06, # Character Record: Status: Dexterity (0-255)
    'RECORD_STAT-LUCK':         0x07, # Character Record: Status: Luck (0-255)
    'RECORD_BONUS-STRENGTH':    0x08, # Character Record: Bonus: Strength
    'RECORD_BONUS-VITALITY':    0x09, # Character Record: Bonus: Vitality
    'RECORD_BONUS-MAGIC':       0x0A, # Character Record: Bonus: Magic
    'RECORD_BONUS-SPIRIT':      0x0B, # Character Record: Bonus: Spirit
    'RECORD_BONUS-DEXTERITY':   0x0C, # Character Record: Bonus: Dexterity
    'RECORD_BONUS-LUCK':        0x0D, # Character Record: Bonus: Luck
    'RECORD_LIMIT-LEVEL':       0x0E, # Character Record: Current Limit Level (1-4)
    'RECORD_LIMIT-BAR':         0x0F, # Character Record: Current Limit Bar (0 = Empty, 255 = Limit Break)
    'RECORD_NAME':              0x10, # Character Record: Name
    'RECORD_WEAPON':            0x1C, # Character Record: Equipped Weapon
    'RECORD_ARMOR':             0x1D, # Character Record: Equipped Armor
    'RECORD_ACCESSORY':         0x1E, # Character Record: Equipped Accessory
    'RECORD_FLAGS':             0x1F, # Character Record: Character Flags
}

# size of various items in a save file (in bytes)
SIZE = {
    # Final Fantasy VII Save Slot
    'SLOT_CHECKSUM':          2, # Save Slot: Checksum
    'SLOT_PREVIEW-GIL':       4, # Save Slot: Preview: Amount of Gil
    'SLOT_PREVIEW-HP-CURR':   2, # Save Slot: Preview: Lead Character's Current HP
    'SLOT_PREVIEW-HP-MAX':    2, # Save Slot: Preview: Lead Character's Maximum HP
    'SLOT_PREVIEW-LEVEL':     1, # Save Slot: Preview: Lead Character's Level
    'SLOT_PREVIEW-LOCATION': 32, # Save Slot: Preview: Save Location
    'SLOT_PREVIEW-MP-CURR':   2, # Save Slot: Preview: Lead Character's Current MP
    'SLOT_PREVIEW-MP-MAX':    2, # Save Slot: Preview: Lead Character's Maximum MP
    'SLOT_PREVIEW-NAME':     16, # Save Slot: Preview: Lead Character's Name
    'SLOT_PREVIEW-PLAYTIME':  4, # Save Slot: Preview: Total Playtime
    'SLOT_PREVIEW-PORTRAIT':  1, # Save Slot: Preview: Portrait
    'SLOT_RECORD':          132, # Save Slot: Character Record
    'SLOT_UNKNOWN1':          2, # Save Slot: Unknown 1
    'SLOT_WINDOW-COLOR':      3, # Save Slot: Window Color (RGB)

    # Character Record
    'RECORD_ACCESSORY':       1, # Character Record: Accessory
    'RECORD_ARMOR':           1, # Character Record: Armor
    'RECORD_BONUS':           1, # Character Record: Bonus
    'RECORD_FLAGS':           3, # Character Record: Character Flags
    'RECORD_LEVEL':           1, # Character Record: Level (0-99)
    'RECORD_LIMIT-BAR':       1, # Character Record: Current Limit Bar (0 = Empty, 255 = Limit Break)
    'RECORD_LIMIT-LEVEL':     1, # Character Record: Current Limit Level (1-4)
    'RECORD_NAME':           12, # Character Record: Name
    'RECORD_SEPHIROTH-FLAG':  1, # Character Record: Vincent -> Sephiroth Flag
    'RECORD_STAT':            1, # Character Record: Status
    'RECORD_WEAPON':          1, # Character Record: Equipped Weapon
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

def parse_color(data):
    '''Parse the bytes of an RGB color

    Args:
        ``data`` (``bytes``): The input RGB color bytes

    Returns:
        ``tuple`` of ``int``: The resulting RGB color
    '''
    if len(data) != SIZE['SLOT_WINDOW-COLOR']:
        raise ValueError("Invalid color data length: %d bytes" % len(data))
    return (data[0], data[1], data[2])

def parse_char_flags(data):
    '''Parse the bytes of Character Flags (in Character Record)

    Args:
        ``data`` (``bytes``): The input character flags bytes

    Returns:
        TODO: The resulting character flags
    '''
    if len(data) != SIZE['RECORD_FLAGS']:
        raise ValueError("Invalid character flags data length: %d" % len(data))
    return data

def parse_char_record(data):
    '''Parse the bytes of a character record

    Args:
        ``data`` (``bytes``): The input character record bytes

    Returns:
        ``dict``: The resulting character record
    '''
    if len(data) != SIZE['SLOT_RECORD']:
        raise ValueError("Invalid character record data length: %d bytes" % len(data))
    out = dict()
    out['sephiroth_flag'] = unpack('B', data[START['RECORD_SEPHIROTH-FLAG']:START['RECORD_SEPHIROTH-FLAG']+SIZE['RECORD_SEPHIROTH-FLAG']])[0]
    out['level'] = unpack('B', data[START['RECORD_LEVEL']:START['RECORD_LEVEL']+SIZE['RECORD_LEVEL']])[0]
    out['status'] = dict()
    for k in ['STRENGTH', 'VITALITY', 'MAGIC', 'SPIRIT', 'DEXTERITY', 'LUCK']:
        out['status'][k.lower()] = unpack('B', data[START['RECORD_STAT-%s'%k]:START['RECORD_STAT-%s'%k]+SIZE['RECORD_STAT']])[0]
    out['bonus'] = dict()
    for k in ['STRENGTH', 'VITALITY', 'MAGIC', 'SPIRIT', 'DEXTERITY', 'LUCK']:
        out['bonus'][k.lower()] = unpack('B', data[START['RECORD_BONUS-%s'%k]:START['RECORD_BONUS-%s'%k]+SIZE['RECORD_BONUS']])[0]
    out['limit_level'] = unpack('B', data[START['RECORD_LIMIT-LEVEL']:START['RECORD_LIMIT-LEVEL']+SIZE['RECORD_LIMIT-LEVEL']])[0]
    out['limit_bar'] = unpack('B', data[START['RECORD_LIMIT-BAR']:START['RECORD_LIMIT-BAR']+SIZE['RECORD_LIMIT-BAR']])[0]
    out['name'] = decode_field_text(data[START['RECORD_NAME']:START['RECORD_NAME']+SIZE['RECORD_NAME']])
    out['weapon'] = unpack('B', data[START['RECORD_WEAPON']:START['RECORD_WEAPON']+SIZE['RECORD_WEAPON']])[0]
    out['armor'] = unpack('B', data[START['RECORD_ARMOR']:START['RECORD_ARMOR']+SIZE['RECORD_ARMOR']])[0]
    out['accessory'] = unpack('B', data[START['RECORD_ACCESSORY']:START['RECORD_ACCESSORY']+SIZE['RECORD_ACCESSORY']])[0]
    out['flags'] = parse_char_flags(data[START['RECORD_FLAGS']:START['RECORD_FLAGS']+SIZE['RECORD_FLAGS']])
    return out

def parse_slot_data(data):
    '''Parse the bytes of a save slot

    Args:
        ``data`` (``bytes``): The input save slot data

    Returns:
        ``dict``: The parsed save slot
    '''
    if len(data) != SAVE_SLOT_SIZE:
        raise ValueError(ERROR_INVALID_SAVE_FILE)
    out = dict()
    out['checksum'] = unpack('H', data[START['SLOT_CHECKSUM']:START['SLOT_CHECKSUM']+SIZE['SLOT_CHECKSUM']])[0]
    out['unknown1'] = unpack('H', data[START['SLOT_UNKNOWN1']:START['SLOT_UNKNOWN1']+SIZE['SLOT_UNKNOWN1']])[0]
    out['preview'] = dict()
    out['preview']['level'] = unpack('B', data[START['SLOT_PREVIEW-LEVEL']:START['SLOT_PREVIEW-LEVEL']+SIZE['SLOT_PREVIEW-LEVEL']])[0]
    for i in [1,2,3]:
        out['preview']['portrait%d'%i] = unpack('B', data[START['SLOT_PREVIEW-PORTRAIT%d'%i]:START['SLOT_PREVIEW-PORTRAIT%d'%i]+SIZE['SLOT_PREVIEW-PORTRAIT']])[0]
    out['preview']['name'] = decode_field_text(data[START['SLOT_PREVIEW-NAME']:START['SLOT_PREVIEW-NAME']+SIZE['SLOT_PREVIEW-NAME']])
    out['preview']['curr_hp'] = unpack('H', data[START['SLOT_PREVIEW-HP-CURR']:START['SLOT_PREVIEW-HP-CURR']+SIZE['SLOT_PREVIEW-HP-CURR']])[0]
    out['preview']['max_hp'] = unpack('H', data[START['SLOT_PREVIEW-HP-MAX']:START['SLOT_PREVIEW-HP-MAX']+SIZE['SLOT_PREVIEW-HP-MAX']])[0]
    out['preview']['curr_mp'] = unpack('H', data[START['SLOT_PREVIEW-MP-CURR']:START['SLOT_PREVIEW-MP-CURR']+SIZE['SLOT_PREVIEW-MP-CURR']])[0]
    out['preview']['max_mp'] = unpack('H', data[START['SLOT_PREVIEW-MP-MAX']:START['SLOT_PREVIEW-MP-MAX']+SIZE['SLOT_PREVIEW-MP-MAX']])[0]
    out['preview']['gil'] = unpack('I', data[START['SLOT_PREVIEW-GIL']:START['SLOT_PREVIEW-GIL']+SIZE['SLOT_PREVIEW-GIL']])[0]
    out['preview']['playtime'] = unpack('I', data[START['SLOT_PREVIEW-PLAYTIME']:START['SLOT_PREVIEW-PLAYTIME']+SIZE['SLOT_PREVIEW-PLAYTIME']])[0]
    out['preview']['location'] = decode_field_text(data[START['SLOT_PREVIEW-LOCATION']:START['SLOT_PREVIEW-LOCATION']+SIZE['SLOT_PREVIEW-LOCATION']])
    out['window_color'] = dict()
    for k1,k2 in [('upper_left','UL'), ('upper_right','UR'), ('lower_left','LL'), ('lower_right','LR')]:
        out['window_color'][k1] = parse_color(data[START['SLOT_WINDOW-COLOR-%s'%k2]:START['SLOT_WINDOW-COLOR-%s'%k2]+SIZE['SLOT_WINDOW-COLOR']])
    out['record'] = dict()
    for k in ['CLOUD']: # TODO ADD OTHER CHARACTERS
        out['record'][k.lower()] = parse_char_record(data[START['SLOT_RECORD-%s'%k]:START['SLOT_RECORD-%s'%k]+SIZE['SLOT_RECORD']])
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
