#!/usr/bin/env python3
'''
Functions and classes for handling Field Files
Niema Moshiri 2019
'''
from . import NULL_BYTE,NULL_STR
from struct import unpack

# section names
SECTION_NAME = [ # Sections 1-9
    "Field Script",
    "Camera Matrix",
    "Model Loader",
    "Palette",
    "Walkmesh",
    "TileMap (Unused)",
    "Encounter",
    "Triggers",
    "Background",
]

# constants
SECTION1_HEADER_NUM_SCRIPT_POINTERS = 32

# sizes
SIZE = {
    # header sizes
    'HEADER_BLANK':                   2, # Header starts with 2 NULL bytes
    'HEADER_NUM-SECTIONS':            4, # Header: Number of Sections in File
    'HEADER_SECTION-START':           4, # Header: Section Start Position

    # properties of all sections
    'SECTION-LENGTH':                 4, # Section Length

    # Section 1 (Field Script)
    'SECTION1-HEADER_UNKNOWN':        2, # Section 1 Header: Unknown
    'SECTION1-HEADER_NUM-ENTITIES':   1, # Section 1 Header: Number of Entities
    'SECTION1-HEADER_NUM-MODELS':     1, # Section 1 Header: Number of Models
    'SECTION1-HEADER_STRINGS-OFFSET': 2, # Section 1 Header: Offset to Strings
    'SECTION1-HEADER_NUM-AKAO':       2, # Section 1 Header: Number of Akao/Tutorial Blocks
    'SECTION1-HEADER_SCALE':          2, # Section 1 Header: Field Scale
    'SECTION1-HEADER_BLANK':          6, # Section 1 Header: Blanks (NULL bytes)
    'SECTION1-HEADER_CREATOR':        8, # Section 1 Header: Field Creator
    'SECTION1-HEADER_NAME':           8, # Section 1 Header: Field Name
    'SECTION1-HEADER_ENTITY-NAME':    8, # Section 1 Header: Field Entity Name
    'SECTION1-HEADER_AKAO-OFFSET':    4, # Section 1 Header: Akao/Tutorial Block Offsets
    'SECTION1-HEADER_SCRIPT-POINTER': 2, # Section 1 Header: Entity Script Pointer
}

# error messages
ERROR_MISSING_HEADER_BLANK = "Missing header blanks"

class FieldFile:
    '''Field File class'''
    def __init__(self, filename):
        '''``FieldFile`` constructor
        Args:
            ``filename`` (``str``): The filename of the Field File
        '''
        self.filename = filename; self.file = open(filename, 'rb')
        if self.file.read(SIZE['HEADER_BLANK']) != NULL_BYTE*2:
            raise ValueError(ERROR_MISSING_HEADER_BLANK)

        # read header
        num_sections = unpack('I', self.file.read(SIZE['HEADER_NUM-SECTIONS']))[0]
        if num_sections != len(SECTION_NAME):
            raise ValueError("Expected %d sections, but file has %d" % (len(SECTION_NAME),num_sections))
        sec_starts = [unpack('I', self.file.read(SIZE['HEADER_SECTION-START']))[0] for _ in range(num_sections)]

        # read sections
        for sec in range(num_sections):
            self.file.seek(sec_starts[sec])
            length = unpack('I', self.file.read(SIZE['SECTION-LENGTH']))[0]
            tmp = self.file.read(length)

            # read Section 1: Field Script
            if sec == 0:
                # read header
                i = 0
                unknown = unpack('H', tmp[i:i+SIZE['SECTION1-HEADER_UNKNOWN']])[0]; i += SIZE['SECTION1-HEADER_UNKNOWN'] # this is always 0x0502
                num_entities = tmp[i]; i += SIZE['SECTION1-HEADER_NUM-ENTITIES']
                num_models = tmp[i]; i += SIZE['SECTION1-HEADER_NUM-MODELS']
                strings_offset = unpack('H', tmp[i:i+SIZE['SECTION1-HEADER_STRINGS-OFFSET']])[0]; i += SIZE['SECTION1-HEADER_STRINGS-OFFSET']
                num_akao = unpack('H', tmp[i:i+SIZE['SECTION1-HEADER_NUM-AKAO']])[0]; i += SIZE['SECTION1-HEADER_NUM-AKAO']
                scale = unpack('H', tmp[i:i+SIZE['SECTION1-HEADER_SCALE']])[0]; i += SIZE['SECTION1-HEADER_SCALE']
                if tmp[i:i+SIZE['SECTION1-HEADER_BLANK']] != NULL_BYTE*SIZE['SECTION1-HEADER_BLANK']:
                    raise ValueError(MISSING_HEADER_BLANK)
                i += SIZE['SECTION1-HEADER_BLANK']
                field_creator = tmp[i:i+SIZE['SECTION1-HEADER_CREATOR']].decode().strip(NULL_STR); i += SIZE['SECTION1-HEADER_CREATOR']
                field_name = tmp[i:i+SIZE['SECTION1-HEADER_NAME']].decode().strip(NULL_STR); i += SIZE['SECTION1-HEADER_NAME']
                field_entity_names = list()
                for _ in range(num_entities):
                    field_entity_names.append(tmp[i:i+SIZE['SECTION1-HEADER_ENTITY-NAME']].decode().strip(NULL_STR)); i += SIZE['SECTION1-HEADER_ENTITY-NAME']
                akao_offsets = list()
                for _ in range(num_akao):
                    akao_offsets.append(unpack('I', tmp[i:i+SIZE['SECTION1-HEADER_AKAO-OFFSET']])[0]); i += SIZE['SECTION1-HEADER_AKAO-OFFSET']
                script_pointers = list()
                for _ in range(num_entities):
                    script_pointers.append(list())
                    for __ in range(SECTION1_HEADER_NUM_SCRIPT_POINTERS):
                        script_pointers[-1].append(unpack('H', tmp[i:i+SIZE['SECTION1-HEADER_SCRIPT-POINTER']])[0]); i += SIZE['SECTION1-HEADER_SCRIPT-POINTER']
                # TODO CONTINUE HERE and maybe double check pointers
            else:
                pass
            exit()
