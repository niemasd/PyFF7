#!/usr/bin/env python3
'''
Functions and classes for handling Field Files
Niema Moshiri 2019
'''
from . import NULL_BYTE,NULL_STR
from .lzss import decompress_lzss
from .text import decode_field_text
from struct import pack,unpack

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
DEFAULT_VERSION = 0x0502
MAX_NUM_STRINGS = 256
SECTION1_HEADER_NUM_SCRIPTS_PER_ACTOR = 32
SECTION2_AXES = ('x','y','z')
SECTION2_VECTOR_DIV = 4096.
SECTION2_NUM_DIMENSIONS = 3
STRING_TERMINATOR = b'\xff'

# OP codes
OP = [
    ("ret", 0),    ("req", 2),    ("reqsw", 2),  ("reqew", 2),  ("preq", 2),   ("prqsw", 2),  ("prqew", 2),  ("retto", 1),   # 0x00..0x07
    ("join", 1),   ("split", 14), ("sptye", 5),  ("gptye", 5),  ("", -1),      ("", -1),      ("dskcg", 1),  ("spcal", 0),   # 0x08..0x0f
    ("skip", 1),   ("lskip", 2),  ("back", 1),   ("lback", 2),  ("if", 5),     ("lif", 6),    ("if2", 7),    ("lif2", 8),    # 0x10..0x17
    ("if2", 7),    ("lif2", 8),   ("", -1),      ("", -1),      ("", -1),      ("", -1),      ("", -1),      ("", -1),       # 0x18..0x1f
    ("mgame", 10), ("tutor", 1),  ("btmd2", 4),  ("btrlt", 2),  ("wait", 2),   ("nfade", 8),  ("blink", 1),  ("bgmovie", 1), # 0x20..0x27
    ("kawai", 0),  ("kawiw", 0),  ("pmova", 1),  ("slip", 1),   ("bgdph", 4),  ("bgscr", 6),  ("wcls!", 1),  ("wsizw", 9),   # 0x28..0x2f
    ("key!", 3),   ("keyon", 3),  ("keyof", 3),  ("uc", 1),     ("pdira", 1),  ("ptura", 3),  ("wspcl", 4),  ("wnumb", 7),   # 0x30..0x37
    ("sttim", 5),  ("gold+", 5),  ("gold-", 5),  ("chgld", 3),  ("hmpmx", 0),  ("hmpmx", 0),  ("mhmmx", 0),  ("hmpmx", 0),   # 0x38..0x3f
    ("mes", 2),    ("mpara", 4),  ("mpra2", 5),  ("mpnam", 1),  ("", -1),      ("mp+", 4),    ("", -1),      ("mp-", 4),     # 0x40..0x47
    ("ask", 6),    ("menu", 3),   ("menu", 1),   ("btltb", 1),  ("", -1),      ("hp+", 4),    ("", -1),      ("hp-", 4),     # 0x48..0x4f
    ("wsize", 9),  ("wmove", 5),  ("wmode", 3),  ("wrest", 1),  ("wclse", 1),  ("wrow", 2),   ("gwcol", 6),  ("swcol", 6),   # 0x50..0x57
    ("stitm", 4),  ("dlitm", 4),  ("ckitm", 4),  ("smtra", 6),  ("dmtra", 7),  ("cmtra", 9),  ("shake", 7),  ("wait", 0),    # 0x58..0x5f
    ("mjump", 9),  ("scrlo", 1),  ("scrlc", 4),  ("scrla", 5),  ("scr2d", 5),  ("scrcc", 0),  ("scr2dc", 8), ("scrlw", 0),   # 0x60..0x67
    ("scr2dl", 8), ("mpdsp", 1),  ("vwoft", 6),  ("fade", 8),   ("fadew", 0),  ("idlck", 3),  ("lstmp", 2),  ("scrlp", 5),   # 0x68..0x6f
    ("batle", 3),  ("btlon", 1),  ("btlmd", 2),  ("pgtdr", 3),  ("getpc", 3),  ("pxyzi", 7),  ("plus!", 3),  ("pls2!", 4),   # 0x70..0x77
    ("mins!", 3),  ("mns2!", 4),  ("inc!", 2),   ("inc2!", 2),  ("dec!", 2),   ("dec2!", 2),  ("tlkon", 1),  ("rdmsd", 2),   # 0x78..0x7f
    ("set", 3),    ("set2", 4),   ("biton", 3),  ("bitof", 3),  ("bitxr", 3),  ("plus", 3),   ("plus2", 4),  ("minus", 3),   # 0x80..0x87
    ("mins2", 4),  ("mul", 3),    ("mul2", 4),   ("div", 3),    ("div2", 4),   ("remai", 3),  ("rema2", 4),  ("and", 3),     # 0x88..0x8f
    ("and2", 4),   ("or", 3),     ("or2", 4),    ("xor", 3),    ("xor2", 4),   ("inc", 2),    ("inc2", 2),   ("dec", 2),     # 0x90..0x97
    ("dec2", 2),   ("randm", 2),  ("lbyte", 3),  ("hbyte", 4),  ("2byte", 5),  ("setx", 6),   ("getx", 6),   ("srchx", 10),  # 0x98..0x9f
    ("pc", 1),     ("char", 1),   ("dfanm", 2),  ("anime", 2),  ("visi", 1),   ("xyzi", 10),  ("xyi", 8),    ("xyz", 8),     # 0xa0..0xa7
    ("move", 5),   ("cmove", 5),  ("mova", 1),   ("tura", 3),   ("animw", 0),  ("fmove", 5),  ("anime", 2),  ("anim!", 2),   # 0xa8..0xaf
    ("canim", 4),  ("canm!", 4),  ("msped", 3),  ("dir", 2),    ("turnr", 5),  ("turn", 5),   ("dira", 1),   ("gtdir", 3),   # 0xb0..0xb7
    ("getaxy", 4), ("getai", 3),  ("anim!", 2),  ("canim", 4),  ("canm!", 4),  ("asped", 3),  ("", -1),      ("cc", 1),      # 0xb8..0xbf
    ("jump", 10),  ("axyzi", 7),  ("lader", 14), ("ofstd", 11), ("ofstw", 0),  ("talkR", 2),  ("slidR", 2),  ("solid", 1),   # 0xc0..0xc7
    ("prtyp", 1),  ("prtym", 1),  ("prtye", 3),  ("prtyq", 2),  ("membq", 2),  ("mmb+-", 2),  ("mmblk", 1),  ("mmbuk", 1),   # 0xc8..0xcf
    ("line", 12),  ("linon", 1),  ("mpjpo", 1),  ("sline", 15), ("sin", 9),    ("cos", 9),    ("tlkR2", 3),  ("sldR2", 3),   # 0xd0..0xd7
    ("pmjmp", 2),  ("pmjmp", 0),  ("akao2", 14), ("fcfix", 1),  ("ccanm", 3),  ("animb", 0),  ("turnw", 0),  ("mppal", 10),  # 0xd8..0xdf
    ("bgon", 3),   ("bgoff", 3),  ("bgrol", 2),  ("bgrol", 2),  ("bgclr", 2),  ("stpal", 4),  ("ldpal", 4),  ("cppal", 4),   # 0xe0..0xe7
    ("rtpal", 6),  ("adpal", 9),  ("mppal", 9),  ("stpls", 4),  ("ldpls", 4),  ("cppal", 7),  ("rtpal", 7),  ("adpal", 10),  # 0xe8..0xef
    ("music", 1),  ("se", 4),     ("akao", 13),  ("musvt", 1),  ("musvm", 1),  ("mulck", 1),  ("bmusc", 1),  ("chmph", 3),   # 0xf0..0xf7
    ("pmvie", 1),  ("movie", 0),  ("mvief", 2),  ("mvcam", 1),  ("fmusc", 1),  ("cmusc", 5),  ("chmst", 2),  ("gmovr", 0),   # 0xf8..0xff
]

# SPECIAL OP codes
SPECIAL_OP_CODES = {
    0xF5: ("arrow", 1), # Special: Arrow Switch
    0xF6: ("pname", 4),
    0xF7: ("gmspd", 2),
    0xF8: ("smspd", 2), # Special: Set Field Message Speed
    0xF9: ("flmat", 0), # Special: Fill Materia
    0xFA: ("flitm", 0), # Special: Fill Items
    0xFB: ("btlck", 1), # Special: Battle Lock
    0xFC: ("mvlck", 1), # Special: Movie Lock
    0xFD: ("spcnm", 2), # Special: Change Character Name
    0xFE: ("rsglb", 0), # Special: Reset Game and ?
    0xFF: ("clitm", 0), # Special: Clear Items
}

# important OP codes
OP_KAWAI   = 0x28 # Character Graphics Opcode (Multibyte sequence)
OP_RET     = 0x00 # Return from request / Halt
OP_SPECIAL = 0x0F # Special Opcode (Multibyte sequence)

# sizes
SIZE = {
    # header sizes
    'HEADER_BLANK':                   2, # Header starts with 2 NULL bytes
    'HEADER_NUM-SECTIONS':            4, # Header: Number of Sections in File
    'HEADER_SECTION-START':           4, # Header: Section Start Position

    # properties of all sections
    'SECTION-LENGTH':                 4, # Section Length

    # Section 1 (Field Script)
    'SECTION1-HEADER_VERSION':        2, # Section 1 Header: Version
    'SECTION1-HEADER_NUM-ACTORS':     1, # Section 1 Header: Number of Actors
    'SECTION1-HEADER_NUM-MODELS':     1, # Section 1 Header: Number of Models
    'SECTION1-HEADER_STRINGS-OFFSET': 2, # Section 1 Header: String Table Offset
    'SECTION1-HEADER_NUM-AKAO':       2, # Section 1 Header: Number of Akao/Tutorial Blocks
    'SECTION1-HEADER_SCALE':          2, # Section 1 Header: Field Scale
    'SECTION1-HEADER_BLANK':          6, # Section 1 Header: Blanks (NULL bytes)
    'SECTION1-HEADER_CREATOR':        8, # Section 1 Header: Field Creator
    'SECTION1-HEADER_NAME':           8, # Section 1 Header: Field Name
    'SECTION1-HEADER_ACTOR-NAME':     8, # Section 1 Header: Actor Name
    'SECTION1-HEADER_AKAO-OFFSET':    4, # Section 1 Header: Akao/Tutorial Block Offsets
    'SECTION1-HEADER_ACTOR-SCRIPT':   2, # Section 1 Header: Actor Script
    'SECTION1_NUM-STRINGS':           2, # Section 1: Number of Strings in String Offset Table
    'SECTION1_STRING-OFFSET':         2, # Section 1: String Offset

    # Section 2 (Camera Matrix)
    'SECTION2-ENTRY_VECTOR-VALUE':    2, # Section 2 Entry: Value in an Axis Vector
    'SECTION2-ENTRY_SPACE-POSITION':  4, # Section 2 Entry: Camera Space Position in an Axis
    'SECTION2-ENTRY_BLANK':           4, # Section 2 Entry: Blank
    'SECTION2-ENTRY_ZOOM':            2, # Section 2 Entry: Zoom
}
SIZE['SECTION2-ENTRY'] = len(SECTION2_AXES)*SECTION2_NUM_DIMENSIONS*SIZE['SECTION2-ENTRY_VECTOR-VALUE'] + SIZE['SECTION2-ENTRY_VECTOR-VALUE'] + len(SECTION2_AXES)*SIZE['SECTION2-ENTRY_SPACE-POSITION'] + SIZE['SECTION2-ENTRY_BLANK'] + SIZE['SECTION2-ENTRY_ZOOM']

# error messages
ERROR_INVALID_FIELD_FILE = "Invalid Field file"
ERROR_SECTION2_CAM_VEC_Z_DUP_MISMATCH = "Duplicate z-axis vector dimension 3 value does not match"

def instruction_size(code, offset):
    '''Find the size of the instruction at the given offset in a script code block

    Args:
        ``code`` (``int``): The script code block

        ``offset`` (``int``): The offset

     Returns:
        ``int``: The instruction size
    '''
    op = code[offset]; size = OP[op][1] + 1
    if op == OP_SPECIAL:
        sub_op = code[offset+1]; size = SPECIAL_OP_CODES[sub_op][1] + 2
    elif op == OP_KAWAI:
        size = code[offset+1]
    return size

class FieldScript:
    '''Field Script (Section 1) class'''
    def __init__(self, data):
        '''``FieldScript`` constructor

        Args:
            ``data`` (``bytes``): The Field Script (Section 1) data
        '''
        ind = 0

        # read header
        self.version = unpack('H', data[ind:ind+SIZE['SECTION1-HEADER_VERSION']])[0]; ind += SIZE['SECTION1-HEADER_VERSION'] # always 0x0502
        num_actors = unpack('B', data[ind:ind+SIZE['SECTION1-HEADER_NUM-ACTORS']])[0]; ind += SIZE['SECTION1-HEADER_NUM-ACTORS']
        self.num_models = unpack('B', data[ind:ind+SIZE['SECTION1-HEADER_NUM-MODELS']])[0]; ind += SIZE['SECTION1-HEADER_NUM-MODELS']
        string_table_offset = unpack('H', data[ind:ind+SIZE['SECTION1-HEADER_STRINGS-OFFSET']])[0]; ind += SIZE['SECTION1-HEADER_STRINGS-OFFSET']
        num_akao = unpack('H', data[ind:ind+SIZE['SECTION1-HEADER_NUM-AKAO']])[0]; ind += SIZE['SECTION1-HEADER_NUM-AKAO']
        self.scale = unpack('H', data[ind:ind+SIZE['SECTION1-HEADER_SCALE']])[0]; ind += SIZE['SECTION1-HEADER_SCALE']
        if data[ind:ind+SIZE['SECTION1-HEADER_BLANK']] != NULL_BYTE*SIZE['SECTION1-HEADER_BLANK']:
            raise ValueError(ERROR_INVALID_FIELD_FILE)
        ind += SIZE['SECTION1-HEADER_BLANK']
        self.creator = data[ind:ind+SIZE['SECTION1-HEADER_CREATOR']].decode().rstrip(NULL_STR); ind += SIZE['SECTION1-HEADER_CREATOR']
        self.name = data[ind:ind+SIZE['SECTION1-HEADER_NAME']].decode().rstrip(NULL_STR); ind += SIZE['SECTION1-HEADER_NAME']
        self.actor_names = [data[ind + i*SIZE['SECTION1-HEADER_ACTOR-NAME'] : ind + (i+1)*SIZE['SECTION1-HEADER_ACTOR-NAME']].decode().rstrip(NULL_STR) for i in range(num_actors)]; ind += num_actors*SIZE['SECTION1-HEADER_ACTOR-NAME']
        akao_offsets = [unpack('I', data[ind + i*SIZE['SECTION1-HEADER_AKAO-OFFSET'] : ind + (i+1)*SIZE['SECTION1-HEADER_AKAO-OFFSET']])[0] for i in range(num_akao)]; ind += num_akao*SIZE['SECTION1-HEADER_AKAO-OFFSET']
        akao_offsets.append(len(data))
        self.actor_scripts = [[unpack('H', data[ind + SIZE['SECTION1-HEADER_ACTOR-SCRIPT']*(i*SECTION1_HEADER_NUM_SCRIPTS_PER_ACTOR + j) : ind + SIZE['SECTION1-HEADER_ACTOR-SCRIPT']*(i*SECTION1_HEADER_NUM_SCRIPTS_PER_ACTOR + j+1)])[0] for j in range(SECTION1_HEADER_NUM_SCRIPTS_PER_ACTOR)] for i in range(num_actors)]; ind += SIZE['SECTION1-HEADER_ACTOR-SCRIPT']*SECTION1_HEADER_NUM_SCRIPTS_PER_ACTOR*num_actors
        self.script_entry_offsets = {e for l in self.actor_scripts for e in l}

        # read the script code
        self.script_start_offset = ind
        self.script_code = bytearray(data[self.script_start_offset:string_table_offset])
        if (len(self.script_code) + self.script_start_offset) in self.script_entry_offsets:
            self.script_code.append(OP_RET) # the SNW_W field has (unused) pointers after the end of the code
        
        # add 33rd element to each script entry table which points to the instruction after the first RET of the default script (see https://github.com/niemasd/ff7tools/blob/master/ff7/field.py#L151)
        for i in range(num_actors):
            default_script = self.actor_scripts[i][0]
            code_offset = default_script - self.script_start_offset
            while code_offset < len(self.script_code):
                if self.script_code[code_offset] == OP_RET:
                    entry = code_offset + self.script_start_offset + 1
                    self.actor_scripts[i].append(entry)
                    self.script_entry_offsets.add(entry)
                    break
                else:
                    code_offset += instruction_size(self.script_code, code_offset)

        # read the string offset table
        ind = string_table_offset
        num_strings = unpack('H', data[ind:ind+SIZE['SECTION1_NUM-STRINGS']])[0]; ind += SIZE['SECTION1_NUM-STRINGS'] # internet says this is unreliable
        first_string_offset = unpack('H', data[ind:ind+SIZE['SECTION1_STRING-OFFSET']])[0]
        num_strings = int(first_string_offset / 2) - 1 # internet says this is more reliable
        string_offsets = [unpack('H', data[ind + i*SIZE['SECTION1_STRING-OFFSET'] : ind + (i+1)*SIZE['SECTION1_STRING-OFFSET']])[0] for i in range(num_strings)]

        # read the strings (each string is 0xff-terminated)
        self.string_data = [data[string_table_offset+o : data.find(STRING_TERMINATOR, string_table_offset+o)+1] for o in string_offsets]
        tmp = data.find(STRING_TERMINATOR,string_table_offset+string_offsets[-1])

        # read the Akao/tutorial blocks
        self.akao = [data[akao_offsets[i]:akao_offsets[i+1]] for i in range(num_akao)]

    def get_strings(self):
        '''Return the strings in this Field Script

        Returns:
            ``list`` of ``str``: The strings in this Field Script
        '''
        return [decode_field_text(s) for s in self.string_data]

    def get_bytes(self, version=DEFAULT_VERSION):
        '''Return the bytes encoding this Field Script to repack into a Field File

        Args:
            ``version`` (``int``): The version field of the file (it's always 0x0502)

        Returns:
            ``bytes``: The data to repack into a Field File
        '''
        if len(self.string_data) > MAX_NUM_STRINGS:
            raise ValueError("Number of strings (%d) exceeds maximum allowed (%d)" % (len(self.string_data), MAX_NUM_STRINGS))

        # prepare helpful variables
        string_table_offset = SIZE['SECTION1-HEADER_VERSION'] + SIZE['SECTION1-HEADER_NUM-ACTORS'] + SIZE['SECTION1-HEADER_NUM-MODELS'] + SIZE['SECTION1-HEADER_STRINGS-OFFSET'] + SIZE['SECTION1-HEADER_NUM-AKAO'] + SIZE['SECTION1-HEADER_SCALE'] + SIZE['SECTION1-HEADER_BLANK'] + SIZE['SECTION1-HEADER_CREATOR'] + SIZE['SECTION1-HEADER_NAME'] + SIZE['SECTION1-HEADER_ACTOR-NAME']*len(self.actor_names) + SIZE['SECTION1-HEADER_AKAO-OFFSET']*len(self.akao) + SECTION1_HEADER_NUM_SCRIPTS_PER_ACTOR*SIZE['SECTION1-HEADER_ACTOR-SCRIPT']*len(self.actor_names) + len(self.script_code)

        # create string table
        string_offsets = bytearray(); string_table = bytearray(); offset = SIZE['SECTION1_NUM-STRINGS'] + SIZE['SECTION1_STRING-OFFSET']*len(self.string_data)
        for s in self.string_data:
            string_offsets += pack('H', offset); string_table += s; offset += len(s)
        string_table = pack('H', len(self.string_data)) + string_offsets + string_table
        align = string_table_offset + len(string_table)
        if align % 4 != 0: # for some reason, this way of padding is right on MOST files, but not all (e.g. ancnt*)
            string_table += NULL_BYTE*(4 - (align % 4))

        # encode data
        data = bytearray()
        data += pack('H', version)
        data += pack('B', len(self.actor_names))
        data += pack('B', self.num_models)
        data += pack('H', string_table_offset)
        data += pack('H', len(self.akao))
        data += pack('H', self.scale)
        data += NULL_BYTE*SIZE['SECTION1-HEADER_BLANK']
        data += self.creator.encode(); data += NULL_BYTE*(SIZE['SECTION1-HEADER_CREATOR']-len(self.creator))
        data += self.name.encode(); data += NULL_BYTE*(SIZE['SECTION1-HEADER_NAME']-len(self.name))
        for actor_name in self.actor_names:
            data += actor_name.encode(); data += NULL_BYTE*(SIZE['SECTION1-HEADER_ACTOR-NAME']-len(actor_name))
        offset = string_table_offset + len(string_table)
        for a in self.akao:
            data += pack('I', offset); offset += len(a)
        for scripts in self.actor_scripts:
            for i in range(SECTION1_HEADER_NUM_SCRIPTS_PER_ACTOR): # I added the extra 33rd item, so this gets rid of it
                data += pack('H', scripts[i])
        data += self.script_code # MAYBE IT NEEDS TO BE ALIGNED WITH SCRIPT CODE?
        data += string_table
        for a in self.akao:
            data += a
        return data

class CameraMatrix:
    '''Camera Matrix (Section 2) class'''
    def __init__(self, data):
        '''``CameraMatrix`` constructor

        Args:
            ``data`` (``bytes``): The data of the Field File
        '''
        self.cameras = list(); ind = 0
        for _ in range(int(len(data)/SIZE['SECTION2-ENTRY'])):
            cam = dict()

            # read camera vectors
            for a in SECTION2_AXES:
                cam['vector_%s'%a] = list()
                for __ in range(SECTION2_NUM_DIMENSIONS):
                    cam['vector_%s'%a].append(unpack('H', data[ind:ind+SIZE['SECTION2-ENTRY_VECTOR-VALUE']])[0]); ind += SIZE['SECTION2-ENTRY_VECTOR-VALUE']

            # read vector z 3rd dimension duplicate (sanity check? padding?)
            vec_z_dim_3_dup = unpack('H', data[ind:ind+SIZE['SECTION2-ENTRY_VECTOR-VALUE']])[0]; ind += SIZE['SECTION2-ENTRY_VECTOR-VALUE']
            if vec_z_dim_3_dup != cam['vector_z'][2]:
                raise ValueError(ERROR_SECTION2_CAM_VEC_Z_DUP_MISMATCH)

            # correct vectors (for each vector, divide all 3 dimensions by 4096 and negate 2nd and 3rd dimensions)
            #for a in SECTION2_AXES:
            #    for d in range(SECTION2_NUM_DIMENSIONS):
            #        cam['vector_%s'%a][d] /= SECTION2_VECTOR_DIV # divide all vector values by 4096
            #        if d > 0:
            #            cam['vector_%s'%a][d] *= -1 # negate the 2nd and 3rd dimensions of each vector

            # read camera space positions
            cam['position_camera_space'] = list()
            for _ in range(len(SECTION2_AXES)):
                cam['position_camera_space'].append(unpack('I', data[ind:ind+SIZE['SECTION2-ENTRY_SPACE-POSITION']])[0]); ind += SIZE['SECTION2-ENTRY_SPACE-POSITION']

            # read blank (seems to usually be 0, but not always)
            cam['blank'] = data[ind:ind+SIZE['SECTION2-ENTRY_BLANK']]; ind += SIZE['SECTION2-ENTRY_BLANK']

            # read zoom (unknown if it's unsigned or signed, but Makou Reactor assumes signed, so I will to)
            cam['zoom'] = unpack('H', data[ind:ind+SIZE['SECTION2-ENTRY_ZOOM']])[0]; ind += SIZE['SECTION2-ENTRY_ZOOM']
            
            # camera is loaded, so append to cameras
            self.cameras.append(cam)

    def __len__(self):
        return len(self.cameras)

    def __iter__(self):
        for cam in self.cameras:
            yield cam

    def get_bytes(self):
        '''Return the bytes encoding this Camera Matrix to repack into a Field File

        Returns:
            ``bytes``: The data to repack into a Field File
        '''
        data = bytearray()
        for cam in self.cameras:
            for a in SECTION2_AXES:
                for v in cam['vector_%s'%a]:
                    data += pack('H', v)
        data += pack('H', cam['vector_z'][2])
        for v in cam['position_camera_space']:
            data += pack('I', v)
        data += cam['blank']
        data += pack('H', cam['zoom'])
        return data

class FieldFile:
    '''Field File class'''
    def __init__(self, data):
        '''``FieldFile`` constructor

        Args:
            ``data`` (``bytes``): The data of the Field File
        '''
        if isinstance(data,str):
            f = open(data,'rb'); data = f.read(); f.close()
        if data[:SIZE['HEADER_BLANK']] != NULL_BYTE*SIZE['HEADER_BLANK']:
            try:
                data = decompress_lzss(data); assert data[:SIZE['HEADER_BLANK']] == NULL_BYTE*SIZE['HEADER_BLANK']
            except:
                raise ValueError(ERROR_INVALID_FIELD_FILE)

        # read header
        ind = SIZE['HEADER_BLANK']
        num_sections = unpack('I', data[ind:ind+SIZE['HEADER_NUM-SECTIONS']])[0]; ind += SIZE['HEADER_NUM-SECTIONS']
        if num_sections != len(SECTION_NAME):
            raise ValueError("Expected %d sections, but file has %d" % (len(SECTION_NAME),num_sections))
        starts = [unpack('I', data[ind + i*SIZE['HEADER_SECTION-START'] : ind + (i+1)*SIZE['HEADER_SECTION-START']])[0] for i in range(num_sections)]

        # read sections (ignore section length 4-byte chunk at beginning of each)
        self.field_script = FieldScript(data[starts[0]+SIZE['SECTION-LENGTH']:starts[1]])
        self.camera_matrix = CameraMatrix(data[starts[1]+SIZE['SECTION-LENGTH']:starts[2]])
