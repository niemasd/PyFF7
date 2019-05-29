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
SECTION3_NUM_LIGHTS = 3
SECTION3_NUM_DIMENSIONS = 3
SECTION4_COLOR_MASK = 0b11111
SECTION4_COLOR_A_SHIFT = 15 # A = Alpha = Transparency
SECTION4_COLOR_B_SHIFT = 10 # B = Blue
SECTION4_COLOR_G_SHIFT = 5  # G = Green
SECTION4_COLOR_R_SHIFT = 0  # R = Red
SECTION5_NUM_VERTICES_PER_SECTOR = 3 # Sectors are triangles, which have 3 vertices
SECTION6_SPRITE_TP_BLEND_ZZ_MASK         = 0b1111111000000000
SECTION6_SPRITE_TP_BLEND_DEPH_MASK       = 0b0000000110000000
SECTION6_SPRITE_TP_BLEND_BLEND_MODE_MASK = 0b0000000001100000
SECTION6_SPRITE_TP_BLEND_PAGE_Y_MASK     = 0b0000000000010000
SECTION6_SPRITE_TP_BLEND_PAGE_X_MASK     = 0b0000000000001111
SECTION6_SPRITE_TP_BLEND_ZZ_SHIFT = 9
SECTION6_SPRITE_TP_BLEND_DEPH_SHIFT = 7
SECTION6_SPRITE_TP_BLEND_BLEND_MODE_SHIFT = 5
SECTION6_SPRITE_TP_BLEND_PAGE_Y_SHIFT = 4
SECTION6_SPRITE_TP_BLEND_PAGE_X_SHIFT = 0
SECTION6_TILE_CLUT_ZZ1_MASK      = 0b1111110000000000
SECTION6_TILE_CLUT_CLUT_NUM_MASK = 0b0000001111000000
SECTION6_TILE_CLUT_ZZ2_MASK      = 0b0000000000111111
SECTION6_TILE_CLUT_ZZ1_SHIFT = 10
SECTION6_TILE_CLUT_CLUT_NUM_SHIFT = 6
SECTION6_TILE_CLUT_ZZ2_SHIFT = 0
SECTION6_PARAM_BLENDING_MASK = 0b10000000
SECTION6_PARAM_ID_MASK       = 0b01111111
SECTION6_PARAM_BLENDING_SHIFT = 7
SECTION6_PARAM_ID_SHIFT = 0
SECTION6_SUB1_END_OF_LAYER_TYPE = 0x7FFF
SECTION6_SUB1_SPRITE_TYPE = 0x7FFE
SECTION7_NUM_STANDARD = 6
SECTION7_NUM_SPECIAL = 4
SECTION7_ENCOUNTER_PROB_MASK = 0b1111110000000000
SECTION7_ENCOUNTER_ID_MASK   = 0b0000001111111111
SECTION7_ENCOUNTER_PROB_SHIFT = 10
SECTION7_ENCOUNTER_ID_SHIFT = 0
SECTION8_NUM_GATEWAYS = 12
SECTION8_NUM_TRIGGERS = 12
SECTION8_NUM_SHOWN_ARROWS = 12
SECTION8_NUM_ARROWS = 12
SECTION9_PAL_TITLE = "PALETTE"
SECTION9_PAL_NUM_COLORS = 6
SECTION9_PAL_COLOR_MASK = 0b11111
SECTION9_PAL_COLOR_A_SHIFT = 15 # A = Alpha = Transparency
SECTION9_PAL_COLOR_B_SHIFT = 10 # B = Blue
SECTION9_PAL_COLOR_G_SHIFT = 5  # G = Green
SECTION9_PAL_COLOR_R_SHIFT = 0  # R = Red
SECTION9_BACK_TITLE = "BACK"
SECTION9_TEX_TITLE = "TEXTURE"
SECTION9_TEX_MAX_NUM = 42
SECTION9_TEX_BYTES_PER_DEPTH = 65536
EOF_END_STRING = "END"
EOF_FILE_TERMINATOR = "FINAL FANTASY7"
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
    'HEADER_BLANK':                    2, # Header starts with 2 NULL bytes
    'HEADER_NUM-SECTIONS':             4, # Header: Number of Sections in File
    'HEADER_SECTION-START':            4, # Header: Section Start Position

    # properties of all sections
    'SECTION-LENGTH':                  4, # Section Length

    # Section 1 (Field Script)
    'SECTION1-HEADER_VERSION':         2, # Section 1 Header: Version
    'SECTION1-HEADER_NUM-ACTORS':      1, # Section 1 Header: Number of Actors
    'SECTION1-HEADER_NUM-MODELS':      1, # Section 1 Header: Number of Models
    'SECTION1-HEADER_STRINGS-OFFSET':  2, # Section 1 Header: String Table Offset
    'SECTION1-HEADER_NUM-AKAO':        2, # Section 1 Header: Number of Akao/Tutorial Blocks
    'SECTION1-HEADER_SCALE':           2, # Section 1 Header: Field Scale
    'SECTION1-HEADER_BLANK':           6, # Section 1 Header: Blanks (NULL bytes)
    'SECTION1-HEADER_CREATOR':         8, # Section 1 Header: Field Creator
    'SECTION1-HEADER_NAME':            8, # Section 1 Header: Field Name
    'SECTION1-HEADER_ACTOR-NAME':      8, # Section 1 Header: Actor Name
    'SECTION1-HEADER_AKAO-OFFSET':     4, # Section 1 Header: Akao/Tutorial Block Offsets
    'SECTION1-HEADER_ACTOR-SCRIPT':    2, # Section 1 Header: Actor Script
    'SECTION1_NUM-STRINGS':            2, # Section 1: Number of Strings in String Offset Table
    'SECTION1_STRING-OFFSET':          2, # Section 1: String Offset

    # Section 2 (Camera Matrix)
    'SECTION2-ENTRY_VECTOR-VALUE':     2, # Section 2 Entry: Value in an Axis Vector
    'SECTION2-ENTRY_SPACE-POSITION':   4, # Section 2 Entry: Camera Space Position in an Axis
    'SECTION2-ENTRY_BLANK':            4, # Section 2 Entry: Blank
    'SECTION2-ENTRY_ZOOM':             2, # Section 2 Entry: Zoom

    # Section 3 (Model Loader)
    'SECTION3-HEADER_BLANK':           2, # Section 3 Header: Blanks (NULL bytes)
    'SECTION3-HEADER_NUM-MODELS':      2, # Section 3 Header: Number of Models
    'SECTION3-HEADER_SCALE':           2, # Section 3 Header: Scale
    'SECTION3-MODEL_NAME-LENGTH':      2, # Section 3 Model: Model Name Length
    'SECTION3-MODEL_ATTR':             2, # Section 3 Model: Unknown Attribute (sometimes 0 if the model is playable, 1 otherwise)
    'SECTION3-MODEL_HRC':              8, # Section 3 Model: HRC Name (e.g. AAAA.HRC)
    'SECTION3-MODEL_SCALE':            4, # Section 3 Model: Scale String
    'SECTION3-MODEL_NUM-ANIMATIONS':   2, # Section 3 Model: Number of Animations
    'SECTION3-MODEL_LIGHT-COLOR-VAL':  1, # Section 3 Model: Light Color Value (whole color is in RGB format, 1 byte each, so 3 bytes total)
    'SECTION3-MODEL_LIGHT-COORD-VAL':  2, # Section 3 Model: Light Coordinate Value (2-byte signed integer)
    'SECTION3-MODEL_GLOB-COLOR-VAL':   1, # Section 3 Model: Global Light Color Value (whole color is in RGB format, 1 byte each, so 3 bytes total)
    'SECTION3-ANIMATION_NAME-LENGTH':  2, # Section 3 Animation: Animation Name Length
    'SECTION3-ANIMATION_ATTR':         2, # Section 3 Animation: Unknown Attribute (the 2nd byte is always 0x0 and the 1st byte varies, so maybe an unsigned integer?)

    # Section 4 (Palette)
    'SECTION4-HEADER_LENGTH':          4, # Section 4 Header: Length
    'SECTION4-HEADER_PALX':            2, # Section 4 Header: PalX (always 0)
    'SECTION4-HEADER_PALY':            2, # Section 4 Header: PalY (always 480)
    'SECTION4-HEADER_COLORS-PER-PAGE': 2, # Section 4 Header: Number of Colors in Palette (always 256)
    'SECTION4-HEADER_NUM-PAGES':       2, # Section 4 Header: Number of Palettes
    'SECTION4_COLOR':                  2, # Section 4: Color (16-bit MBBBBBGGGGGRRRRR where M = Mask, B = Blue, G = Green, R = Red)

    # Section 5 (Walkmesh)
    'SECTION5-HEADER_NUM-SECTORS':     4, # Section 5 Header: Number of Sectors
    'SECTION5-SP_VECTOR-VALUE':        2, # Section 5: Value in a Sector Pool Vector (x, y, z, res) (signed integer)
    'SECTION5-AP_VECTOR-VALUE':        2, # Section 5: Value in an Access Pool Vector (access1, access2, access3) (signed integer)

    # Section 6 (Tile Map)
    'SECTION6-HEADER_OFFSET':          4, # Section 6 Header: Subsection Offset
    'SECTION6-SUB1_TYPE':              2, # Section 6 Subsection 1: Type (Layer or Not Layer)
    'SECTION6-SUB2_DEST-X':            2, # Section 6 Subsection 2: Destination X
    'SECTION6-SUB2_DEST-Y':            2, # Section 6 Subsection 2: Destination Y
    'SECTION6-SUB2_TEX-PG-SRC-X':      1, # Section 6 Subsection 2: Tex Page Source X
    'SECTION6-SUB2_TEX-PG-SRC-Y':      1, # Section 6 Subsection 2: Tex Page Source Y
    'SECTION6-SUB2_TILE-CLUT':         2, # Section 6 Subsection 2: Tile Clut Data
    'SECTION6-SUB3_ENTRY':             2, # Section 6 Subsection 3: Entry
    'SECTION6-SUB4_DEST-X':            2, # Section 6 Subsection 4: Destination X
    'SECTION6-SUB4_DEST-Y':            2, # Section 6 Subsection 4: Destination Y
    'SECTION6-SUB4_TEX-PG-SRC-X':      1, # Section 6 Subsection 4: Tex Page Source X
    'SECTION6-SUB4_TEX-PG-SRC-Y':      1, # Section 6 Subsection 4: Tex Page Source Y
    'SECTION6-SUB4_TILE-CLUT':         2, # Section 6 Subsection 4: Tile Clut Data
    'SECTION6-SUB4_SPRITE-TP-BLEND':   2, # Section 6 Subsection 4: Sprite TP Blend
    'SECTION6-SUB4_GROUP':             2, # Section 6 Subsection 4: Group
    'SECTION6-SUB4_PARAM':             1, # Section 6 Subsection 4: Parameter
    'SECTION6-SUB4_STATE':             1, # Section 6 Subsection 4: State
    'SECTION6-SUB5_DEST-X':            2, # Section 6 Subsection 5: Destination X
    'SECTION6-SUB5_DEST-Y':            2, # Section 6 Subsection 5: Destination Y
    'SECTION6-SUB5_TEX-PG-SRC-X':      1, # Section 6 Subsection 5: Tex Page Source X
    'SECTION6-SUB5_TEX-PG-SRC-Y':      1, # Section 6 Subsection 5: Tex Page Source Y
    'SECTION6-SUB5_TILE-CLUT':         2, # Section 6 Subsection 5: Tile Clut Data
    'SECTION6-SUB5_PARAM':             1, # Section 6 Subsection 5: Parameter
    'SECTION6-SUB5_STATE':             1, # Section 6 Subsection 5: State

    # Section 7 (Encounter)
    'SECTION7_ENABLED':                1, # Section 7: Enabled
    'SECTION7_RATE':                   1, # Section 7: Rate
    'SECTION7_ENCOUNTER':              2, # Section 7: Encounter
    'SECTION7_PAD':                    2, # Section 7: Paddig at End of Table

    # Section 8 (Triggers)
    'SECTION8_FIELD-NAME':             9, # Section 8: Field Name (terminated with 0x00)
    'SECTION8_CONTROL-DIRECTION':      1, # Section 8: Control Direction
    'SECTION8_FOCUS-HEIGHT':           2, # Section 8: Camera Focus Height
    'SECTION8_CAMERA-RANGE-DIR':       2, # Section 8: Camera Range Direction
    'SECTION8_UNKNOWN-1':              2, # Section 8: Unknown 1 (related to Background Layer 3 or 4)
    'SECTION8_ANIMATION-WIDTH':        2, # Section 8: Background Layer Animation Width
    'SECTION8_ANIMATION-HEIGHT':       2, # Section 8: Background Layer Animation Height
    'SECTION8_UNKNOWN-2':             12, # Section 8: Unknown 2 (related to Background Layer 3 or 4)
    'SECTION8-GATEWAY_VERTEX-DIM':     2, # Section 8 Gateway: Vertex Coordinate (x, y, or z)
    'SECTION8-GATEWAY_FIELD-ID':       2, # Section 8 Gateway: Field ID
    'SECTION8-GATEWAY_UNKNOWN':        4, # Section 8 Gateway: Unknown
    'SECTION8-TRIGGER_VERTEX-DIM':     2, # Section 8 Trigger: Vertex Coordinate (x, y, or z)
    'SECTION8-TRIGGER_BG-GROUP-ID':    1, # Section 8 Trigger: Background Group ID (Parameter)
    'SECTION8-TRIGGER_BG-FRAME-ID':    1, # Section 8 Trigger: Background Frame ID (State)
    'SECTION8-TRIGGER_BEHAVIOR':       1, # Section 8 Trigger: Behavior
    'SECTION8-TRIGGER_SOUND-ID':       1, # Section 8 Trigger: Sound ID
    'SECTION8_SHOWN-ARROW':            1, # Section 8: Shown Arrow
    'SECTION8-ARROW_POSITION':         4, # Section 8 Arrow: Position (x, y, or z)
    'SECTION8-ARROW_TYPE':             4, # Section 8 Arrow: Type

    # Section 9 (Background)
    'SECTION9-HEADER_UNKNOWN1':        2, # Section 9: Unknown 1 (seems to always be 0)
    'SECTION9-HEADER_DEPTH':           2, # Section 9: Depth (almost always 1, but I saw a file with it as 2)
    'SECTION9-HEADER_UNKNOWN2':        1, # Section 9: Unknown 2 (seems to always be 1)
    'SECTION9-PAL_TITLE':              7, # Section 9 Palette: Title (the string "PALETTE")
    'SECTION9-PAL_SIZE':               4, # Section 9 Palette: Size
    'SECTION9-PAL_PALX':               2, # Section 9 Palette: PalX
    'SECTION9-PAL_PALY':               2, # Section 9 Palette: PalY
    'SECTION9-PAL_WIDTH':              2, # Section 9 Palette: Width
    'SECTION9-PAL_HEIGHT':             2, # Section 9 Palette: Height
    'SECTION9-PAL_COLOR':              2, # Section 9 Palette: Color
    'SECTION9-BACK_TITLE':             4, # Section 9 Background: Title (the string "BACK")
    'SECTION9-BACK-L1_WIDTH':          2, # Section 9 Background Layer 1: Width
    'SECTION9-BACK-L1_HEIGHT':         2, # Section 9 Background Layer 1: Height
    'SECTION9-BACK-L1_NUM-TILES':      2, # Section 9 Background Layer 1: Number of Tiles
    'SECTION9-BACK-L1_DEPTH':          2, # Section 9 Background Layer 1: Depth
    'SECTION9-BACK-L1_BLANK':          2, # Section 9 Background Layer 1: Blank
    'SECTION9-BACK-L1_BLANK-2':        2, # Section 9 Background Layer 1: Blank 2
    'SECTION9-BACK-L2_FLAG':           1, # Section 9 Background Layer 2: Flag
    'SECTION9-BACK-L2_WIDTH':          2, # Section 9 Background Layer 2: Width
    'SECTION9-BACK-L2_HEIGHT':         2, # Section 9 Background Layer 2: Height
    'SECTION9-BACK-L2_NUM-TILES':      2, # Section 9 Background Layer 2: Number of Tiles
    'SECTION9-BACK-L2_UNKNOWN':       16, # Section 9 Background Layer 2: Unknown (unused)
    'SECTION9-BACK-L2_BLANK':          2, # Section 9 Background Layer 2: Blank
    'SECTION9-BACK-L2_BLANK-2':        2, # Section 9 Background Layer 2: Blank 2
    'SECTION9-BACK-L3_FLAG':           1, # Section 9 Background Layer 3: Flag
    'SECTION9-BACK-L3_WIDTH':          2, # Section 9 Background Layer 3: Width
    'SECTION9-BACK-L3_HEIGHT':         2, # Section 9 Background Layer 3: Height
    'SECTION9-BACK-L3_NUM-TILES':      2, # Section 9 Background Layer 3: Number of Tiles
    'SECTION9-BACK-L3_UNKNOWN':       10, # Section 9 Background Layer 3: Unknown (unused)
    'SECTION9-BACK-L3_BLANK':          2, # Section 9 Background Layer 3: Blank
    'SECTION9-BACK-L3_BLANK-2':        2, # Section 9 Background Layer 3: Blank 2
    'SECTION9-BACK-L4_FLAG':           1, # Section 9 Background Layer 4: Flag
    'SECTION9-BACK-L4_WIDTH':          2, # Section 9 Background Layer 4: Width
    'SECTION9-BACK-L4_HEIGHT':         2, # Section 9 Background Layer 4: Height
    'SECTION9-BACK-L4_NUM-TILES':      2, # Section 9 Background Layer 4: Number of Tiles
    'SECTION9-BACK-L4_UNKNOWN':       10, # Section 9 Background Layer 4: Unknown (unused)
    'SECTION9-BACK-L4_BLANK':          2, # Section 9 Background Layer 4: Blank
    'SECTION9-BACK-L4_BLANK-2':        2, # Section 9 Background Layer 4: Blank 2
    'SECTION9-BACK-TILE_BLANK':        2, # Section 9 Background Tile: Blank
    'SECTION9-BACK-TILE_DST-X':        2, # Section 9 Background Tile: Destination X
    'SECTION9-BACK-TILE_DST-Y':        2, # Section 9 Background Tile: Destination Y
    'SECTION9-BACK-TILE_UNKNOWN-1':    4, # Section 9 Background Tile: Unknown 1
    'SECTION9-BACK-TILE_SRC-X':        1, # Section 9 Background Tile: Source X
    'SECTION9-BACK-TILE_UNKNOWN-2':    1, # Section 9 Background Tile: Unknown 2
    'SECTION9-BACK-TILE_SRC-Y':        1, # Section 9 Background Tile: Source Y
    'SECTION9-BACK-TILE_UNKNOWN-3':    1, # Section 9 Background Tile: Unknown 3
    'SECTION9-BACK-TILE_SRC-X2':       1, # Section 9 Background Tile: Source X2
    'SECTION9-BACK-TILE_UNKNOWN-4':    1, # Section 9 Background Tile: Unknown 4
    'SECTION9-BACK-TILE_SRC-Y2':       1, # Section 9 Background Tile: Source Y2
    'SECTION9-BACK-TILE_UNKNOWN-5':    1, # Section 9 Background Tile: Unknown 5
    'SECTION9-BACK-TILE_WIDTH':        2, # Section 9 Background Tile: Width (normally unused)
    'SECTION9-BACK-TILE_HEIGHT':       2, # Section 9 Background Tile: Height (normally unused)
    'SECTION9-BACK-TILE_PALETTE-ID':   1, # Section 9 Background Tile: Palette ID
    'SECTION9-BACK-TILE_UNKNOWN-6':    1, # Section 9 Background Tile: Unknown 6
    'SECTION9-BACK-TILE_ID':           2, # Section 9 Background Tile: ID
    'SECTION9-BACK-TILE_PARAM':        1, # Section 9 Background Tile: Param
    'SECTION9-BACK-TILE_STATE':        1, # Section 9 Background Tile: State
    'SECTION9-BACK-TILE_BLENDING':     1, # Section 9 Background Tile: Blending
    'SECTION9-BACK-TILE_UNKNOWN-7':    1, # Section 9 Background Tile: Unknown 7
    'SECTION9-BACK-TILE_TYPE-TRANS':   1, # Section 9 Background Tile: Type Trans
    'SECTION9-BACK-TILE_UNKNOWN-8':    1, # Section 9 Background Tile: Unknown 8
    'SECTION9-BACK-TILE_TEXTURE-ID':   1, # Section 9 Background Tile: Texture ID
    'SECTION9-BACK-TILE_UNKNOWN-9':    1, # Section 9 Background Tile: Unknown 9
    'SECTION9-BACK-TILE_TEXTURE-ID2':  1, # Section 9 Background Tile: Texture ID 2
    'SECTION9-BACK-TILE_UNKNOWN-10':   1, # Section 9 Background Tile: Unknown 10
    'SECTION9-BACK-TILE_DEPTH':        1, # Section 9 Background Tile: Depth (normally unused)
    'SECTION9-BACK-TILE_UNKNOWN-11':   1, # Section 9 Background Tile: Unknown 11
    'SECTION9-BACK-TILE_ID-BIG':       4, # Section 9 Background Tile: ID Big
    'SECTION9-BACK-TILE_SRC-X-BIG':    4, # Section 9 Background Tile: Source X Big
    'SECTION9-BACK-TILE_SRC-Y-BIG':    4, # Section 9 Background Tile: Source Y Big
    'SECTION9-BACK-TILE_BLANK-2':      2, # Section 9 Background Tile: Blank 2
    'SECTION9-TEX_TITLE':              7, # Section 9 Textures: Title (the string "TEXTURE")
    'SECTION9-TEX_TEX-EXISTS':         2, # Section 9 Textures Texture: Exists
    'SECTION9-TEX_TEX-SIZE':           2, # Section 9 Textures Texture: Size
    'SECTION9-TEX_TEX-DEPTH':          2, # Section 9 Textures Texture: Depth

    # End of File
    'EOF_END-STRING':                  3, # End of File: End String (the string "END")
    'EOF_FILE-TERMINATOR':            14, # End of File: File Terminator (the string "FINAL FANTASY7")
}
SIZE['SECTION2-ENTRY'] = len(SECTION2_AXES)*SECTION2_NUM_DIMENSIONS*SIZE['SECTION2-ENTRY_VECTOR-VALUE'] + SIZE['SECTION2-ENTRY_VECTOR-VALUE'] + len(SECTION2_AXES)*SIZE['SECTION2-ENTRY_SPACE-POSITION'] + SIZE['SECTION2-ENTRY_BLANK'] + SIZE['SECTION2-ENTRY_ZOOM']

# error messages
ERROR_INVALID_FIELD_FILE = "Invalid Field file"
ERROR_SECTION2_CAM_VEC_Z_DUP_MISMATCH = "Duplicate z-axis vector dimension 3 value does not match"
ERROR_SECTION5_SLICE_NOT_IMPLEMENTED = "The ability to slice indices in a Walkmesh has not yet been implemented"

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

    def __eq__(self, other):
        return isinstance(other,FieldScript) and self.version == other.version and self.num_models == other.num_models and self.scale == other.scale and self.creator == other.creator and self.name == other.name and self.actor_names == other.actor_names and self.actor_scripts == other.actor_scripts and self.script_entry_offsets == other.script_entry_offsets and self.script_start_offset == other.script_start_offset and self.script_code == other.script_code and self.string_data == other.string_data and self.akao == other.akao

    def __ne__(self, other):
        return not self == other

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
            ``data`` (``bytes``): The Camera Matrix (Section 2) data
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

    def __eq__(self, other):
        return isinstance(other,CameraMatrix) and self.cameras == other.cameras

    def __ne__(self, other):
        return not self == other

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

class ModelLoader:
    '''Model Loader (Section 3) class'''
    def __init__(self, data):
        '''``ModelLoader`` constructor

        Args:
            ``data`` (``bytes``): The Model Loader (Section 3) data
        '''
        self.models = list(); ind = 0
        self.blank = data[ind:ind+SIZE['SECTION3-HEADER_BLANK']]; ind = SIZE['SECTION3-HEADER_BLANK']
        num_models = unpack('H', data[ind:ind+SIZE['SECTION3-HEADER_NUM-MODELS']])[0]; ind += SIZE['SECTION3-HEADER_NUM-MODELS']
        self.scale = unpack('H', data[ind:ind+SIZE['SECTION3-HEADER_SCALE']])[0]; ind += SIZE['SECTION3-HEADER_SCALE']
        for _ in range(num_models):
            model = dict()
            name_length = unpack('H', data[ind:ind+SIZE['SECTION3-MODEL_NAME-LENGTH']])[0]; ind += SIZE['SECTION3-MODEL_NAME-LENGTH']
            model['name'] = data[ind:ind+name_length].decode(); ind += name_length
            model['attribute'] = unpack('H', data[ind:ind+SIZE['SECTION3-MODEL_ATTR']])[0]; ind += SIZE['SECTION3-MODEL_ATTR']
            model['hrc'] = data[ind:ind+SIZE['SECTION3-MODEL_HRC']].decode(); ind += SIZE['SECTION3-MODEL_HRC']
            model['scale'] = int(data[ind:ind+SIZE['SECTION3-MODEL_SCALE']].decode().rstrip(NULL_STR)); ind += SIZE['SECTION3-MODEL_SCALE']
            num_animations = unpack('H', data[ind:ind+SIZE['SECTION3-MODEL_NUM-ANIMATIONS']])[0]; ind += SIZE['SECTION3-MODEL_NUM-ANIMATIONS']
            for i in range(1, SECTION3_NUM_LIGHTS+1):
                model['light_%d'%i] = dict()
                model['light_%d'%i]['color'] = list()
                for c in ('R','G','B'):
                    model['light_%d'%i]['color'].append(data[ind]); ind += SIZE['SECTION3-MODEL_LIGHT-COLOR-VAL']
                model['light_%d'%i]['coord'] = list()
                for d in range(SECTION3_NUM_DIMENSIONS):
                    model['light_%d'%i]['coord'].append(unpack('h', data[ind:ind+SIZE['SECTION3-MODEL_LIGHT-COORD-VAL']])[0]); ind += SIZE['SECTION3-MODEL_LIGHT-COORD-VAL']
            model['global_light_color'] = list()
            for c in ('R','G','B'):
                model['global_light_color'].append(data[ind]); ind += SIZE['SECTION3-MODEL_GLOB-COLOR-VAL']
            model['animations'] = list()
            for __ in range(num_animations):
                animation = dict()
                name_length = unpack('H', data[ind:ind+SIZE['SECTION3-ANIMATION_NAME-LENGTH']])[0]; ind += SIZE['SECTION3-ANIMATION_NAME-LENGTH']
                animation['name'] = data[ind:ind+name_length].decode(); ind += name_length
                animation['attribute'] = unpack('H', data[ind:ind+SIZE['SECTION3-ANIMATION_ATTR']])[0]; ind += SIZE['SECTION3-ANIMATION_ATTR']
                model['animations'].append(animation)
            self.models.append(model)

    def __eq__(self, other):
        return isinstance(other,ModelLoader) and self.models == other.models and self.scale == other.scale and self.blank == other.blank

    def __ne__(self, other):
        return not self == other

    def __len__(self):
        return len(self.models)

    def __iter__(self):
        for model in self.models:
            yield model

    def get_bytes(self):
        '''Return the bytes encoding this Model Loader to repack into a Field File

        Returns:
            ``bytes``: The data to repack into a Field File
        '''
        data = bytearray()
        data += NULL_BYTE*SIZE['SECTION3-HEADER_BLANK']
        data += pack('H', len(self.models))
        data += pack('H', self.scale)
        for model in self.models:
            data += pack('H', len(model['name']))
            data += model['name'].encode()
            data += pack('H', model['attribute'])
            data += model['hrc'].encode()
            data += str(model['scale']).encode(); data += NULL_BYTE*(SIZE['SECTION3-MODEL_SCALE']-len(str(model['scale'])))
            data += pack('H', len(model['animations']))
            for i in range(1, SECTION3_NUM_LIGHTS+1):
                for v in model['light_%d'%i]['color']:
                    data += pack('B', v)
                for v in model['light_%d'%i]['coord']:
                    data += pack('h', v)
            for v in model['global_light_color']:
                data += pack('B', v)
            for animation in model['animations']:
                data += pack('H', len(animation['name']))
                data += animation['name'].encode()
                data += pack('H', animation['attribute'])
        return data

class Palette:
    '''Palette (Section 4) class'''
    def __init__(self, data):
        '''``Palette`` constructor

        Args:
            ``data`` (``bytes``): The Palette (Section 4) data
        '''
        self.color_pages = list(); ind = SIZE['SECTION4-HEADER_LENGTH']
        self.palX = unpack('H', data[ind:ind+SIZE['SECTION4-HEADER_PALX']])[0]; ind += SIZE['SECTION4-HEADER_PALX']
        self.palY = unpack('H', data[ind:ind+SIZE['SECTION4-HEADER_PALY']])[0]; ind += SIZE['SECTION4-HEADER_PALY']
        colors_per_page = unpack('H', data[ind:ind+SIZE['SECTION4-HEADER_COLORS-PER-PAGE']])[0]; ind += SIZE['SECTION4-HEADER_COLORS-PER-PAGE']
        num_pages = unpack('H', data[ind:ind+SIZE['SECTION4-HEADER_NUM-PAGES']])[0]; ind += SIZE['SECTION4-HEADER_NUM-PAGES']
        while ind < len(data):
            color = unpack('H', data[ind:ind+SIZE['SECTION4_COLOR']])[0]; ind += SIZE['SECTION4_COLOR']
            color_r = (color >> SECTION4_COLOR_R_SHIFT) & SECTION4_COLOR_MASK
            color_g = (color >> SECTION4_COLOR_G_SHIFT) & SECTION4_COLOR_MASK
            color_b = (color >> SECTION4_COLOR_B_SHIFT) & SECTION4_COLOR_MASK
            color_a = (color >> SECTION4_COLOR_A_SHIFT) & SECTION4_COLOR_MASK
            if len(self.color_pages) == 0 or len(self.color_pages[-1]) == colors_per_page:
                self.color_pages.append(list())
            self.color_pages[-1].append([color_r, color_g, color_b, color_a]) # I read them as ABGR, but I like saving them as RGBA

    def __eq__(self, other):
        return isinstance(other,Palette) and self.palX == other.palX and self.palY == other.palY and self.colors_per_page == other.colors_per_page and self.colors == other.colors

    def __ne__(self, other):
        return not self == other

    def get_num_color_pages(self):
        return len(self.color_pages)

    def get_num_colors_per_page(self):
        return len(self.color_pages[0])

    def get_bytes(self):
        '''Return the bytes encoding this Palette to repack into a Field File

        Returns:
            ``bytes``: The data to repack into a Field File
        '''
        data = bytearray()
        data += pack('H', self.palX)                      # always 0
        data += pack('H', self.palY)                      # always 480
        data += pack('H', self.get_num_colors_per_page()) # always 256
        data += pack('H', self.get_num_color_pages())
        for p in self.color_pages:
            for c in p:
                data += pack('H', (c[0] << SECTION4_COLOR_R_SHIFT) | (c[1] << SECTION4_COLOR_G_SHIFT) | (c[2] << SECTION4_COLOR_B_SHIFT) | (c[3] << SECTION4_COLOR_A_SHIFT))
        data = pack('I', SIZE['SECTION4-HEADER_LENGTH']+len(data)) + data
        return data

class Walkmesh:
    '''Walkmesh (Section 5) class'''
    def __init__(self, data):
        '''``Walkmesh`` constructor

        Args:
            ``data`` (``bytes``): The Walkmesh (Section 5) data
        '''
        self.sector_pool = list(); self.access_pool = list(); ind = 0
        num_sectors = unpack('I', data[ind:ind+SIZE['SECTION5-HEADER_NUM-SECTORS']])[0]; ind += SIZE['SECTION5-HEADER_NUM-SECTORS']
        for _ in range(num_sectors):
            triangle = list()
            for __ in range(SECTION5_NUM_VERTICES_PER_SECTOR):
                vertex_x = unpack('h', data[ind:ind+SIZE['SECTION5-SP_VECTOR-VALUE']])[0]; ind += SIZE['SECTION5-SP_VECTOR-VALUE']
                vertex_y = unpack('h', data[ind:ind+SIZE['SECTION5-SP_VECTOR-VALUE']])[0]; ind += SIZE['SECTION5-SP_VECTOR-VALUE']
                vertex_z = unpack('h', data[ind:ind+SIZE['SECTION5-SP_VECTOR-VALUE']])[0]; ind += SIZE['SECTION5-SP_VECTOR-VALUE']
                vertex_r = unpack('h', data[ind:ind+SIZE['SECTION5-SP_VECTOR-VALUE']])[0]; ind += SIZE['SECTION5-SP_VECTOR-VALUE']
                triangle.append([vertex_x, vertex_y, vertex_z, vertex_r])
            self.sector_pool.append(triangle)
        for _ in range(num_sectors):
            access_1 = unpack('h', data[ind:ind+SIZE['SECTION5-AP_VECTOR-VALUE']])[0]; ind += SIZE['SECTION5-AP_VECTOR-VALUE']
            access_2 = unpack('h', data[ind:ind+SIZE['SECTION5-AP_VECTOR-VALUE']])[0]; ind += SIZE['SECTION5-AP_VECTOR-VALUE']
            access_3 = unpack('h', data[ind:ind+SIZE['SECTION5-AP_VECTOR-VALUE']])[0]; ind += SIZE['SECTION5-AP_VECTOR-VALUE']
            self.access_pool.append([access_1, access_2, access_3])

    def __eq__(self, other):
        return isinstance(other,Walkmesh) and self.sector_pool == other.sector_pool and self.access_pool == other.access_pool

    def __ne__(self, other):
        return not self == other

    def __len__(self):
        return len(self.sector_pool)

    def __getitem__(self, key):
        if isinstance(key, slice):
            raise NotImplementedError(ERROR_SECTION5_SLICE_NOT_IMPLEMENTED)
        elif isinstance(key, int):
            if key < 0 or key >= len(self.sector_pool):
                raise IndexError("Index must be between at least 0 and less than %d" % len(self.sector_pool))
            return (self.sector_pool[key], self.access_pool[key])
        else:
            raise TypeError('Index must be int, not {}'.format(type(key).__name__))

    def get_bytes(self):
        '''Return the bytes encoding this Walkmesh to repack into a Field File

        Returns:
            ``bytes``: The data to repack into a Field File
        '''
        data = bytearray()
        data += pack('I', len(self.sector_pool))
        for triangle in self.sector_pool:
            for vertex in triangle:
                for v in vertex:
                    data += pack('h', v)
        for vector in self.access_pool:
            for v in vector:
                data += pack('h', v)
        return data

def parse_sec6_sprite_tp_blend(raw):
    '''Parse a (raw) Sprite TP Blend represented as a 2-byte integer

    Returns:
        ``dict``: The parsed Sprite Blend
    '''
    entry = dict()
    entry['zz']            = (raw & SECTION6_SPRITE_TP_BLEND_ZZ_MASK)         >> SECTION6_SPRITE_TP_BLEND_ZZ_SHIFT
    entry['deph']          = (raw & SECTION6_SPRITE_TP_BLEND_DEPH_MASK)       >> SECTION6_SPRITE_TP_BLEND_DEPH_SHIFT
    entry['blending_mode'] = (raw & SECTION6_SPRITE_TP_BLEND_BLEND_MODE_MASK) >> SECTION6_SPRITE_TP_BLEND_BLEND_MODE_SHIFT
    entry['page_y']        = (raw & SECTION6_SPRITE_TP_BLEND_PAGE_Y_MASK)     >> SECTION6_SPRITE_TP_BLEND_PAGE_Y_SHIFT
    entry['page_x']        = (raw & SECTION6_SPRITE_TP_BLEND_PAGE_X_MASK)     >> SECTION6_SPRITE_TP_BLEND_PAGE_X_SHIFT
    return entry

def parse_sec6_tile_clut(raw):
    '''Parse a (raw) Tile Clut represented as a 2-byte integer

    Returns:
        ``dict``: The parsed Tile Clut
    '''
    entry = dict()
    entry['zz1']      = (raw & SECTION6_TILE_CLUT_ZZ1_MASK)      >> SECTION6_TILE_CLUT_ZZ1_SHIFT
    entry['clut_num'] = (raw & SECTION6_TILE_CLUT_CLUT_NUM_MASK) >> SECTION6_TILE_CLUT_CLUT_NUM_SHIFT
    entry['zz2']      = (raw & SECTION6_TILE_CLUT_ZZ2_MASK)      >> SECTION6_TILE_CLUT_ZZ2_SHIFT
    return entry

def parse_sec6_param(raw):
    '''Parse a (raw) Parameter represented as a 2-byte integer

    Returns:
        ``dict``: The parsed Parameter
    '''
    entry = dict()
    entry['blending'] = (raw & SECTION6_PARAM_BLENDING_MASK) >> SECTION6_PARAM_BLENDING_SHIFT
    entry['ID']       = (raw & SECTION6_PARAM_ID_MASK)       >> SECTION6_PARAM_ID_SHIFT
    return entry

class TileMap:
    '''Tile Map (Section 6) class (it's unused, so just save the data)'''
    def __init__(self, data):
        '''``TileMap`` constructor

        Args:
            ``data`` (``bytes``): The Tile Map (Section 6) data
        '''
        self.data = data

    def __len__(self):
        return len(self.data)

    def get_bytes(self):
        '''Return the bytes encoding this Tile Map to repack into a Field File

        Returns:
            ``bytes``: The data to repack into a Field File
        '''
        return self.data

class Encounter:
    '''Encounter (Section 7) class'''
    def __init__(self, data):
        '''``Encounter`` constructor

        Args:
            ``data`` (``bytes``): The Encounter (Section 7) data
        '''
        self.table_1 = dict(); self.table_2 = dict(); ind = 0
        for table in [self.table_1, self.table_2]:
            table['enabled'] = unpack('B', data[ind:ind+SIZE['SECTION7_ENABLED']])[0]; ind += SIZE['SECTION7_ENABLED']
            table['rate'] = unpack('B', data[ind:ind+SIZE['SECTION7_RATE']])[0]; ind += SIZE['SECTION7_RATE']
            table['den'] = dict()
            for k,n in [('standard',SECTION7_NUM_STANDARD), ('special',SECTION7_NUM_SPECIAL)]:
                table[k] = list()
                for _ in range(n):
                    tmp = unpack('H', data[ind:ind+SIZE['SECTION7_ENCOUNTER']])[0]; ind += SIZE['SECTION7_ENCOUNTER']
                    table[k].append({'prob':(tmp & SECTION7_ENCOUNTER_PROB_MASK) >> SECTION7_ENCOUNTER_PROB_SHIFT, 'ID':(tmp & SECTION7_ENCOUNTER_ID_MASK) >> SECTION7_ENCOUNTER_ID_SHIFT})
                tot = sum(enc['prob'] for enc in table[k]); table['den'][k] = {True:1., False:float(tot)}[tot == 0]
                for enc in table[k]: # divide by sum to get probability
                    enc['prob'] /= table['den'][k]
            table['pad'] = data[ind:ind+SIZE['SECTION7_PAD']]; ind += SIZE['SECTION7_PAD']

    def get_bytes(self):
        '''Return the bytes encoding this Encounter to repack into a Field File

        Returns:
            ``bytes``: The data to repack into a Field File
        '''
        data = bytearray()
        for table in [self.table_1, self.table_2]:
            data += pack('B', table['enabled'])
            data += pack('B', table['rate'])
            for k in ['standard','special']:
                for enc in table[k]:
                    data += pack('H', (int(enc['prob']*table['den'][k]) << SECTION7_ENCOUNTER_PROB_SHIFT) | (enc['ID'] << SECTION7_ENCOUNTER_ID_SHIFT))
            data += table['pad']
        return data

class Triggers:
    '''Triggers (Section 8) class'''
    def __init__(self, data):
        '''``Triggers`` constructor

        Args:
            ``data`` (``bytes``): The Encounter (Section 8) data
        '''
        ind = 0
        self.name = data[ind:ind+SIZE['SECTION8_FIELD-NAME']].decode().rstrip(NULL_STR); ind += SIZE['SECTION8_FIELD-NAME']
        self.control_direction = unpack('b', data[ind:ind+SIZE['SECTION8_CONTROL-DIRECTION']])[0]; ind += SIZE['SECTION8_CONTROL-DIRECTION']
        self.focus_height = unpack('h', data[ind:ind+SIZE['SECTION8_FOCUS-HEIGHT']])[0]; ind += SIZE['SECTION8_FOCUS-HEIGHT']
        self.camera_range = dict()
        for d in ['left','bottom','right','top']:
            self.camera_range[d] = unpack('h', data[ind:ind+SIZE['SECTION8_CAMERA-RANGE-DIR']])[0]; ind += SIZE['SECTION8_CAMERA-RANGE-DIR']
        self.unknown_1 = dict()
        for k in ['layer_3', 'layer_4']:
            self.unknown_1[k] = unpack('H', data[ind:ind+SIZE['SECTION8_UNKNOWN-1']])[0]; ind += SIZE['SECTION8_UNKNOWN-1']
        self.bg_animation = {'layer_3':dict(), 'layer_4':dict()}
        for k in ['layer_3', 'layer_4']:
            self.bg_animation[k]['width'] = unpack('h', data[ind:ind+SIZE['SECTION8_ANIMATION-WIDTH']])[0]; ind += SIZE['SECTION8_ANIMATION-WIDTH']
            self.bg_animation[k]['height'] = unpack('h', data[ind:ind+SIZE['SECTION8_ANIMATION-HEIGHT']])[0]; ind += SIZE['SECTION8_ANIMATION-HEIGHT']
        self.unknown_2 = {'layer_3':list(), 'layer_4':list()}
        for k in ['layer_3', 'layer_4']:
            self.unknown_2[k] = data[ind:ind+SIZE['SECTION8_UNKNOWN-2']]; ind += SIZE['SECTION8_UNKNOWN-2']
        self.gateways = list()
        for _ in range(SECTION8_NUM_GATEWAYS):
            gateway = dict()
            for k in ['exit_vertex_1', 'exit_vertex_2', 'destination_vertex']:
                gateway[k] = list()
                for d in ['x','z','y']:
                    gateway[k].append(unpack('h', data[ind:ind+SIZE['SECTION8-GATEWAY_VERTEX-DIM']])[0]); ind += SIZE['SECTION8-GATEWAY_VERTEX-DIM']
            gateway['field_ID'] = unpack('H', data[ind:ind+SIZE['SECTION8-GATEWAY_FIELD-ID']])[0]; ind += SIZE['SECTION8-GATEWAY_FIELD-ID']
            gateway['unknown'] = data[ind:ind+SIZE['SECTION8-GATEWAY_UNKNOWN']]; ind += SIZE['SECTION8-GATEWAY_UNKNOWN']
            self.gateways.append(gateway)
        self.triggers = list()
        for _ in range(SECTION8_NUM_TRIGGERS):
            trigger = dict()
            for k in ['vertex_corner_1', 'vertex_corner_2']:
                trigger[k] = list()
                for d in ['x','y','z']:
                    trigger[k].append(unpack('h', data[ind:ind+SIZE['SECTION8-TRIGGER_VERTEX-DIM']])[0]); ind += SIZE['SECTION8-TRIGGER_VERTEX-DIM']
            trigger['bg_group_ID'] = unpack('b', data[ind:ind+SIZE['SECTION8-TRIGGER_BG-GROUP-ID']])[0]; ind += SIZE['SECTION8-TRIGGER_BG-GROUP-ID']
            trigger['bg_frame_ID'] = unpack('B', data[ind:ind+SIZE['SECTION8-TRIGGER_BG-FRAME-ID']])[0]; ind += SIZE['SECTION8-TRIGGER_BG-FRAME-ID']
            trigger['behavior'] = unpack('B', data[ind:ind+SIZE['SECTION8-TRIGGER_BEHAVIOR']])[0]; ind += SIZE['SECTION8-TRIGGER_BEHAVIOR']
            trigger['sound_ID'] = unpack('B', data[ind:ind+SIZE['SECTION8-TRIGGER_SOUND-ID']])[0]; ind += SIZE['SECTION8-TRIGGER_SOUND-ID']
            self.triggers.append(trigger)
        self.shown_arrows = list()
        for _ in range(SECTION8_NUM_SHOWN_ARROWS):
            self.shown_arrows.append(unpack('B', data[ind:ind+SIZE['SECTION8_SHOWN-ARROW']])[0]); ind += SIZE['SECTION8_SHOWN-ARROW']
        self.arrows = list()
        for _ in range(SECTION8_NUM_ARROWS):
            arrow = {'position': list()}
            for d in ['x','z','y']:
                arrow['position'].append(unpack('i', data[ind:ind+SIZE['SECTION8-ARROW_POSITION']])[0]); ind += SIZE['SECTION8-ARROW_POSITION']
            arrow['type'] = unpack('i', data[ind:ind+SIZE['SECTION8-ARROW_TYPE']])[0]; ind += SIZE['SECTION8-ARROW_TYPE']
            self.arrows.append(arrow)

    def get_bytes(self):
        '''Return the bytes encoding this Triggers to repack into a Field File

        Returns:
            ``bytes``: The data to repack into a Field File
        '''
        data = bytearray()
        data += self.name.encode(); data += NULL_BYTE*(SIZE['SECTION8_FIELD-NAME'] - len(self.name))
        data += pack('b', self.control_direction)
        data += pack('h', self.focus_height)
        for d in ['left','bottom','right','top']:
            data += pack('h', self.camera_range[d])
        for k in ['layer_3', 'layer_4']:
            data += pack('H', self.unknown_1[k])
        for k in ['layer_3', 'layer_4']:
            data += pack('h', self.bg_animation[k]['width']); data += pack('h', self.bg_animation[k]['height'])
        for k in ['layer_3', 'layer_4']:
            data += self.unknown_2[k]
        for gateway in self.gateways:
            for k in ['exit_vertex_1', 'exit_vertex_2', 'destination_vertex']:
                for v in gateway[k]:
                    data += pack('h', v)
            data += pack('H', gateway['field_ID'])
            data += gateway['unknown']
        for trigger in self.triggers:
            for k in ['vertex_corner_1', 'vertex_corner_2']:
                for v in trigger[k]:
                    data += pack('h', v)
            data += pack('b', trigger['bg_group_ID'])
            data += pack('B', trigger['bg_frame_ID'])
            data += pack('B', trigger['behavior'])
            data += pack('B', trigger['sound_ID'])
        for shown_arrow in self.shown_arrows:
            data += pack('B', shown_arrow)
        for arrow in self.arrows:
            for v in arrow['position']:
                data += pack('i', v)
            data += pack('i', arrow['type'])
        return data

class Background:
    '''Background class'''
    def __init__(self, data):
        '''``Background`` constructor

        Args:
            ``data`` (``bytes``): The Background (Section 9) data
        '''
        ind = 0

        # read header
        self.header = dict()
        self.header['unknown1'] = unpack('H', data[ind:ind+SIZE['SECTION9-HEADER_UNKNOWN1']])[0]; ind += SIZE['SECTION9-HEADER_UNKNOWN1']
        self.header['depth'] = unpack('H', data[ind:ind+SIZE['SECTION9-HEADER_DEPTH']])[0]; ind += SIZE['SECTION9-HEADER_DEPTH']
        self.header['unknown2'] = unpack('B', data[ind:ind+SIZE['SECTION9-HEADER_UNKNOWN2']])[0]; ind += SIZE['SECTION9-HEADER_UNKNOWN2']

        # read palette
        self.palette = dict()
        title = data[ind:ind+SIZE['SECTION9-PAL_TITLE']].decode().strip(); ind += SIZE['SECTION9-PAL_TITLE'] # the string "PALETTE"
        if title != SECTION9_PAL_TITLE:
            raise ValueError(ERROR_INVALID_FIELD_FILE)
        self.palette['size'] = unpack('I', data[ind:ind+SIZE['SECTION9-PAL_SIZE']])[0]; ind += SIZE['SECTION9-PAL_SIZE']
        self.palette['palX'] = unpack('H', data[ind:ind+SIZE['SECTION9-PAL_PALX']])[0]; ind += SIZE['SECTION9-PAL_PALX']
        self.palette['palY'] = unpack('H', data[ind:ind+SIZE['SECTION9-PAL_PALY']])[0]; ind += SIZE['SECTION9-PAL_PALY']
        self.palette['width'] = unpack('H', data[ind:ind+SIZE['SECTION9-PAL_WIDTH']])[0]; ind += SIZE['SECTION9-PAL_WIDTH']
        self.palette['height'] = unpack('H', data[ind:ind+SIZE['SECTION9-PAL_HEIGHT']])[0]; ind += SIZE['SECTION9-PAL_HEIGHT']
        self.palette['colors'] = list()
        for _ in range(SECTION9_PAL_NUM_COLORS):
            color = unpack('H', data[ind:ind+SIZE['SECTION9-PAL_COLOR']])[0]; ind += SIZE['SECTION9-PAL_COLOR']
            color_r = (color >> SECTION9_PAL_COLOR_R_SHIFT) & SECTION9_PAL_COLOR_MASK
            color_g = (color >> SECTION9_PAL_COLOR_G_SHIFT) & SECTION9_PAL_COLOR_MASK
            color_b = (color >> SECTION9_PAL_COLOR_B_SHIFT) & SECTION9_PAL_COLOR_MASK
            color_a = (color >> SECTION9_PAL_COLOR_A_SHIFT) & SECTION9_PAL_COLOR_MASK
            self.palette['colors'].append([color_r, color_g, color_b, color_a]) # I read them as ABGR, but I like saving them as RGBA

        # read background tiles
        self.back = dict()
        title = data[ind:ind+SIZE['SECTION9-BACK_TITLE']].decode().strip(); ind += SIZE['SECTION9-BACK_TITLE']
        if title != SECTION9_BACK_TITLE:
            raise ValueError(ERROR_INVALID_FIELD_FILE)

        # read layer 1
        self.back['layer_1'] = dict()
        self.back['layer_1']['width'] = unpack('H', data[ind:ind+SIZE['SECTION9-BACK-L1_WIDTH']])[0]; ind += SIZE['SECTION9-BACK-L1_WIDTH']
        self.back['layer_1']['height'] = unpack('H', data[ind:ind+SIZE['SECTION9-BACK-L1_HEIGHT']])[0]; ind += SIZE['SECTION9-BACK-L1_HEIGHT']
        num_l1_tiles = unpack('H', data[ind:ind+SIZE['SECTION9-BACK-L1_NUM-TILES']])[0]; ind += SIZE['SECTION9-BACK-L1_NUM-TILES']
        self.back['layer_1']['depth'] = unpack('H', data[ind:ind+SIZE['SECTION9-BACK-L1_DEPTH']])[0]; ind += SIZE['SECTION9-BACK-L1_DEPTH']
        blank = unpack('H', data[ind:ind+SIZE['SECTION9-BACK-L1_BLANK']])[0]; ind += SIZE['SECTION9-BACK-L1_BLANK']
        self.back['layer_1']['tiles'] = list()
        for _ in range(num_l1_tiles):
            tile = dict()
            blank = unpack('H', data[ind:ind+SIZE['SECTION9-BACK-TILE_BLANK']])[0]; ind += SIZE['SECTION9-BACK-TILE_BLANK']
            tile['dst_x'] = unpack('h', data[ind:ind+SIZE['SECTION9-BACK-TILE_DST-X']])[0]; ind += SIZE['SECTION9-BACK-TILE_DST-X']
            tile['dst_y'] = unpack('h', data[ind:ind+SIZE['SECTION9-BACK-TILE_DST-Y']])[0]; ind += SIZE['SECTION9-BACK-TILE_DST-Y']
            tile['unknown_1'] = data[ind:ind+SIZE['SECTION9-BACK-TILE_UNKNOWN-1']]; ind += SIZE['SECTION9-BACK-TILE_UNKNOWN-1']
            tile['src_x'] = unpack('B', data[ind:ind+SIZE['SECTION9-BACK-TILE_SRC-X']])[0]; ind += SIZE['SECTION9-BACK-TILE_SRC-X']
            tile['unknown_2'] = data[ind:ind+SIZE['SECTION9-BACK-TILE_UNKNOWN-2']]; ind += SIZE['SECTION9-BACK-TILE_UNKNOWN-2']
            tile['src_y'] = unpack('B', data[ind:ind+SIZE['SECTION9-BACK-TILE_SRC-Y']])[0]; ind += SIZE['SECTION9-BACK-TILE_SRC-Y']
            tile['unknown_3'] = data[ind:ind+SIZE['SECTION9-BACK-TILE_UNKNOWN-3']]; ind += SIZE['SECTION9-BACK-TILE_UNKNOWN-3']
            tile['src_x2'] = unpack('B', data[ind:ind+SIZE['SECTION9-BACK-TILE_SRC-X2']])[0]; ind += SIZE['SECTION9-BACK-TILE_SRC-X2']
            tile['unknown_4'] = data[ind:ind+SIZE['SECTION9-BACK-TILE_UNKNOWN-4']]; ind += SIZE['SECTION9-BACK-TILE_UNKNOWN-4']
            tile['src_y2'] = unpack('B', data[ind:ind+SIZE['SECTION9-BACK-TILE_SRC-Y2']])[0]; ind += SIZE['SECTION9-BACK-TILE_SRC-Y2']
            tile['unknown_5'] = data[ind:ind+SIZE['SECTION9-BACK-TILE_UNKNOWN-5']]; ind += SIZE['SECTION9-BACK-TILE_UNKNOWN-5']
            tile['width'] = unpack('H', data[ind:ind+SIZE['SECTION9-BACK-TILE_WIDTH']])[0]; ind += SIZE['SECTION9-BACK-TILE_WIDTH']
            tile['height'] = unpack('H', data[ind:ind+SIZE['SECTION9-BACK-TILE_HEIGHT']])[0]; ind += SIZE['SECTION9-BACK-TILE_HEIGHT']
            tile['palette_ID'] = unpack('B', data[ind:ind+SIZE['SECTION9-BACK-TILE_PALETTE-ID']])[0]; ind += SIZE['SECTION9-BACK-TILE_PALETTE-ID']
            tile['unknown_6'] = data[ind:ind+SIZE['SECTION9-BACK-TILE_UNKNOWN-6']]; ind += SIZE['SECTION9-BACK-TILE_UNKNOWN-6']
            tile['ID'] = unpack('H', data[ind:ind+SIZE['SECTION9-BACK-TILE_ID']])[0]; ind += SIZE['SECTION9-BACK-TILE_ID']
            tile['param'] = unpack('B', data[ind:ind+SIZE['SECTION9-BACK-TILE_PARAM']])[0]; ind += SIZE['SECTION9-BACK-TILE_PARAM']
            tile['state'] = unpack('B', data[ind:ind+SIZE['SECTION9-BACK-TILE_STATE']])[0]; ind += SIZE['SECTION9-BACK-TILE_STATE']
            tile['blending'] = unpack('B', data[ind:ind+SIZE['SECTION9-BACK-TILE_BLENDING']])[0]; ind += SIZE['SECTION9-BACK-TILE_BLENDING']
            tile['unknown_7'] = data[ind:ind+SIZE['SECTION9-BACK-TILE_UNKNOWN-7']]; ind += SIZE['SECTION9-BACK-TILE_UNKNOWN-7']
            tile['type_trans'] = unpack('B', data[ind:ind+SIZE['SECTION9-BACK-TILE_TYPE-TRANS']])[0]; ind += SIZE['SECTION9-BACK-TILE_TYPE-TRANS']
            tile['unknown_8'] = data[ind:ind+SIZE['SECTION9-BACK-TILE_UNKNOWN-8']]; ind += SIZE['SECTION9-BACK-TILE_UNKNOWN-8']
            tile['texture_id'] = unpack('B', data[ind:ind+SIZE['SECTION9-BACK-TILE_TEXTURE-ID']])[0]; ind += SIZE['SECTION9-BACK-TILE_TEXTURE-ID']
            tile['unknown_9'] = data[ind:ind+SIZE['SECTION9-BACK-TILE_UNKNOWN-9']]; ind += SIZE['SECTION9-BACK-TILE_UNKNOWN-9']
            tile['texture_id2'] = unpack('B', data[ind:ind+SIZE['SECTION9-BACK-TILE_TEXTURE-ID2']])[0]; ind += SIZE['SECTION9-BACK-TILE_TEXTURE-ID2']
            tile['unknown_10'] = data[ind:ind+SIZE['SECTION9-BACK-TILE_UNKNOWN-10']]; ind += SIZE['SECTION9-BACK-TILE_UNKNOWN-10']
            tile['depth'] = unpack('B', data[ind:ind+SIZE['SECTION9-BACK-TILE_DEPTH']])[0]; ind += SIZE['SECTION9-BACK-TILE_DEPTH']
            tile['unknown_11'] = data[ind:ind+SIZE['SECTION9-BACK-TILE_UNKNOWN-11']]; ind += SIZE['SECTION9-BACK-TILE_UNKNOWN-11']
            tile['ID_big'] = unpack('I', data[ind:ind+SIZE['SECTION9-BACK-TILE_ID-BIG']])[0]; ind += SIZE['SECTION9-BACK-TILE_ID-BIG']
            src_x_big = unpack('I', data[ind:ind+SIZE['SECTION9-BACK-TILE_SRC-X-BIG']])[0]; ind += SIZE['SECTION9-BACK-TILE_SRC-X-BIG']
            src_y_big = unpack('I', data[ind:ind+SIZE['SECTION9-BACK-TILE_SRC-Y-BIG']])[0]; ind += SIZE['SECTION9-BACK-TILE_SRC-Y-BIG']
            blank = unpack('H', data[ind:ind+SIZE['SECTION9-BACK-TILE_BLANK-2']])[0]; ind += SIZE['SECTION9-BACK-TILE_BLANK-2']
            self.back['layer_1']['tiles'].append(tile)
        blank = unpack('H', data[ind:ind+SIZE['SECTION9-BACK-L1_BLANK-2']])[0]; ind += SIZE['SECTION9-BACK-L1_BLANK-2']

        # read layer 2
        l2_flag = unpack('B', data[ind:ind+SIZE['SECTION9-BACK-L2_FLAG']])[0]; ind += SIZE['SECTION9-BACK-L2_FLAG']
        self.back['layer_2'] = dict()
        if l2_flag != 0:
            if l2_flag != 1:
                raise ValueError(ERROR_INVALID_FIELD_FILE)
            self.back['layer_2']['width'] = unpack('H', data[ind:ind+SIZE['SECTION9-BACK-L2_WIDTH']])[0]; ind += SIZE['SECTION9-BACK-L2_WIDTH']
            self.back['layer_2']['height'] = unpack('H', data[ind:ind+SIZE['SECTION9-BACK-L2_HEIGHT']])[0]; ind += SIZE['SECTION9-BACK-L2_HEIGHT']
            num_l2_tiles = unpack('H', data[ind:ind+SIZE['SECTION9-BACK-L2_NUM-TILES']])[0]; ind += SIZE['SECTION9-BACK-L2_NUM-TILES']
            self.back['layer_2']['unknown'] = data[ind:ind+SIZE['SECTION9-BACK-L2_UNKNOWN']]; ind += SIZE['SECTION9-BACK-L2_UNKNOWN']
            blank = unpack('H', data[ind:ind+SIZE['SECTION9-BACK-L2_BLANK']])[0]; ind += SIZE['SECTION9-BACK-L2_BLANK']
            self.back['layer_2']['tiles'] = list()
            for _ in range(num_l2_tiles):
                tile = dict()
                blank = unpack('H', data[ind:ind+SIZE['SECTION9-BACK-TILE_BLANK']])[0]; ind += SIZE['SECTION9-BACK-TILE_BLANK']
                tile['dst_x'] = unpack('h', data[ind:ind+SIZE['SECTION9-BACK-TILE_DST-X']])[0]; ind += SIZE['SECTION9-BACK-TILE_DST-X']
                tile['dst_y'] = unpack('h', data[ind:ind+SIZE['SECTION9-BACK-TILE_DST-Y']])[0]; ind += SIZE['SECTION9-BACK-TILE_DST-Y']
                tile['unknown_1'] = data[ind:ind+SIZE['SECTION9-BACK-TILE_UNKNOWN-1']]; ind += SIZE['SECTION9-BACK-TILE_UNKNOWN-1']
                tile['src_x'] = unpack('B', data[ind:ind+SIZE['SECTION9-BACK-TILE_SRC-X']])[0]; ind += SIZE['SECTION9-BACK-TILE_SRC-X']
                tile['unknown_2'] = data[ind:ind+SIZE['SECTION9-BACK-TILE_UNKNOWN-2']]; ind += SIZE['SECTION9-BACK-TILE_UNKNOWN-2']
                tile['src_y'] = unpack('B', data[ind:ind+SIZE['SECTION9-BACK-TILE_SRC-Y']])[0]; ind += SIZE['SECTION9-BACK-TILE_SRC-Y']
                tile['unknown_3'] = data[ind:ind+SIZE['SECTION9-BACK-TILE_UNKNOWN-3']]; ind += SIZE['SECTION9-BACK-TILE_UNKNOWN-3']
                tile['src_x2'] = unpack('B', data[ind:ind+SIZE['SECTION9-BACK-TILE_SRC-X2']])[0]; ind += SIZE['SECTION9-BACK-TILE_SRC-X2']
                tile['unknown_4'] = data[ind:ind+SIZE['SECTION9-BACK-TILE_UNKNOWN-4']]; ind += SIZE['SECTION9-BACK-TILE_UNKNOWN-4']
                tile['src_y2'] = unpack('B', data[ind:ind+SIZE['SECTION9-BACK-TILE_SRC-Y2']])[0]; ind += SIZE['SECTION9-BACK-TILE_SRC-Y2']
                tile['unknown_5'] = data[ind:ind+SIZE['SECTION9-BACK-TILE_UNKNOWN-5']]; ind += SIZE['SECTION9-BACK-TILE_UNKNOWN-5']
                tile['width'] = unpack('H', data[ind:ind+SIZE['SECTION9-BACK-TILE_WIDTH']])[0]; ind += SIZE['SECTION9-BACK-TILE_WIDTH']
                tile['height'] = unpack('H', data[ind:ind+SIZE['SECTION9-BACK-TILE_HEIGHT']])[0]; ind += SIZE['SECTION9-BACK-TILE_HEIGHT']
                tile['palette_ID'] = unpack('B', data[ind:ind+SIZE['SECTION9-BACK-TILE_PALETTE-ID']])[0]; ind += SIZE['SECTION9-BACK-TILE_PALETTE-ID']
                tile['unknown_6'] = data[ind:ind+SIZE['SECTION9-BACK-TILE_UNKNOWN-6']]; ind += SIZE['SECTION9-BACK-TILE_UNKNOWN-6']
                tile['ID'] = unpack('H', data[ind:ind+SIZE['SECTION9-BACK-TILE_ID']])[0]; ind += SIZE['SECTION9-BACK-TILE_ID']
                tile['param'] = unpack('B', data[ind:ind+SIZE['SECTION9-BACK-TILE_PARAM']])[0]; ind += SIZE['SECTION9-BACK-TILE_PARAM']
                tile['state'] = unpack('B', data[ind:ind+SIZE['SECTION9-BACK-TILE_STATE']])[0]; ind += SIZE['SECTION9-BACK-TILE_STATE']
                tile['blending'] = unpack('B', data[ind:ind+SIZE['SECTION9-BACK-TILE_BLENDING']])[0]; ind += SIZE['SECTION9-BACK-TILE_BLENDING']
                tile['unknown_7'] = data[ind:ind+SIZE['SECTION9-BACK-TILE_UNKNOWN-7']]; ind += SIZE['SECTION9-BACK-TILE_UNKNOWN-7']
                tile['type_trans'] = unpack('B', data[ind:ind+SIZE['SECTION9-BACK-TILE_TYPE-TRANS']])[0]; ind += SIZE['SECTION9-BACK-TILE_TYPE-TRANS']
                tile['unknown_8'] = data[ind:ind+SIZE['SECTION9-BACK-TILE_UNKNOWN-8']]; ind += SIZE['SECTION9-BACK-TILE_UNKNOWN-8']
                tile['texture_id'] = unpack('B', data[ind:ind+SIZE['SECTION9-BACK-TILE_TEXTURE-ID']])[0]; ind += SIZE['SECTION9-BACK-TILE_TEXTURE-ID']
                tile['unknown_9'] = data[ind:ind+SIZE['SECTION9-BACK-TILE_UNKNOWN-9']]; ind += SIZE['SECTION9-BACK-TILE_UNKNOWN-9']
                tile['texture_id2'] = unpack('B', data[ind:ind+SIZE['SECTION9-BACK-TILE_TEXTURE-ID2']])[0]; ind += SIZE['SECTION9-BACK-TILE_TEXTURE-ID2']
                tile['unknown_10'] = data[ind:ind+SIZE['SECTION9-BACK-TILE_UNKNOWN-10']]; ind += SIZE['SECTION9-BACK-TILE_UNKNOWN-10']
                tile['depth'] = unpack('B', data[ind:ind+SIZE['SECTION9-BACK-TILE_DEPTH']])[0]; ind += SIZE['SECTION9-BACK-TILE_DEPTH']
                tile['unknown_11'] = data[ind:ind+SIZE['SECTION9-BACK-TILE_UNKNOWN-11']]; ind += SIZE['SECTION9-BACK-TILE_UNKNOWN-11']
                tile['ID_big'] = unpack('I', data[ind:ind+SIZE['SECTION9-BACK-TILE_ID-BIG']])[0]; ind += SIZE['SECTION9-BACK-TILE_ID-BIG']
                src_x_big = unpack('I', data[ind:ind+SIZE['SECTION9-BACK-TILE_SRC-X-BIG']])[0]; ind += SIZE['SECTION9-BACK-TILE_SRC-X-BIG']
                src_y_big = unpack('I', data[ind:ind+SIZE['SECTION9-BACK-TILE_SRC-Y-BIG']])[0]; ind += SIZE['SECTION9-BACK-TILE_SRC-Y-BIG']
                blank = unpack('H', data[ind:ind+SIZE['SECTION9-BACK-TILE_BLANK-2']])[0]; ind += SIZE['SECTION9-BACK-TILE_BLANK-2']
                self.back['layer_2']['tiles'].append(tile)
            blank = unpack('H', data[ind:ind+SIZE['SECTION9-BACK-L2_BLANK-2']])[0]; ind += SIZE['SECTION9-BACK-L2_BLANK-2']

        # read layer 3
        l3_flag = unpack('B', data[ind:ind+SIZE['SECTION9-BACK-L3_FLAG']])[0]; ind += SIZE['SECTION9-BACK-L3_FLAG']
        self.back['layer_3'] = dict()
        if l3_flag != 0:
            if l3_flag != 1:
                raise ValueError(ERROR_INVALID_FIELD_FILE)
            self.back['layer_3']['width'] = unpack('H', data[ind:ind+SIZE['SECTION9-BACK-L3_WIDTH']])[0]; ind += SIZE['SECTION9-BACK-L3_WIDTH']
            self.back['layer_3']['height'] = unpack('H', data[ind:ind+SIZE['SECTION9-BACK-L3_HEIGHT']])[0]; ind += SIZE['SECTION9-BACK-L3_HEIGHT']
            num_l3_tiles = unpack('H', data[ind:ind+SIZE['SECTION9-BACK-L3_NUM-TILES']])[0]; ind += SIZE['SECTION9-BACK-L3_NUM-TILES']
            self.back['layer_3']['unknown'] = data[ind:ind+SIZE['SECTION9-BACK-L3_UNKNOWN']]; ind += SIZE['SECTION9-BACK-L3_UNKNOWN']
            blank = unpack('H', data[ind:ind+SIZE['SECTION9-BACK-L3_BLANK']])[0]; ind += SIZE['SECTION9-BACK-L3_BLANK']
            self.back['layer_3']['tiles'] = list()
            for _ in range(num_l3_tiles):
                tile = dict()
                blank = unpack('H', data[ind:ind+SIZE['SECTION9-BACK-TILE_BLANK']])[0]; ind += SIZE['SECTION9-BACK-TILE_BLANK']
                tile['dst_x'] = unpack('h', data[ind:ind+SIZE['SECTION9-BACK-TILE_DST-X']])[0]; ind += SIZE['SECTION9-BACK-TILE_DST-X']
                tile['dst_y'] = unpack('h', data[ind:ind+SIZE['SECTION9-BACK-TILE_DST-Y']])[0]; ind += SIZE['SECTION9-BACK-TILE_DST-Y']
                tile['unknown_1'] = data[ind:ind+SIZE['SECTION9-BACK-TILE_UNKNOWN-1']]; ind += SIZE['SECTION9-BACK-TILE_UNKNOWN-1']
                tile['src_x'] = unpack('B', data[ind:ind+SIZE['SECTION9-BACK-TILE_SRC-X']])[0]; ind += SIZE['SECTION9-BACK-TILE_SRC-X']
                tile['unknown_2'] = data[ind:ind+SIZE['SECTION9-BACK-TILE_UNKNOWN-2']]; ind += SIZE['SECTION9-BACK-TILE_UNKNOWN-2']
                tile['src_y'] = unpack('B', data[ind:ind+SIZE['SECTION9-BACK-TILE_SRC-Y']])[0]; ind += SIZE['SECTION9-BACK-TILE_SRC-Y']
                tile['unknown_3'] = data[ind:ind+SIZE['SECTION9-BACK-TILE_UNKNOWN-3']]; ind += SIZE['SECTION9-BACK-TILE_UNKNOWN-3']
                tile['src_x2'] = unpack('B', data[ind:ind+SIZE['SECTION9-BACK-TILE_SRC-X2']])[0]; ind += SIZE['SECTION9-BACK-TILE_SRC-X2']
                tile['unknown_4'] = data[ind:ind+SIZE['SECTION9-BACK-TILE_UNKNOWN-4']]; ind += SIZE['SECTION9-BACK-TILE_UNKNOWN-4']
                tile['src_y2'] = unpack('B', data[ind:ind+SIZE['SECTION9-BACK-TILE_SRC-Y2']])[0]; ind += SIZE['SECTION9-BACK-TILE_SRC-Y2']
                tile['unknown_5'] = data[ind:ind+SIZE['SECTION9-BACK-TILE_UNKNOWN-5']]; ind += SIZE['SECTION9-BACK-TILE_UNKNOWN-5']
                tile['width'] = unpack('H', data[ind:ind+SIZE['SECTION9-BACK-TILE_WIDTH']])[0]; ind += SIZE['SECTION9-BACK-TILE_WIDTH']
                tile['height'] = unpack('H', data[ind:ind+SIZE['SECTION9-BACK-TILE_HEIGHT']])[0]; ind += SIZE['SECTION9-BACK-TILE_HEIGHT']
                tile['palette_ID'] = unpack('B', data[ind:ind+SIZE['SECTION9-BACK-TILE_PALETTE-ID']])[0]; ind += SIZE['SECTION9-BACK-TILE_PALETTE-ID']
                tile['unknown_6'] = data[ind:ind+SIZE['SECTION9-BACK-TILE_UNKNOWN-6']]; ind += SIZE['SECTION9-BACK-TILE_UNKNOWN-6']
                tile['ID'] = unpack('H', data[ind:ind+SIZE['SECTION9-BACK-TILE_ID']])[0]; ind += SIZE['SECTION9-BACK-TILE_ID']
                tile['param'] = unpack('B', data[ind:ind+SIZE['SECTION9-BACK-TILE_PARAM']])[0]; ind += SIZE['SECTION9-BACK-TILE_PARAM']
                tile['state'] = unpack('B', data[ind:ind+SIZE['SECTION9-BACK-TILE_STATE']])[0]; ind += SIZE['SECTION9-BACK-TILE_STATE']
                tile['blending'] = unpack('B', data[ind:ind+SIZE['SECTION9-BACK-TILE_BLENDING']])[0]; ind += SIZE['SECTION9-BACK-TILE_BLENDING']
                tile['unknown_7'] = data[ind:ind+SIZE['SECTION9-BACK-TILE_UNKNOWN-7']]; ind += SIZE['SECTION9-BACK-TILE_UNKNOWN-7']
                tile['type_trans'] = unpack('B', data[ind:ind+SIZE['SECTION9-BACK-TILE_TYPE-TRANS']])[0]; ind += SIZE['SECTION9-BACK-TILE_TYPE-TRANS']
                tile['unknown_8'] = data[ind:ind+SIZE['SECTION9-BACK-TILE_UNKNOWN-8']]; ind += SIZE['SECTION9-BACK-TILE_UNKNOWN-8']
                tile['texture_id'] = unpack('B', data[ind:ind+SIZE['SECTION9-BACK-TILE_TEXTURE-ID']])[0]; ind += SIZE['SECTION9-BACK-TILE_TEXTURE-ID']
                tile['unknown_9'] = data[ind:ind+SIZE['SECTION9-BACK-TILE_UNKNOWN-9']]; ind += SIZE['SECTION9-BACK-TILE_UNKNOWN-9']
                tile['texture_id2'] = unpack('B', data[ind:ind+SIZE['SECTION9-BACK-TILE_TEXTURE-ID2']])[0]; ind += SIZE['SECTION9-BACK-TILE_TEXTURE-ID2']
                tile['unknown_10'] = data[ind:ind+SIZE['SECTION9-BACK-TILE_UNKNOWN-10']]; ind += SIZE['SECTION9-BACK-TILE_UNKNOWN-10']
                tile['depth'] = unpack('B', data[ind:ind+SIZE['SECTION9-BACK-TILE_DEPTH']])[0]; ind += SIZE['SECTION9-BACK-TILE_DEPTH']
                tile['unknown_11'] = data[ind:ind+SIZE['SECTION9-BACK-TILE_UNKNOWN-11']]; ind += SIZE['SECTION9-BACK-TILE_UNKNOWN-11']
                tile['ID_big'] = unpack('I', data[ind:ind+SIZE['SECTION9-BACK-TILE_ID-BIG']])[0]; ind += SIZE['SECTION9-BACK-TILE_ID-BIG']
                src_x_big = unpack('I', data[ind:ind+SIZE['SECTION9-BACK-TILE_SRC-X-BIG']])[0]; ind += SIZE['SECTION9-BACK-TILE_SRC-X-BIG']
                src_y_big = unpack('I', data[ind:ind+SIZE['SECTION9-BACK-TILE_SRC-Y-BIG']])[0]; ind += SIZE['SECTION9-BACK-TILE_SRC-Y-BIG']
                blank = unpack('H', data[ind:ind+SIZE['SECTION9-BACK-TILE_BLANK-2']])[0]; ind += SIZE['SECTION9-BACK-TILE_BLANK-2']
                self.back['layer_3']['tiles'].append(tile)
            blank = unpack('H', data[ind:ind+SIZE['SECTION9-BACK-L3_BLANK-2']])[0]; ind += SIZE['SECTION9-BACK-L3_BLANK-2']

        # read layer 4
        l4_flag = unpack('B', data[ind:ind+SIZE['SECTION9-BACK-L4_FLAG']])[0]; ind += SIZE['SECTION9-BACK-L4_FLAG']
        self.back['layer_4'] = dict()
        if l4_flag != 0:
            if l4_flag != 1:
                raise ValueError(ERROR_INVALID_FIELD_FILE)
            self.back['layer_4']['width'] = unpack('H', data[ind:ind+SIZE['SECTION9-BACK-L4_WIDTH']])[0]; ind += SIZE['SECTION9-BACK-L4_WIDTH']
            self.back['layer_4']['height'] = unpack('H', data[ind:ind+SIZE['SECTION9-BACK-L4_HEIGHT']])[0]; ind += SIZE['SECTION9-BACK-L4_HEIGHT']
            num_l4_tiles = unpack('H', data[ind:ind+SIZE['SECTION9-BACK-L4_NUM-TILES']])[0]; ind += SIZE['SECTION9-BACK-L4_NUM-TILES']
            self.back['layer_4']['unknown'] = data[ind:ind+SIZE['SECTION9-BACK-L4_UNKNOWN']]; ind += SIZE['SECTION9-BACK-L4_UNKNOWN']
            blank = unpack('H', data[ind:ind+SIZE['SECTION9-BACK-L4_BLANK']])[0]; ind += SIZE['SECTION9-BACK-L4_BLANK']
            self.back['layer_4']['tiles'] = list()
            for _ in range(num_l4_tiles):
                tile = dict()
                blank = unpack('H', data[ind:ind+SIZE['SECTION9-BACK-TILE_BLANK']])[0]; ind += SIZE['SECTION9-BACK-TILE_BLANK']
                tile['dst_x'] = unpack('h', data[ind:ind+SIZE['SECTION9-BACK-TILE_DST-X']])[0]; ind += SIZE['SECTION9-BACK-TILE_DST-X']
                tile['dst_y'] = unpack('h', data[ind:ind+SIZE['SECTION9-BACK-TILE_DST-Y']])[0]; ind += SIZE['SECTION9-BACK-TILE_DST-Y']
                tile['unknown_1'] = data[ind:ind+SIZE['SECTION9-BACK-TILE_UNKNOWN-1']]; ind += SIZE['SECTION9-BACK-TILE_UNKNOWN-1']
                tile['src_x'] = unpack('B', data[ind:ind+SIZE['SECTION9-BACK-TILE_SRC-X']])[0]; ind += SIZE['SECTION9-BACK-TILE_SRC-X']
                tile['unknown_2'] = data[ind:ind+SIZE['SECTION9-BACK-TILE_UNKNOWN-2']]; ind += SIZE['SECTION9-BACK-TILE_UNKNOWN-2']
                tile['src_y'] = unpack('B', data[ind:ind+SIZE['SECTION9-BACK-TILE_SRC-Y']])[0]; ind += SIZE['SECTION9-BACK-TILE_SRC-Y']
                tile['unknown_3'] = data[ind:ind+SIZE['SECTION9-BACK-TILE_UNKNOWN-3']]; ind += SIZE['SECTION9-BACK-TILE_UNKNOWN-3']
                tile['src_x2'] = unpack('B', data[ind:ind+SIZE['SECTION9-BACK-TILE_SRC-X2']])[0]; ind += SIZE['SECTION9-BACK-TILE_SRC-X2']
                tile['unknown_4'] = data[ind:ind+SIZE['SECTION9-BACK-TILE_UNKNOWN-4']]; ind += SIZE['SECTION9-BACK-TILE_UNKNOWN-4']
                tile['src_y2'] = unpack('B', data[ind:ind+SIZE['SECTION9-BACK-TILE_SRC-Y2']])[0]; ind += SIZE['SECTION9-BACK-TILE_SRC-Y2']
                tile['unknown_5'] = data[ind:ind+SIZE['SECTION9-BACK-TILE_UNKNOWN-5']]; ind += SIZE['SECTION9-BACK-TILE_UNKNOWN-5']
                tile['width'] = unpack('H', data[ind:ind+SIZE['SECTION9-BACK-TILE_WIDTH']])[0]; ind += SIZE['SECTION9-BACK-TILE_WIDTH']
                tile['height'] = unpack('H', data[ind:ind+SIZE['SECTION9-BACK-TILE_HEIGHT']])[0]; ind += SIZE['SECTION9-BACK-TILE_HEIGHT']
                tile['palette_ID'] = unpack('B', data[ind:ind+SIZE['SECTION9-BACK-TILE_PALETTE-ID']])[0]; ind += SIZE['SECTION9-BACK-TILE_PALETTE-ID']
                tile['unknown_6'] = data[ind:ind+SIZE['SECTION9-BACK-TILE_UNKNOWN-6']]; ind += SIZE['SECTION9-BACK-TILE_UNKNOWN-6']
                tile['ID'] = unpack('H', data[ind:ind+SIZE['SECTION9-BACK-TILE_ID']])[0]; ind += SIZE['SECTION9-BACK-TILE_ID']
                tile['param'] = unpack('B', data[ind:ind+SIZE['SECTION9-BACK-TILE_PARAM']])[0]; ind += SIZE['SECTION9-BACK-TILE_PARAM']
                tile['state'] = unpack('B', data[ind:ind+SIZE['SECTION9-BACK-TILE_STATE']])[0]; ind += SIZE['SECTION9-BACK-TILE_STATE']
                tile['blending'] = unpack('B', data[ind:ind+SIZE['SECTION9-BACK-TILE_BLENDING']])[0]; ind += SIZE['SECTION9-BACK-TILE_BLENDING']
                tile['unknown_7'] = data[ind:ind+SIZE['SECTION9-BACK-TILE_UNKNOWN-7']]; ind += SIZE['SECTION9-BACK-TILE_UNKNOWN-7']
                tile['type_trans'] = unpack('B', data[ind:ind+SIZE['SECTION9-BACK-TILE_TYPE-TRANS']])[0]; ind += SIZE['SECTION9-BACK-TILE_TYPE-TRANS']
                tile['unknown_8'] = data[ind:ind+SIZE['SECTION9-BACK-TILE_UNKNOWN-8']]; ind += SIZE['SECTION9-BACK-TILE_UNKNOWN-8']
                tile['texture_id'] = unpack('B', data[ind:ind+SIZE['SECTION9-BACK-TILE_TEXTURE-ID']])[0]; ind += SIZE['SECTION9-BACK-TILE_TEXTURE-ID']
                tile['unknown_9'] = data[ind:ind+SIZE['SECTION9-BACK-TILE_UNKNOWN-9']]; ind += SIZE['SECTION9-BACK-TILE_UNKNOWN-9']
                tile['texture_id2'] = unpack('B', data[ind:ind+SIZE['SECTION9-BACK-TILE_TEXTURE-ID2']])[0]; ind += SIZE['SECTION9-BACK-TILE_TEXTURE-ID2']
                tile['unknown_10'] = data[ind:ind+SIZE['SECTION9-BACK-TILE_UNKNOWN-10']]; ind += SIZE['SECTION9-BACK-TILE_UNKNOWN-10']
                tile['depth'] = unpack('B', data[ind:ind+SIZE['SECTION9-BACK-TILE_DEPTH']])[0]; ind += SIZE['SECTION9-BACK-TILE_DEPTH']
                tile['unknown_11'] = data[ind:ind+SIZE['SECTION9-BACK-TILE_UNKNOWN-11']]; ind += SIZE['SECTION9-BACK-TILE_UNKNOWN-11']
                tile['ID_big'] = unpack('I', data[ind:ind+SIZE['SECTION9-BACK-TILE_ID-BIG']])[0]; ind += SIZE['SECTION9-BACK-TILE_ID-BIG']
                src_x_big = unpack('I', data[ind:ind+SIZE['SECTION9-BACK-TILE_SRC-X-BIG']])[0]; ind += SIZE['SECTION9-BACK-TILE_SRC-X-BIG']
                src_y_big = unpack('I', data[ind:ind+SIZE['SECTION9-BACK-TILE_SRC-Y-BIG']])[0]; ind += SIZE['SECTION9-BACK-TILE_SRC-Y-BIG']
                blank = unpack('H', data[ind:ind+SIZE['SECTION9-BACK-TILE_BLANK-2']])[0]; ind += SIZE['SECTION9-BACK-TILE_BLANK-2']
                self.back['layer_4']['tiles'].append(tile)
            blank = unpack('H', data[ind:ind+SIZE['SECTION9-BACK-L4_BLANK-2']])[0]; ind += SIZE['SECTION9-BACK-L4_BLANK-2']

        # read textures
        self.textures = list()
        title = data[ind:ind+SIZE['SECTION9-TEX_TITLE']].decode().strip(); ind += SIZE['SECTION9-TEX_TITLE']
        if title != SECTION9_TEX_TITLE:
            raise ValueError(ERROR_INVALID_FIELD_FILE)
        for _ in range(SECTION9_TEX_MAX_NUM):
            exists = unpack('H', data[ind:ind+SIZE['SECTION9-TEX_TEX-EXISTS']])[0]; ind += SIZE['SECTION9-TEX_TEX-EXISTS']
            if bool(exists):
                tex = dict()
                tex['size'] = unpack('H', data[ind:ind+SIZE['SECTION9-TEX_TEX-SIZE']])[0]; ind += SIZE['SECTION9-TEX_TEX-SIZE']
                tex['depth'] = unpack('H', data[ind:ind+SIZE['SECTION9-TEX_TEX-DEPTH']])[0]; ind += SIZE['SECTION9-TEX_TEX-DEPTH']
                data_size = tex['depth'] * SECTION9_TEX_BYTES_PER_DEPTH
                tex['data'] = data[ind:ind+data_size]; ind += data_size
                self.textures.append(tex)
            else:
                self.textures.append(None)

        # read end of file
        end = data[ind:ind+SIZE['EOF_END-STRING']].decode().strip(); ind += SIZE['EOF_END-STRING']
        if end != EOF_END_STRING:
            raise ValueError(ERROR_INVALID_FIELD_FILE)
        terminator = data[ind:ind+SIZE['EOF_FILE-TERMINATOR']].decode().strip(); ind += SIZE['EOF_FILE-TERMINATOR']
        if terminator != EOF_FILE_TERMINATOR:
            raise ValueError(ERROR_INVALID_FIELD_FILE)
        if ind != len(data):
            raise ValueError(ERROR_INVALID_FIELD_FILE)

    def get_bytes(self):
        '''Return the bytes encoding this Background to repack into a Field File

        Returns:
            ``bytes``: The data to repack into a Field File
        '''
        data = bytearray()

        # write header
        data += pack('H', self.header['unknown1'])
        data += pack('H', self.header['depth'])
        data += pack('B', self.header['unknown2'])

        # write palette
        data += SECTION9_PAL_TITLE.encode()
        data += pack('I', self.palette['size'])
        data += pack('H', self.palette['palX'])
        data += pack('H', self.palette['palY'])
        data += pack('H', self.palette['width'])
        data += pack('H', self.palette['height'])
        for c in self.palette['colors']:
            data += pack('H', (c[0] << SECTION9_PAL_COLOR_R_SHIFT) | (c[1] << SECTION9_PAL_COLOR_G_SHIFT) | (c[2] << SECTION9_PAL_COLOR_B_SHIFT) | (c[3] << SECTION9_PAL_COLOR_A_SHIFT))

        # write background tiles
        data += SECTION9_BACK_TITLE.encode()

        # write layer 1
        data += pack('H', self.back['layer_1']['width'])
        data += pack('H', self.back['layer_1']['height'])
        data += pack('H', len(self.back['layer_1']['tiles']))
        data += pack('H', self.back['layer_1']['depth'])
        data += 2 * NULL_BYTE
        for tile in self.back['layer_1']['tiles']:
            data += 2 * NULL_BYTE
            data += pack('h', tile['dst_x'])
            data += pack('h', tile['dst_y'])
            data += tile['unknown_1']
            data += pack('B', tile['src_x'])
            data += tile['unknown_2']
            data += pack('B', tile['src_y'])
            data += tile['unknown_3']
            data += pack('B', tile['src_x2'])
            data += tile['unknown_4']
            data += pack('B', tile['src_y2'])
            data += tile['unknown_5']
            data += pack('H', tile['width'])
            data += pack('H', tile['height'])
            data += pack('B', tile['palette_ID'])
            data += tile['unknown_6']
            data += pack('H', tile['ID'])
            data += pack('B', tile['param'])
            data += pack('B', tile['state'])
            data += pack('B', tile['blending'])
            data += tile['unknown_7']
            data += pack('B', tile['type_trans'])
            data += tile['unknown_8']
            data += pack('B', tile['texture_id'])
            data += tile['unknown_9']
            data += pack('B', tile['texture_id2'])
            data += tile['unknown_10']
            data += pack('B', tile['depth'])
            data += tile['unknown_11']
            data += pack('I', tile['ID_big'])
            data += pack('I', int(tile['src_x'] / 16 * 625000))
            data += pack('I', int(tile['src_y'] / 16 * 625000))
            data += 2 * NULL_BYTE
        data += 2 * NULL_BYTE

        # write layer 2
        if len(self.back['layer_2']) == 0:
            data += pack('B', 0) # False
        else:
            data += pack('B', 1) # True
            data += pack('H', self.back['layer_2']['width'])
            data += pack('H', self.back['layer_2']['height'])
            data += pack('H', len(self.back['layer_2']['tiles']))
            data += self.back['layer_2']['unknown']
            data += 2 * NULL_BYTE
            for tile in self.back['layer_2']['tiles']:
                data += 2 * NULL_BYTE
                data += pack('h', tile['dst_x'])
                data += pack('h', tile['dst_y'])
                data += tile['unknown_1']
                data += pack('B', tile['src_x'])
                data += tile['unknown_2']
                data += pack('B', tile['src_y'])
                data += tile['unknown_3']
                data += pack('B', tile['src_x2'])
                data += tile['unknown_4']
                data += pack('B', tile['src_y2'])
                data += tile['unknown_5']
                data += pack('H', tile['width'])
                data += pack('H', tile['height'])
                data += pack('B', tile['palette_ID'])
                data += tile['unknown_6']
                data += pack('H', tile['ID'])
                data += pack('B', tile['param'])
                data += pack('B', tile['state'])
                data += pack('B', tile['blending'])
                data += tile['unknown_7']
                data += pack('B', tile['type_trans'])
                data += tile['unknown_8']
                data += pack('B', tile['texture_id'])
                data += tile['unknown_9']
                data += pack('B', tile['texture_id2'])
                data += tile['unknown_10']
                data += pack('B', tile['depth'])
                data += tile['unknown_11']
                data += pack('I', tile['ID_big'])
                data += pack('I', int(tile['src_x'] / 16 * 625000))
                data += pack('I', int(tile['src_y'] / 16 * 625000))
                data += 2 * NULL_BYTE
            data += 2 * NULL_BYTE

        # write layer 3
        if len(self.back['layer_3']) == 0:
            data += pack('B', 0) # False
        else:
            data += pack('B', 1) # True
            data += pack('H', self.back['layer_3']['width'])
            data += pack('H', self.back['layer_3']['height'])
            data += pack('H', len(self.back['layer_3']['tiles']))
            data += self.back['layer_3']['unknown']
            data += 2 * NULL_BYTE
            for tile in self.back['layer_3']['tiles']:
                data += 2 * NULL_BYTE
                data += pack('h', tile['dst_x'])
                data += pack('h', tile['dst_y'])
                data += tile['unknown_1']
                data += pack('B', tile['src_x'])
                data += tile['unknown_2']
                data += pack('B', tile['src_y'])
                data += tile['unknown_3']
                data += pack('B', tile['src_x2'])
                data += tile['unknown_4']
                data += pack('B', tile['src_y2'])
                data += tile['unknown_5']
                data += pack('H', tile['width'])
                data += pack('H', tile['height'])
                data += pack('B', tile['palette_ID'])
                data += tile['unknown_6']
                data += pack('H', tile['ID'])
                data += pack('B', tile['param'])
                data += pack('B', tile['state'])
                data += pack('B', tile['blending'])
                data += tile['unknown_7']
                data += pack('B', tile['type_trans'])
                data += tile['unknown_8']
                data += pack('B', tile['texture_id'])
                data += tile['unknown_9']
                data += pack('B', tile['texture_id2'])
                data += tile['unknown_10']
                data += pack('B', tile['depth'])
                data += tile['unknown_11']
                data += pack('I', tile['ID_big'])
                data += pack('I', int(tile['src_x'] / 16 * 625000))
                data += pack('I', int(tile['src_y'] / 16 * 625000))
                data += 2 * NULL_BYTE
            data += 2 * NULL_BYTE

        # write layer 4
        if len(self.back['layer_4']) == 0:
            data += pack('B', 0) # False
        else:
            data += pack('B', 1) # True
            data += pack('H', self.back['layer_4']['width'])
            data += pack('H', self.back['layer_4']['height'])
            data += pack('H', len(self.back['layer_4']['tiles']))
            data += self.back['layer_4']['unknown']
            data += 2 * NULL_BYTE
            for tile in self.back['layer_4']['tiles']:
                data += 2 * NULL_BYTE
                data += pack('h', tile['dst_x'])
                data += pack('h', tile['dst_y'])
                data += tile['unknown_1']
                data += pack('B', tile['src_x'])
                data += tile['unknown_2']
                data += pack('B', tile['src_y'])
                data += tile['unknown_3']
                data += pack('B', tile['src_x2'])
                data += tile['unknown_4']
                data += pack('B', tile['src_y2'])
                data += tile['unknown_5']
                data += pack('H', tile['width'])
                data += pack('H', tile['height'])
                data += pack('B', tile['palette_ID'])
                data += tile['unknown_6']
                data += pack('H', tile['ID'])
                data += pack('B', tile['param'])
                data += pack('B', tile['state'])
                data += pack('B', tile['blending'])
                data += tile['unknown_7']
                data += pack('B', tile['type_trans'])
                data += tile['unknown_8']
                data += pack('B', tile['texture_id'])
                data += tile['unknown_9']
                data += pack('B', tile['texture_id2'])
                data += tile['unknown_10']
                data += pack('B', tile['depth'])
                data += tile['unknown_11']
                data += pack('I', tile['ID_big'])
                data += pack('I', int(tile['src_x'] / 16 * 625000))
                data += pack('I', int(tile['src_y'] / 16 * 625000))
                data += 2 * NULL_BYTE
            data += 2 * NULL_BYTE

        # write textures
        data += SECTION9_TEX_TITLE.encode()
        for tex in self.textures:
            if tex is None:
                data += pack('H', 0) # False
            else:
                data += pack('H', 1) # True
                data += pack('H', tex['size'])
                data += pack('H', tex['depth'])
                data += tex['data']

        # write end of file
        data += EOF_END_STRING.encode()
        data += EOF_FILE_TERMINATOR.encode()
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
        self.model_loader = ModelLoader(data[starts[2]+SIZE['SECTION-LENGTH']:starts[3]])
        self.palette = Palette(data[starts[3]+SIZE['SECTION-LENGTH']:starts[4]])
        self.walkmesh = Walkmesh(data[starts[4]+SIZE['SECTION-LENGTH']:starts[5]])
        self.tile_map = TileMap(data[starts[5]+SIZE['SECTION-LENGTH']:starts[6]])
        self.encounter = Encounter(data[starts[6]+SIZE['SECTION-LENGTH']:starts[7]])
        self.triggers = Triggers(data[starts[7]+SIZE['SECTION-LENGTH']:starts[8]])
        self.background = Background(data[starts[8]+SIZE['SECTION-LENGTH']:])

    def get_bytes(self, lzss_compress=False):
        '''Return the bytes encoding this Field file

        Args:
            ``lzss_compress`` (``bool``): ``True`` to LZSS-compress the data before returning, otherwise ``False`` to return the uncompressed data

        Returns:
            ``bytes``: The data encoding this Field file
        '''
        # convert all sections to bytes first
        section_bytes = [
            self.field_script.get_bytes(),
            self.camera_matrix.get_bytes(),
            self.model_loader.get_bytes(),
            self.palette.get_bytes(),
            self.walkmesh.get_bytes(),
            self.tile_map.get_bytes(),
            self.encounter.get_bytes(),
            self.triggers.get_bytes(),
            self.background.get_bytes(),
        ]

        # merge into output
        data = bytearray()
        data += NULL_BYTE*SIZE['HEADER_BLANK']
        data += pack('I', len(SECTION_NAME))
        start_ind = len(data) + SIZE['HEADER_SECTION-START']*len(SECTION_NAME)
        for sec in section_bytes:
            data += pack('I', start_ind); start_ind += len(sec) + SIZE['HEADER_SECTION-START']
        for sec in section_bytes:
            data += pack('I', len(sec)); data += sec
        if lzss_compress:
            return compress_lzss(data)
        else:
            return data

    def get_bg_image(self):
        '''Return a Pillow Image object of this Field file's Background

        Returns:
            ``Image``: A Pillow Image object of this Field file's Background
        '''
        from PIL import Image

        # compute image width and height
        min_width = 0; max_width = 0
        min_height = 0; max_height = 0
        for k in ['layer_1', 'layer_2', 'layer_3', 'layer_4']:
            if 'tiles' not in self.background.back[k]:
                continue
            for tile in self.background.back[k]['tiles']:
                if tile['dst_x'] >= 0 and tile['dst_x'] > max_width:
                    max_width = tile['dst_x']
                elif tile['dst_x'] < 0 and -tile['dst_x'] > min_width:
                    min_width = -tile['dst_x']
                if tile['dst_y'] >= 0 and tile['dst_y'] > max_height:
                    max_height = tile['dst_y']
                elif tile['dst_y'] < 0 and -tile['dst_y'] > min_height:
                    min_height = -tile['dst_y']
        width = min_width + max_width + 16
        height = min_height + max_height + 16
        center_x = int(width/2); center_y = int(height/2)

        # build Pillow image
        img = Image.new('RGB', (width,height), (0,0,0)); done = set()
        for k in ['layer_1', 'layer_2', 'layer_3', 'layer_4']:
            if 'tiles' not in self.background.back[k]:
                continue
            for tile in self.background.back[k]['tiles']:
                color_page = self.palette.color_pages[tile['palette_ID']]
                raw = self.background.textures[tile['texture_id']]['data']
                if tile['width'] == 0:
                    width = 16
                else:
                    width = tile['width']
                if tile['height'] == 0:
                    height = 16
                else:
                    height = tile['height']
                for dx in range(0, width):
                    for dy in range(0, height):
                        color_ind = raw[(tile['src_y']+dy)*256 + tile['src_x'] + dx]
                        color_raw = color_page[color_ind]
                        img_x = tile['dst_x']+dx+center_x; img_y = tile['dst_y']+dy+center_y
                        curr_color = img.getpixel((img_x,img_y))
                        color = [min(255,curr_color[i]+(color_raw[i] << 3)) for i in range(3)]
                        img.putpixel((img_x,img_y), tuple(color)); done.add((img_x,img_y))
        return img
