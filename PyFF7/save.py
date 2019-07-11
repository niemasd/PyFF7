#!/usr/bin/env python3
'''
Functions and classes for handling save files
Niema Moshiri 2019
'''
from . import BYTES_TO_FORMAT,NULL_BYTE
from .text import decode_field_text,encode_text
from struct import pack,unpack

# constants
SAVE_SLOT_SIZE = 4340
CAPACITY_STOCK_ITEM = 320
CAPACITY_STOCK_MATERIA = 200

# start offsets of various items in a save file (in bytes, with respect to start of slot data)
START = {
    # Final Fantasy VII Save Slot
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
    'SLOT_PREVIEW-GIL':       0x0020, # Save Slot: Preview: Total Gil
    'SLOT_PREVIEW-PLAYTIME':  0x0024, # Save Slot: Preview: Total Playtime
    'SLOT_PREVIEW-LOCATION':  0x0028, # Save Slot: Preview: Save Location
    'SLOT_WINDOW-COLOR-UL':   0x0048, # Save Slot: Window Color, Upper-Left Corner (RGB)
    'SLOT_WINDOW-COLOR-UR':   0x004B, # Save Slot: Window Color, Upper-Right Corner (RGB)
    'SLOT_WINDOW-COLOR-LL':   0x004E, # Save Slot: Window Color, Lower-Left Corner (RGB)
    'SLOT_WINDOW-COLOR-LR':   0x0051, # Save Slot: Window Color, Lower-Right Corner (RGB)
    'SLOT_RECORD-CLOUD':      0x0054, # Save Slot: Character Record: Cloud
    'SLOT_RECORD-BARRET':     0x00D8, # Save Slot: Character Record: Barret
    'SLOT_RECORD-TIFA':       0x015C, # Save Slot: Character Record: Tifa
    'SLOT_RECORD-AERITH':     0x01E0, # Save Slot: Character Record: Aerith
    'SLOT_RECORD-REDXIII':    0x0264, # Save Slot: Character Record: Red XIII
    'SLOT_RECORD-YUFFIE':     0x02E8, # Save Slot: Character Record: Yuffie
    'SLOT_RECORD-CAITSITH':   0x036C, # Save Slot: Character Record: Cait Sith
    'SLOT_RECORD-VINCENT':    0x03F0, # Save Slot: Character Record: Vincent
    'SLOT_RECORD-CID':        0x0474, # Save Slot: Character Record: Cid
    'SLOT_PORTRAIT1':         0x04F8, # Save Slot: Portrait 1
    'SLOT_PORTRAIT2':         0x04F9, # Save Slot: Portrait 2
    'SLOT_PORTRAIT3':         0x04FA, # Save Slot: Portrait 3
    'SLOT_BLANK1':            0x04FB, # Save Slot: Blank 1 (0xFF)
    'SLOT_STOCK-ITEM':        0x04FC, # Save Slot: Party Item Stock (2 bytes/slot, 320 slots)
    'SLOT_STOCK-MATERIA':     0x077C, # Save Slot: Party Materia Stock (4 bytes/slot, 200 slots)
    'SLOT_UNKNOWN4':          0x0A9C, # Save Slot: Unknown 4
    'SLOT_GIL':               0x0B7C, # Save Slot: Total Gil
    'SLOT_PLAYTIME':          0x0B80, # Save Slot: Total Playtime
    'SLOT_UNKNOWN5':          0x0B84, # Save Slot: Unknown 5
    'SLOT_CURR-MAP':          0x0B94, # Save Slot: Current Map
    'SLOT_CURR-LOCATION':     0x0B96, # Save Slot: Current Location
    'SLOT_UNKNOWN6':          0x0B98, # Save Slot: Unknown 6
    'SLOT_WORLD-MAP-LOC-X':   0x0B9A, # Save Slot: World Map Location: X-Coordinate
    'SLOT_WORLD-MAP-LOC-Y':   0x0B9C, # Save Slot: World Map Location: Y-Coordinate
    'SLOT_WORLD-MAP-LOC-Z':   0x0B9E, # Save Slot: World Map Location: Z-Coordinate
    'SLOT_UNKNOWN7':          0x0BA0, # Save Slot: Unknown 7
    'SLOT_PLOT-PROGRESS':     0x0BA4, # Save Slot: Plot Progression Variable
    'SLOT_UNKNOWN8':          0x0BA6, # Save Slot: Unknown 8
    'SLOT_LOVE-AERITH':       0x0BA7, # Save Slot: Love Points: Aerith
    'SLOT_LOVE-TIFA':         0x0BA8, # Save Slot: Love Points: Tifa
    'SLOT_LOVE-YUFFIE':       0x0BA9, # Save Slot: Love Points: Yuffie
    'SLOT_LOVE-BARRET':       0x0BAA, # Save Slot: Love Points: Barret
    'SLOT_UNKNOWN9':          0x0BAB, # Save Slot: Unknown 9
    'SLOT_GAMETIME-HOUR':     0x0BB4, # Save Slot: Game Timer: Hours
    'SLOT_GAMETIME-MINUTE':   0x0BB5, # Save Slot: Game Timer: Minutes
    'SLOT_GAMETIME-SECOND':   0x0BB6, # Save Slot: Game Timer: Seconds
    'SLOT_GAMETIME-TENTH':    0x0BB7, # Save Slot: Game Timer: Tenths
    'SLOT_UNKNOWN10':         0x0BB8, # Save Slot: Unknown 10
    'SLOT_NUM-BATTLES':       0x0BBC, # Save Slot: Number of Battles
    'SLOT_NUM-ESCAPES':       0x0BBE, # Save Slot: Number of Escapes
    'SLOT_UNKNOWN11':         0x0BC0, # Save Slot: Unknown 11
    'SLOT_KEY-ITEMS':         0x0BE4, # Save Slot: Key Items

    # Character Record
    'RECORD_SEPHIROTH-FLAG':     0x00, # Character Record: Vincent -> Sephiroth Flag
    'RECORD_LEVEL':              0x01, # Character Record: Level (0-99)
    'RECORD_STAT-STRENGTH':      0x02, # Character Record: Status: Strength (0-255)
    'RECORD_STAT-VITALITY':      0x03, # Character Record: Status: Vitality (0-255)
    'RECORD_STAT-MAGIC':         0x04, # Character Record: Status: Magic (0-255)
    'RECORD_STAT-SPIRIT':        0x05, # Character Record: Status: Spirit (0-255)
    'RECORD_STAT-DEXTERITY':     0x06, # Character Record: Status: Dexterity (0-255)
    'RECORD_STAT-LUCK':          0x07, # Character Record: Status: Luck (0-255)
    'RECORD_BONUS-STRENGTH':     0x08, # Character Record: Bonus: Strength
    'RECORD_BONUS-VITALITY':     0x09, # Character Record: Bonus: Vitality
    'RECORD_BONUS-MAGIC':        0x0A, # Character Record: Bonus: Magic
    'RECORD_BONUS-SPIRIT':       0x0B, # Character Record: Bonus: Spirit
    'RECORD_BONUS-DEXTERITY':    0x0C, # Character Record: Bonus: Dexterity
    'RECORD_BONUS-LUCK':         0x0D, # Character Record: Bonus: Luck
    'RECORD_LIMIT-LEVEL':        0x0E, # Character Record: Current Limit Level (1-4)
    'RECORD_LIMIT-BAR':          0x0F, # Character Record: Current Limit Bar (0 = Empty, 255 = Limit Break)
    'RECORD_NAME':               0x10, # Character Record: Name
    'RECORD_WEAPON':             0x1C, # Character Record: Equipped Weapon
    'RECORD_ARMOR':              0x1D, # Character Record: Equipped Armor
    'RECORD_ACCESSORY':          0x1E, # Character Record: Equipped Accessory
    'RECORD_FLAGS':              0x1F, # Character Record: Character Flags
    'RECORD_LIMIT-SKILLS':       0x22, # Character Record: Learned Limit Skills
    'RECORD_NUM-KILLS':          0x24, # Character Record: Number of Kills
    'RECORD_NUM-LIMIT-USES-1-1': 0x26, # Character Record: Number of Limit 1-1 Uses
    'RECORD_NUM-LIMIT-USES-2-1': 0x28, # Character Record: Number of Limit 2-1 Uses
    'RECORD_NUM-LIMIT-USES-3-1': 0x2A, # Character Record: Number of Limit 3-1 Uses
    'RECORD_HP-CURR':            0x2C, # Character Record: Current HP
    'RECORD_HP-BASE':            0x2E, # Character Record: Base HP (before materia)
    'RECORD_MP-CURR':            0x30, # Character Record: Current MP
    'RECORD_MP-BASE':            0x32, # Character Record: Base MP (before materia)
    'RECORD_UNKNOWN2':           0x34, # Character Record: Unknown 2
    'RECORD_HP-MAX':             0x38, # Character Record: Maximum HP (after materia)
    'RECORD_MP-MAX':             0x3A, # Character Record: Maximum MP (after materia)
    'RECORD_EXP_CURR':           0x3C, # Character Record: Current Experience
    'RECORD_MATERIA-WEAPON-1':   0x40, # Character Record: Weapon Materia Slot 1
    'RECORD_MATERIA-WEAPON-2':   0x41, # Character Record: Weapon Materia Slot 2
    'RECORD_MATERIA-WEAPON-3':   0x42, # Character Record: Weapon Materia Slot 3
    'RECORD_MATERIA-WEAPON-4':   0x43, # Character Record: Weapon Materia Slot 4
    'RECORD_MATERIA-WEAPON-5':   0x44, # Character Record: Weapon Materia Slot 5
    'RECORD_MATERIA-WEAPON-6':   0x45, # Character Record: Weapon Materia Slot 6
    'RECORD_MATERIA-WEAPON-7':   0x46, # Character Record: Weapon Materia Slot 7
    'RECORD_MATERIA-WEAPON-8':   0x47, # Character Record: Weapon Materia Slot 8
    'RECORD_MATERIA-ARMOR-1':    0x48, # Character Record: Armor Materia Slot 1
    'RECORD_MATERIA-ARMOR-2':    0x49, # Character Record: Armor Materia Slot 2
    'RECORD_MATERIA-ARMOR-3':    0x4A, # Character Record: Armor Materia Slot 3
    'RECORD_MATERIA-ARMOR-4':    0x4B, # Character Record: Armor Materia Slot 4
    'RECORD_MATERIA-ARMOR-5':    0x4C, # Character Record: Armor Materia Slot 5
    'RECORD_MATERIA-ARMOR-6':    0x4D, # Character Record: Armor Materia Slot 6
    'RECORD_MATERIA-ARMOR-7':    0x4E, # Character Record: Armor Materia Slot 7
    'RECORD_MATERIA-ARMOR-8':    0x4F, # Character Record: Armor Materia Slot 8
    'RECORD_UNKNOWN3':           0x50, # Character Record: Unknown 3
    'RECORD_EXP_NEXT':           0x80, # Character Record: Next Level Experience
}

# size of various items in a save file (in bytes)
SIZE = {
    # Final Fantasy VII Save Slot
    'SLOT_BLANK1':               1, # Save Slot: Blank 1 (0xFF)
    'SLOT_CHECKSUM':             4, # Save Slot: Checksum
    'SLOT_CURR-LOCATION':        2, # Save Slot: Current Location
    'SLOT_CURR-MAP':             2, # Save Slot: Current Map
    'SLOT_GAMETIME-HOUR':        1, # Save Slot: Game Timer: Hours
    'SLOT_GAMETIME-MINUTE':      1, # Save Slot: Game Timer: Minutes
    'SLOT_GAMETIME-SECOND':      1, # Save Slot: Game Timer: Seconds
    'SLOT_GAMETIME-TENTH':       1, # Save Slot: Game Timer: Tenths
    'SLOT_GIL':                  4, # Save Slot: Total Gil
    'SLOT_KEY-ITEMS':            8, # Save Slot: Key Items
    'SLOT_LOVE':                 1, # Save Slot: Love Points
    'SLOT_NUM-BATTLES':          2, # Save Slot: Number of Battles
    'SLOT_NUM-ESCAPES':          2, # Save Slot: Number of Escapes
    'SLOT_PLAYTIME':             4, # Save Slot: Total Playtime
    'SLOT_PLOT-PROGRESS':        2, # Save Slot: Plot Progression Variable
    'SLOT_PORTRAIT':             1, # Save Slot: Portrait
    'SLOT_PREVIEW-GIL':          4, # Save Slot: Preview: Amount of Gil
    'SLOT_PREVIEW-HP-CURR':      2, # Save Slot: Preview: Lead Character's Current HP
    'SLOT_PREVIEW-HP-MAX':       2, # Save Slot: Preview: Lead Character's Maximum HP
    'SLOT_PREVIEW-LEVEL':        1, # Save Slot: Preview: Lead Character's Level
    'SLOT_PREVIEW-LOCATION':    32, # Save Slot: Preview: Save Location
    'SLOT_PREVIEW-MP-CURR':      2, # Save Slot: Preview: Lead Character's Current MP
    'SLOT_PREVIEW-MP-MAX':       2, # Save Slot: Preview: Lead Character's Maximum MP
    'SLOT_PREVIEW-NAME':        16, # Save Slot: Preview: Lead Character's Name
    'SLOT_PREVIEW-PLAYTIME':     4, # Save Slot: Preview: Total Playtime
    'SLOT_PREVIEW-PORTRAIT':     1, # Save Slot: Preview: Portrait
    'SLOT_RECORD':             132, # Save Slot: Character Record
    'SLOT_STOCK-ITEM':         640, # Save Slot: Party Item Stock (2 bytes/slot, 320 slots)
    'SLOT_STOCK-ITEM-SINGLE':    2, # Save Slot: Party Item Stock: Single Item
    'SLOT_STOCK-MATERIA':      800, # Save Slot: Party Materia Stock (4 bytes/slot, 200 slots)
    'SLOT_STOCK-MATERIA-SINGLE': 4, # Save Slot: Party Materia Stock: Single Item
    'SLOT_UNKNOWN4':           224, # Save Slot: Unknown 4
    'SLOT_UNKNOWN5':            16, # Save Slot: Unknown 5
    'SLOT_UNKNOWN6':             2, # Save Slot: Unknown 6
    'SLOT_UNKNOWN7':             4, # Save Slot: Unknown 7
    'SLOT_UNKNOWN8':             1, # Save Slot: Unknown 8
    'SLOT_UNKNOWN9':             9, # Save Slot: Unknown 9
    'SLOT_UNKNOWN10':            4, # Save Slot: Unknown 10
    'SLOT_UNKNOWN11':           57, # Save Slot: Unknown 11
    'SLOT_WINDOW-COLOR':         3, # Save Slot: Window Color (RGB)
    'SLOT_WORLD-MAP-LOC':        2, # Save Slot: World Map Location Coordinate

    # Character Record
    'RECORD_ACCESSORY':          1, # Character Record: Accessory
    'RECORD_ARMOR':              1, # Character Record: Armor
    'RECORD_BONUS':              1, # Character Record: Bonus
    'RECORD_EXP_CURR':           4, # Character Record: Current Experience
    'RECORD_EXP_NEXT':           4, # Character Record: Next Level Experience
    'RECORD_FLAGS':              3, # Character Record: Character Flags
    'RECORD_HP-BASE':            2, # Character Record: Base HP (before materia)
    'RECORD_HP-CURR':            2, # Character Record: Current HP
    'RECORD_HP-MAX':             2, # Character Record: Maximum HP (after materia)
    'RECORD_LEVEL':              1, # Character Record: Level (0-99)
    'RECORD_LIMIT-BAR':          1, # Character Record: Current Limit Bar (0 = Empty, 255 = Limit Break)
    'RECORD_LIMIT-LEVEL':        1, # Character Record: Current Limit Level (1-4)
    'RECORD_LIMIT-SKILLS':       2, # Character Record: Learned Limit Skills
    'RECORD_MATERIA':            1, # Character Record: Weapon/Armor Materia
    'RECORD_MP-BASE':            2, # Character Record: Base MP (before materia)
    'RECORD_MP-CURR':            2, # Character Record: Current MP
    'RECORD_MP-MAX':             2, # Character Record: Maximum MP (after materia)
    'RECORD_NAME':              12, # Character Record: Name
    'RECORD_NUM-KILLS':          2, # Character Record: Number of Kills
    'RECORD_NUM-LIMIT-USES':     2, # Character Record: Number of Limit Uses
    'RECORD_SEPHIROTH-FLAG':     1, # Character Record: Vincent -> Sephiroth Flag
    'RECORD_STAT':               1, # Character Record: Status
    'RECORD_UNKNOWN2':           4, # Character Record: Unknown 2
    'RECORD_UNKNOWN3':          48, # Character Record: Unknown 3
    'RECORD_WEAPON':             1, # Character Record: Equipped Weapon
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
ERROR_INVALID_CHECKSUM = "Invalid save slot checksum"
ERROR_INVALID_SAVE_FILE = "Invalid save file"

def compute_checksum(slot_data):
    '''Compute the checksum of a given save slot

    Args:
        ``slot_data`` (``bytes``): The input save slot's packed data (everything after the original checksum)

    Returns:
        ``int``: The checksum of ``slot_data``
    '''
    r = 0xFFFF; pbit = 0x8000
    for t in slot_data:
        r ^= (t << 8)
        for _ in range(8):
            if r & pbit:
                r = (r << 1) ^ 0x1021
            else:
                r <<= 1
        r &= 0xFFFF
    return (r ^ 0xFFFF) & 0xFFFF

def unpack_color(data):
    '''Parse the bytes of an RGB color

    Args:
        ``data`` (``bytes``): The input RGB color bytes

    Returns:
        ``tuple`` of ``int``: The resulting RGB color
    '''
    if len(data) != SIZE['SLOT_WINDOW-COLOR']:
        raise ValueError("Invalid color data length: %d bytes" % len(data))
    return (data[0], data[1], data[2])

def pack_color(c):
    '''Pack an RGB color into 3 bytes

    Args:
        ``c`` (``tuple`` of ``int``): The input RGB color

    Returns:
        ``bytes``: The resulting packed data
    '''
    return pack('B',c[0]) + pack('B',c[1]) + pack('B',c[2])

def unpack_char_flags(data):
    '''Parse the bytes of Character Flags (in Character Record)

    Args:
        ``data`` (``bytes``): The input character flags bytes

    Returns:
        TODO: The resulting character flags
    '''
    if len(data) != SIZE['RECORD_FLAGS']:
        raise ValueError("Invalid character flags data length: %d" % len(data))
    return data # TODO ACTUALLY PARSE

def pack_char_flags(flags):
    '''Pack Character Flags (in Character Record) into bytes

    Args:
        ``flags`` (TODO): The input character flags

    Returns:
        ``bytes``: The resulting packed data
    '''
    return flags # TODO ACTUALLY PACK ONCE I'VE IMPLEMENTED unpack_char_flags

def unpack_char_limit_skills(data):
    '''Parse the bytes of Learned Limit Skills

    Args:
        ``data`` (``bytes``): The input Learned Limit Skills bytes

    Returns:
        TODO: The resulting Learned Limit Skills
    '''
    if len(data) != SIZE['RECORD_LIMIT-SKILLS']:
        raise ValueError("Invalid learned limit skills data length: %d" % len(data))
    return data

def pack_char_limit_skills(skills):
    '''Pack Learned Limit Skills into bytes

    Args:
        ``skills`` (TODO): The input Learned Limit Skills

    Returns:
        ``bytes``: The resulting packed data
    '''
    return skills # TODO ACTUALLY PACK ONCE I'VE IMPLEMENTED unpack_char_limit_skills

def unpack_char_record(data):
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
    out['flags'] = unpack_char_flags(data[START['RECORD_FLAGS']:START['RECORD_FLAGS']+SIZE['RECORD_FLAGS']])
    out['limit_skills'] = unpack_char_limit_skills(data[START['RECORD_LIMIT-SKILLS']:START['RECORD_LIMIT-SKILLS']+SIZE['RECORD_LIMIT-SKILLS']])
    out['num_kills'] = unpack('H', data[START['RECORD_NUM-KILLS']:START['RECORD_NUM-KILLS']+SIZE['RECORD_NUM-KILLS']])[0]
    for i in [1,2,3]:
        out['num_limit_uses_%d_1'%i] = unpack('H', data[START['RECORD_NUM-LIMIT-USES-%d-1'%i]:START['RECORD_NUM-LIMIT-USES-%d-1'%i]+SIZE['RECORD_NUM-LIMIT-USES']])[0]
    out['curr_hp'] = unpack('H', data[START['RECORD_HP-CURR']:START['RECORD_HP-CURR']+SIZE['RECORD_HP-CURR']])[0]
    out['base_hp'] = unpack('H', data[START['RECORD_HP-BASE']:START['RECORD_HP-BASE']+SIZE['RECORD_HP-BASE']])[0]
    out['curr_mp'] = unpack('H', data[START['RECORD_MP-CURR']:START['RECORD_MP-CURR']+SIZE['RECORD_MP-CURR']])[0]
    out['base_mp'] = unpack('H', data[START['RECORD_MP-BASE']:START['RECORD_MP-BASE']+SIZE['RECORD_MP-BASE']])[0]
    out['unknown2'] = unpack('I', data[START['RECORD_UNKNOWN2']:START['RECORD_UNKNOWN2']+SIZE['RECORD_UNKNOWN2']])[0]
    out['max_hp'] = unpack('H', data[START['RECORD_HP-MAX']:START['RECORD_HP-MAX']+SIZE['RECORD_HP-MAX']])[0]
    out['max_mp'] = unpack('H', data[START['RECORD_MP-MAX']:START['RECORD_MP-MAX']+SIZE['RECORD_MP-MAX']])[0]
    out['exp_curr'] = unpack('I', data[START['RECORD_EXP_CURR']:START['RECORD_EXP_CURR']+SIZE['RECORD_EXP_CURR']])[0]
    out['materia'] = {'weapon':list(),'armor':list()}
    for k in ['WEAPON','ARMOR']:
        for i in range(1,9): # 1 through 8
            out['materia'][k.lower()].append(unpack('B', data[START['RECORD_MATERIA-%s-%d'%(k,i)]:START['RECORD_MATERIA-%s-%d'%(k,i)]+SIZE['RECORD_MATERIA']])[0])
    out['unknown3'] = data[START['RECORD_UNKNOWN3']:START['RECORD_UNKNOWN3']+SIZE['RECORD_UNKNOWN3']]
    out['exp_next'] = unpack('I', data[START['RECORD_EXP_NEXT']:START['RECORD_EXP_NEXT']+SIZE['RECORD_EXP_NEXT']])[0]
    return out

def pack_char_record(rec):
    '''Pack a Character Record into bytes

    Args:
        ``rec`` (``dict``): The input character record

    Returns:
        ``bytes``: The resulting packed data
    '''
    out = bytearray()
    out += pack('B', rec['sephiroth_flag'])
    out += pack('B', rec['level'])
    for k in ['strength', 'vitality', 'magic', 'spirit', 'dexterity', 'luck']:
        out += pack('B', rec['status'][k])
    for k in ['strength', 'vitality', 'magic', 'spirit', 'dexterity', 'luck']:
        out += pack('B', rec['bonus'][k])
    out += pack('B', rec['limit_level'])
    out += pack('B', rec['limit_bar'])
    tmp = encode_text(rec['name']); out += tmp; out += NULL_BYTE*(SIZE['RECORD_NAME']-len(tmp))
    for k in ['weapon', 'armor', 'accessory']:
        out += pack('B', rec[k])
    out += pack_char_flags(rec['flags'])
    out += pack_char_limit_skills(rec['limit_skills'])
    out += pack('H', rec['num_kills'])
    for i in [1,2,3]:
        out += pack('H', rec['num_limit_uses_%d_1'%i])
    for k in ['curr_hp', 'base_hp', 'curr_mp', 'base_mp']:
        out += pack('H', rec[k])
    out += pack('I', rec['unknown2'])
    for k in ['max_hp','max_mp']:
        out += pack('H', rec[k])
    out += pack('I', rec['exp_curr'])
    for k in ['weapon', 'armor']:
        for v in rec['materia'][k]:
            out += pack('B', v)
    out += rec['unknown3']
    out += pack('I', rec['exp_next'])
    return out

def unpack_stock_item(data):
    '''Parse the bytes of an item stock

    Args:
        ``data`` (``bytes``): The input item stock data

    Returns:
        ``list`` of ``tuple``: The parsed item stock as (item, quantity) tuples, where items are represented as (item ID, even/odd) tuples, where even is 0 and odd is 1
    '''
    if len(data) != SIZE['SLOT_STOCK-ITEM']:
        raise ValueError("Invalid item stock size: %d" % len(data))
    return [((data[i], data[i+1]%2), int(data[i+1]/2)) for i in range(0, len(data), SIZE['SLOT_STOCK-ITEM-SINGLE'])]

def pack_stock_item(items):
    '''Pack an item stock into bytes

    Args:
        ``items`` (``list`` of ``tuple``): An item stock as (item, quantity) tuples, where items are represented as (item ID, even/odd) tuples, where even is 0 and odd is 1

    Returns:
        ``bytes``: The resulting packed data
    '''
    if len(items) != CAPACITY_STOCK_ITEM:
        raise ValueError("Invalid item stock length: %d" % len(items))
    out = bytearray()
    for ((ID, even_odd), quantity) in items:
        if ID == 0xFF and even_odd == 1: # empty slot
            out += b'\xFF\xFF'
        else:
            out += pack('B', ID); out += pack('B', 2*quantity + even_odd)
    return out

def unpack_stock_materia(data):
    '''Parse the bytes of a materia stock

    Args:
        ``data`` (``bytes``): The input materia stock data

    Returns:
        ``list`` of `tuple``: The parsed materia stock as (materia ID, AP) tuples
    '''
    if len(data) != SIZE['SLOT_STOCK-MATERIA']:
        raise ValueError("Invalid materia stock size: %d" % len(data))
    return [(data[i], unpack('I', data[i+1:i+SIZE['SLOT_STOCK-MATERIA-SINGLE']]+NULL_BYTE)[0]) for i in range(0, len(data), SIZE['SLOT_STOCK-MATERIA-SINGLE'])]

def pack_stock_materia(materia):
    '''Pack a materia stock into bytes

    Args:
        ``materia`` (``list`` of ``tuple``): A materia stock as (materia ID, AP) tuples

    Returns:
        ``bytes``: The resulting packed data
    '''
    if len(materia) != CAPACITY_STOCK_MATERIA:
        raise ValueError("Invalid materia stock length: %d" % len(materia))
    out = bytearray()
    for ID,AP in materia:
        if ID == 0xFF and AP == 0xFFFFFF: # empty slot
            out += b'\xFF\xFF\xFF\xFF'
        else:
            out += pack('B', ID); out += pack('I', AP)[:SIZE['SLOT_STOCK-MATERIA-SINGLE']-1]
    return out

def unpack_slot_data(data):
    '''Parse the bytes of a save slot

    Args:
        ``data`` (``bytes``): The input save slot data

    Returns:
        ``dict``: The parsed save slot
    '''
    if len(data) != SAVE_SLOT_SIZE:
        raise ValueError(ERROR_INVALID_SAVE_FILE)
    out = dict()
    out['checksum'] = unpack('I', data[START['SLOT_CHECKSUM']:START['SLOT_CHECKSUM']+SIZE['SLOT_CHECKSUM']])[0] # TODO REMOVE WHEN I FINISH PARSING SAVE SLOT
    if out['checksum'] != compute_checksum(data[START['SLOT_CHECKSUM']+SIZE['SLOT_CHECKSUM']:]):
        raise ValueError(ERROR_INVALID_CHECKSUM)
    out['preview'] = dict()
    out['preview']['level'] = unpack('B', data[START['SLOT_PREVIEW-LEVEL']:START['SLOT_PREVIEW-LEVEL']+SIZE['SLOT_PREVIEW-LEVEL']])[0]
    out['preview']['party'] = [unpack('B', data[START['SLOT_PREVIEW-PORTRAIT%d'%i]:START['SLOT_PREVIEW-PORTRAIT%d'%i]+SIZE['SLOT_PREVIEW-PORTRAIT']])[0] for i in [1,2,3]]
    out['preview']['name'] = decode_field_text(data[START['SLOT_PREVIEW-NAME']:START['SLOT_PREVIEW-NAME']+SIZE['SLOT_PREVIEW-NAME']])
    out['preview']['curr_hp'] = unpack('H', data[START['SLOT_PREVIEW-HP-CURR']:START['SLOT_PREVIEW-HP-CURR']+SIZE['SLOT_PREVIEW-HP-CURR']])[0]
    out['preview']['max_hp'] = unpack('H', data[START['SLOT_PREVIEW-HP-MAX']:START['SLOT_PREVIEW-HP-MAX']+SIZE['SLOT_PREVIEW-HP-MAX']])[0]
    out['preview']['curr_mp'] = unpack('H', data[START['SLOT_PREVIEW-MP-CURR']:START['SLOT_PREVIEW-MP-CURR']+SIZE['SLOT_PREVIEW-MP-CURR']])[0]
    out['preview']['max_mp'] = unpack('H', data[START['SLOT_PREVIEW-MP-MAX']:START['SLOT_PREVIEW-MP-MAX']+SIZE['SLOT_PREVIEW-MP-MAX']])[0]
    out['preview']['gil'] = unpack('I', data[START['SLOT_PREVIEW-GIL']:START['SLOT_PREVIEW-GIL']+SIZE['SLOT_PREVIEW-GIL']])[0]
    out['preview']['playtime'] = unpack('I', data[START['SLOT_PREVIEW-PLAYTIME']:START['SLOT_PREVIEW-PLAYTIME']+SIZE['SLOT_PREVIEW-PLAYTIME']])[0]
    out['preview']['location'] = decode_field_text(data[START['SLOT_PREVIEW-LOCATION']:START['SLOT_PREVIEW-LOCATION']+SIZE['SLOT_PREVIEW-LOCATION']])
    out['window_color'] = {k1:unpack_color(data[START['SLOT_WINDOW-COLOR-%s'%k2]:START['SLOT_WINDOW-COLOR-%s'%k2]+SIZE['SLOT_WINDOW-COLOR']]) for k1,k2 in [('upper_left','UL'), ('upper_right','UR'), ('lower_left','LL'), ('lower_right','LR')]}
    out['record'] = {k.lower():unpack_char_record(data[START['SLOT_RECORD-%s'%k]:START['SLOT_RECORD-%s'%k]+SIZE['SLOT_RECORD']]) for k in ['CLOUD', 'BARRET', 'TIFA', 'AERITH', 'REDXIII', 'YUFFIE', 'CAITSITH', 'VINCENT', 'CID']}
    out['party'] = [unpack('B', data[START['SLOT_PORTRAIT%d'%i]:START['SLOT_PORTRAIT%d'%i]+SIZE['SLOT_PORTRAIT']])[0] for i in [1,2,3]]
    out['stock'] = dict()
    out['stock']['item'] = unpack_stock_item(data[START['SLOT_STOCK-ITEM']:START['SLOT_STOCK-ITEM']+SIZE['SLOT_STOCK-ITEM']])
    out['stock']['materia'] = unpack_stock_materia(data[START['SLOT_STOCK-MATERIA']:START['SLOT_STOCK-MATERIA']+SIZE['SLOT_STOCK-MATERIA']])
    out['unknown4'] = data[START['SLOT_UNKNOWN4']:START['SLOT_UNKNOWN4']+SIZE['SLOT_UNKNOWN4']]
    out['gil'] = unpack('I', data[START['SLOT_GIL']:START['SLOT_GIL']+SIZE['SLOT_GIL']])[0]
    out['playtime'] = unpack('I', data[START['SLOT_PLAYTIME']:START['SLOT_PLAYTIME']+SIZE['SLOT_PLAYTIME']])[0]
    out['unknown5'] = data[START['SLOT_UNKNOWN5']:START['SLOT_UNKNOWN5']+SIZE['SLOT_UNKNOWN5']]
    out['curr_map'] = unpack('H', data[START['SLOT_CURR-MAP']:START['SLOT_CURR-MAP']+SIZE['SLOT_CURR-MAP']])[0]
    out['curr_location'] = unpack('H', data[START['SLOT_CURR-LOCATION']:START['SLOT_CURR-LOCATION']+SIZE['SLOT_CURR-LOCATION']])[0]
    out['unknown6'] = unpack('H', data[START['SLOT_UNKNOWN6']:START['SLOT_UNKNOWN6']+SIZE['SLOT_UNKNOWN6']])[0]
    out['world_map_location'] = [unpack('H', data[START['SLOT_WORLD-MAP-LOC-%s'%k]:START['SLOT_WORLD-MAP-LOC-%s'%k]+SIZE['SLOT_WORLD-MAP-LOC']])[0] for k in ['X','Y','Z']]
    out['unknown7'] = unpack('I', data[START['SLOT_UNKNOWN7']:START['SLOT_UNKNOWN7']+SIZE['SLOT_UNKNOWN7']])[0]
    out['plot_progress'] = unpack('H', data[START['SLOT_PLOT-PROGRESS']:START['SLOT_PLOT-PROGRESS']+SIZE['SLOT_PLOT-PROGRESS']])[0]
    out['unknown8'] = unpack('B', data[START['SLOT_UNKNOWN8']:START['SLOT_UNKNOWN8']+SIZE['SLOT_UNKNOWN8']])[0]
    out['love'] = {k.lower():unpack('B', data[START['SLOT_LOVE-%s'%k]:START['SLOT_LOVE-%s'%k]+SIZE['SLOT_LOVE']])[0] for k in ['AERITH','TIFA','YUFFIE','BARRET']}
    out['unknown9'] = data[START['SLOT_UNKNOWN9']:START['SLOT_UNKNOWN9']+SIZE['SLOT_UNKNOWN9']]
    out['gametime'] = [unpack('B', data[START['SLOT_GAMETIME-%s'%k]:START['SLOT_GAMETIME-%s'%k]+SIZE['SLOT_GAMETIME-%s'%k]])[0] for k in ['HOUR','MINUTE','SECOND','TENTH']]
    out['unknown10'] = unpack('I', data[START['SLOT_UNKNOWN10']:START['SLOT_UNKNOWN10']+SIZE['SLOT_UNKNOWN10']])[0]
    out['num_battles'] = unpack('H', data[START['SLOT_NUM-BATTLES']:START['SLOT_NUM-BATTLES']+SIZE['SLOT_NUM-BATTLES']])[0]
    out['num_escapes'] = unpack('H', data[START['SLOT_NUM-ESCAPES']:START['SLOT_NUM-ESCAPES']+SIZE['SLOT_NUM-ESCAPES']])[0]
    out['unknown11'] = data[START['SLOT_UNKNOWN11']:START['SLOT_UNKNOWN11']+SIZE['SLOT_UNKNOWN11']]
    return out

def pack_slot_data(slot):
    '''Pack an unpacked save slot into bytes

    Args:
        ``lot`` (``dict``): The input unpacked save slot

    Returns:
        ``bytes``: The resulting packed data
    '''
    out = bytearray(); d = slot['data']
    out += slot['header']
    #out += pack('I', compute_checksum(slot)) # recompute checksum in case any modifications were made
    out += pack('I', d['checksum']) # TODO remove when checksum computing is fixed
    out += pack('B', d['preview']['level'])
    for ch in d['preview']['party']:
        out += pack('B', ch)
    tmp = encode_text(d['preview']['name']); out += tmp; out += NULL_BYTE*(SIZE['SLOT_PREVIEW-NAME']-len(tmp))
    out += pack('H', d['preview']['curr_hp'])
    out += pack('H', d['preview']['max_hp'])
    out += pack('H', d['preview']['curr_mp'])
    out += pack('H', d['preview']['max_mp'])
    out += pack('I', d['preview']['gil'])
    out += pack('I', d['preview']['playtime'])
    tmp = encode_text(d['preview']['location']); out += tmp; out += NULL_BYTE*(SIZE['SLOT_PREVIEW-LOCATION']-len(tmp))
    for loc in ['upper_left', 'upper_right', 'lower_left', 'lower_right']:
        out += pack_color(d['window_color'][loc])
    for ch in ['cloud', 'barret', 'tifa', 'aerith', 'redxiii', 'yuffie', 'caitsith', 'vincent', 'cid']:
        out += pack_char_record(d['record'][ch])
    for ch in d['party']:
        out += pack('B', ch)
    out += b'\xFF'
    out += pack_stock_item(d['stock']['item'])
    out += pack_stock_materia(d['stock']['materia'])
    out += d['unknown4']
    out += pack('I', d['gil'])
    out += pack('I', d['playtime'])
    out += d['unknown5']
    out += pack('H', d['curr_map'])
    out += pack('H', d['curr_location'])
    out += pack('H', d['unknown6'])
    for v in d['world_map_location']:
        out += pack('H', v)
    out += pack('I', d['unknown7'])
    out += pack('H', d['plot_progress'])
    out += pack('B', d['unknown8'])
    for ch in ['aerith','tifa','yuffie','barret']:
        out += pack('B', d['love'][ch])
    out += d['unknown9']
    for v in d['gametime']:
        out += pack('B', v)
    out += pack('I', d['unknown10'])
    out += pack('H', d['num_battles'])
    out += pack('H', d['num_escapes'])
    out += d['unknown11']
    #out += slot['footer'] # TODO UNCOMMENT WHEN FINISHED PACKING SAVE SLOT DATA
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
            slot['data'] = unpack_slot_data(data[ind:ind+SAVE_SLOT_SIZE]); ind += SAVE_SLOT_SIZE
            slot['footer'] = data[ind:ind+prop['slot_footer_size']]; ind += prop['slot_footer_size']
            self.save_slots.append(slot)

        # VALIDITY CHECK, TODO REMOVE WHEN DONE
        self_bytes = self.get_bytes(); data_bytes = bytearray(data)
        for i in range(len(self.save_slots)):
            # fix preview name
            null = False
            start = len(self.header) + i*(prop['slot_header_size']+SAVE_SLOT_SIZE+prop['slot_footer_size']) + 8
            for j in range(start, start + 16):
                if null:
                    data_bytes[j] = 0
                elif data_bytes[j] == 255:
                    null = True

            # fix preview location
            null = False
            start = len(self.header) + i*(prop['slot_header_size']+SAVE_SLOT_SIZE+prop['slot_footer_size']) + 0x28
            for j in range(start, start + 32):
                if null:
                    data_bytes[j] = 0
                elif data_bytes[j] == 255:
                    null = True

            # fix character names
            for j in range(len(self.save_slots[0]['data']['record'])):
                null = False
                start = len(self.header) + i*(prop['slot_header_size']+SAVE_SLOT_SIZE+prop['slot_footer_size']) + 0x54 + j*132 + 0x10
                for k in range(start, start+12):
                    if null:
                        data_bytes[k] = 0
                    elif data_bytes[k] == 255:
                        null = True
        assert self_bytes == data_bytes[:len(self_bytes)]

    def get_bytes(self):
        '''Return the bytes encoding of this save file

        Returns:
            ``bytes``: The data encoding this save file
        '''
        out = bytearray()
        out += self.header
        for slot in self.save_slots:
            out += pack_slot_data(slot)
            break # TODO REMOVE WHEN FINISHED PACK SLOT DATA
        return out

    def __len__(self):
        return len(self.save_slots)

    def __iter__(self):
        for s in self.save_slots:
            yield s
