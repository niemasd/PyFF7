#!/usr/bin/env python3
'''
Functions and classes for handling TEX files
Niema Moshiri 2019
'''
from PIL import Image
from struct import pack,unpack

# size of various items in an TEX file (in bytes)
SIZE = {
    # Header
    'HEADER_VERSION':                      4, # Header: Version (must be 1)
    'HEADER_UNKNOWN1':                     4, # Header: Unknown 1
    'HEADER_COLOR-KEY-FLAG':               4, # Header: Color Key Flag
    'HEADER_UNKNOWN2':                     4, # Header: Unknown 2
    'HEADER_UNKNOWN3':                     4, # Header: Unknown 3
    'HEADER_MIN-BITS-PER-COLOR':           4, # Header: Minimum Number of Bits per Color
    'HEADER_MAX-BITS-PER-COLOR':           4, # Header: Maximum Number of Bits per Color
    'HEADER_MIN-ALPHA-BITS':               4, # Header: Minimum Number of Alpha Bits
    'HEADER_MAX-ALPHA-BITS':               4, # Header: Maximum Number of Alpha Bits
    'HEADER_MIN-BITS-PER-PIXEL':           4, # Header: Minimum Number of Bits per Pixel
    'HEADER_MAX-BITS-PER-PIXEL':           4, # Header: Maximum Number of Bits per Pixel
    'HEADER_UNKNOWN4':                     4, # Header: Unknown 4
    'HEADER_NUM-PALETTES':                 4, # Header: Number of Palettes
    'HEADER_NUM-COLORS-PER-PALETTE':       4, # Header: Number of Colors per Palette
    'HEADER_BIT-DEPTH':                    4, # Header: Bit Depth
    'HEADER_IMAGE-WIDTH':                  4, # Header: Image Width
    'HEADER_IMAGE-HEIGHT':                 4, # Header: Image Height
    'HEADER_BYTES-PER-ROW':                4, # Header: Bytes per Row (usually ignored and assumed to be bytes per pixel * width)
    'HEADER_UNKNOWN5':                     4, # Header: Unknown 5
    'HEADER_PALETTE-FLAG':                 4, # Header: Palette Flag (indicates the presence of a palette)
    'HEADER_BITS-PER-INDEX':               4, # Header: Bits per Index (always 0 for non-paletted images)
    'HEADER_INDEXED-TO-8BIT-FLAG':         4, # Header: Indexed-to-8bit Flag (never used in FF7)
    'HEADER_PALETTE-SIZE':                 4, # Header: Palette Size (always number of palettes * colors per palette)
    'HEADER_NUM-COLORS-PER-PALETTE-DUP':   4, # Header: Number of Colors per Palette again (may be 0 sometimes; the first value will be used anyway)
    'HEADER_RUNTIME-DATA1':                4, # Header: Runtime Data 1 (ignored on load)
    'HEADER_BITS-PER-PIXEL':               4, # Header: Number of Bits per Pixel
    'HEADER_BYTES-PER-PIXEL':              4, # Header: Number of Bytes per Pixel

    # Pixel Format
    'PIXEL-FORMAT_NUM-RED-BITS':           4, # Pixel Format: Number of Red Bits
    'PIXEL-FORMAT_NUM-GREEN-BITS':         4, # Pixel Format: Number of Green Bits
    'PIXEL-FORMAT_NUM-BLUE-BITS':          4, # Pixel Format: Number of Blue Bits
    'PIXEL-FORMAT_NUM-ALPHA-BITS':         4, # Pixel Format: Number of Alpha Bits
    'PIXEL-FORMAT_RED-BITMASK':            4, # Pixel Format: Red Bitmask
    'PIXEL-FORMAT_GREEN-BITMASK':          4, # Pixel Format: Green Bitmask
    'PIXEL-FORMAT_BLUE-BITMASK':           4, # Pixel Format: Blue Bitmask
    'PIXEL-FORMAT_ALPHA-BITMASK':          4, # Pixel Format: Alpha Bitmask
    'PIXEL-FORMAT_RED-SHIFT':              4, # Pixel Format: Red Shift
    'PIXEL-FORMAT_GREEN-SHIFT':            4, # Pixel Format: Green Shift
    'PIXEL-FORMAT_BLUE-SHIFT':             4, # Pixel Format: Blue Shift
    'PIXEL-FORMAT_ALPHA-SHIFT':            4, # Pixel Format: Alpha Shift
    'PIXEL-FORMAT_8-MINUS-NUM-RED-BITS':   4, # Pixel Format: 8 - Number of Red Bits (always ignored)
    'PIXEL-FORMAT_8-MINUS-NUM-GREEN-BITS': 4, # Pixel Format: 8 - Number of Green Bits (always ignored)
    'PIXEL-FORMAT_8-MINUS-NUM-BLUE-BITS':  4, # Pixel Format: 8 - Number of Blue Bits (always ignored)
    'PIXEL-FORMAT_8-MINUS-NUM-ALPHA-BITS': 4, # Pixel Format: 8 - Number of Alpha Bits (always ignored)
    'PIXEL-FORMAT_RED-MAX':                4, # Pixel Format: Red Max
    'PIXEL-FORMAT_GREEN-MAX':              4, # Pixel Format: Green Max
    'PIXEL-FORMAT_BLUE-MAX':               4, # Pixel Format: Blue Max
    'PIXEL-FORMAT_ALPHA-MAX':              4, # Pixel Format: Alpha Max

    # Header 2
    'HEADER-2_COLOR-KEY-ARRAY-FLAG':       4, # Header 2: Color Key Array Flag
    'HEADER-2_RUNTIME-DATA2':              4, # Header 2: Runtime Data 2
    'HEADER-2_REFERENCE-ALPHA':            4, # Header 2: Reference Alpha
    'HEADER-2_RUNTIME-DATA3':              4, # Header 2: Runtime Data 3
    'HEADER-2_UNKNOWN6':                   4, # Header 2: Unknown 6
    'HEADER-2_PALETTE-INDEX':              4, # Header 2: Palette Index (Runtime Data)
    'HEADER-2_RUNTIME-DATA4':              8, # Header 2: Runtime Data 4
    'HEADER-2_UNKNOWN7':                  16, # Header 2: Unknown 7

    # Palette Entry (BGRA)
    'PALETTE-ENTRY_BLUE':                  1, # Palette Entry: Blue
    'PALETTE-ENTRY_GREEN':                 1, # Palette Entry: Green
    'PALETTE-ENTRY_RED':                   1, # Palette Entry: Red
    'PALETTE-ENTRY_ALPHA':                 1, # Palette Entry: Alpha
}
SIZE['HEADER'] = sum(SIZE[k] for k in SIZE if k.startswith('HEADER_')) # 108

# other defaults
DEFAULT_VERSION = 1
BITS_PER_BYTE = 8
BYTES_TO_FORMAT = {1:'B', 2:'H', 4:'I'}

# error messages
ERROR_INVALID_TEX_FILE = "Invalid TEX file"

class TEX:
    '''TEX file class'''
    def __init__(self, data):
        '''``TEX`` constructor

        Args:
            ``data`` (``bytes``): The input TEX file
        '''
        if isinstance(data,str): # if filename instead of bytes, read bytes
            with open(data,'rb') as f:
                data = f.read()
        ind = 0

        # read header
        self.version = unpack('I', data[ind:ind+SIZE['HEADER_VERSION']])[0]; ind += SIZE['HEADER_VERSION']
        if self.version != DEFAULT_VERSION:
            raise ValueError(ERROR_INVALID_TEX_FILE)
        self.unknown1 = data[ind:ind+SIZE['HEADER_VERSION']]; ind += SIZE['HEADER_VERSION']
        color_key_flag = unpack('I', data[ind:ind+SIZE['HEADER_COLOR-KEY-FLAG']])[0]; ind += SIZE['HEADER_COLOR-KEY-FLAG']
        self.unknown2 = data[ind:ind+SIZE['HEADER_UNKNOWN2']]; ind += SIZE['HEADER_UNKNOWN2']
        self.unknown3 = data[ind:ind+SIZE['HEADER_UNKNOWN3']]; ind += SIZE['HEADER_UNKNOWN3']
        self.min_bits_per_color = unpack('I', data[ind:ind+SIZE['HEADER_MIN-BITS-PER-COLOR']])[0]; ind += SIZE['HEADER_MIN-BITS-PER-COLOR']
        self.max_bits_per_color = unpack('I', data[ind:ind+SIZE['HEADER_MAX-BITS-PER-COLOR']])[0]; ind += SIZE['HEADER_MAX-BITS-PER-COLOR']
        self.min_alpha_bits = unpack('I', data[ind:ind+SIZE['HEADER_MIN-ALPHA-BITS']])[0]; ind += SIZE['HEADER_MIN-ALPHA-BITS']
        self.max_alpha_bits = unpack('I', data[ind:ind+SIZE['HEADER_MAX-ALPHA-BITS']])[0]; ind += SIZE['HEADER_MAX-ALPHA-BITS']
        self.min_bits_per_pixel = unpack('I', data[ind:ind+SIZE['HEADER_MIN-BITS-PER-PIXEL']])[0]; ind += SIZE['HEADER_MIN-BITS-PER-PIXEL']
        self.max_bits_per_pixel = unpack('I', data[ind:ind+SIZE['HEADER_MAX-BITS-PER-PIXEL']])[0]; ind += SIZE['HEADER_MAX-BITS-PER-PIXEL']
        self.unknown4 = data[ind:ind+SIZE['HEADER_UNKNOWN4']]; ind += SIZE['HEADER_UNKNOWN4']
        num_palettes = unpack('I', data[ind:ind+SIZE['HEADER_NUM-PALETTES']])[0]; ind += SIZE['HEADER_NUM-PALETTES']
        num_colors_per_palette = unpack('I', data[ind:ind+SIZE['HEADER_NUM-COLORS-PER-PALETTE']])[0]; ind += SIZE['HEADER_NUM-COLORS-PER-PALETTE']
        self.bit_depth = unpack('I', data[ind:ind+SIZE['HEADER_BIT-DEPTH']])[0]; ind += SIZE['HEADER_BIT-DEPTH']
        width = unpack('I', data[ind:ind+SIZE['HEADER_IMAGE-WIDTH']])[0]; ind += SIZE['HEADER_IMAGE-WIDTH']
        height = unpack('I', data[ind:ind+SIZE['HEADER_IMAGE-HEIGHT']])[0]; ind += SIZE['HEADER_IMAGE-HEIGHT']
        bytes_per_row = unpack('I', data[ind:ind+SIZE['HEADER_BYTES-PER-ROW']])[0]; ind += SIZE['HEADER_BYTES-PER-ROW']
        self.unknown5 = data[ind:ind+SIZE['HEADER_UNKNOWN5']]; ind += SIZE['HEADER_UNKNOWN5']
        palette_flag = unpack('I', data[ind:ind+SIZE['HEADER_PALETTE-FLAG']])[0]; ind += SIZE['HEADER_PALETTE-FLAG']
        self.bits_per_index = unpack('I', data[ind:ind+SIZE['HEADER_BITS-PER-INDEX']])[0]; ind += SIZE['HEADER_BITS-PER-INDEX']
        self.indexed_to_8bit_flag = unpack('I', data[ind:ind+SIZE['HEADER_INDEXED-TO-8BIT-FLAG']])[0]; ind += SIZE['HEADER_INDEXED-TO-8BIT-FLAG']
        palette_size = unpack('I', data[ind:ind+SIZE['HEADER_PALETTE-SIZE']])[0]; ind += SIZE['HEADER_PALETTE-SIZE']
        num_colors_per_palette_dup = unpack('I', data[ind:ind+SIZE['HEADER_NUM-COLORS-PER-PALETTE-DUP']])[0]; ind += SIZE['HEADER_NUM-COLORS-PER-PALETTE-DUP']
        self.runtime_data1 = data[ind:ind+SIZE['HEADER_RUNTIME-DATA1']]; ind += SIZE['HEADER_RUNTIME-DATA1']
        bits_per_pixel = unpack('I', data[ind:ind+SIZE['HEADER_BITS-PER-PIXEL']])[0]; ind += SIZE['HEADER_BITS-PER-PIXEL']
        bytes_per_pixel = unpack('I', data[ind:ind+SIZE['HEADER_BYTES-PER-PIXEL']])[0]; ind += SIZE['HEADER_BYTES-PER-PIXEL']

        # read pixel format
        self.num_red_bits = unpack('I', data[ind:ind+SIZE['PIXEL-FORMAT_NUM-RED-BITS']])[0]; ind += SIZE['PIXEL-FORMAT_NUM-RED-BITS']
        self.num_green_bits = unpack('I', data[ind:ind+SIZE['PIXEL-FORMAT_NUM-GREEN-BITS']])[0]; ind += SIZE['PIXEL-FORMAT_NUM-GREEN-BITS']
        self.num_blue_bits = unpack('I', data[ind:ind+SIZE['PIXEL-FORMAT_NUM-BLUE-BITS']])[0]; ind += SIZE['PIXEL-FORMAT_NUM-BLUE-BITS']
        self.num_alpha_bits = unpack('I', data[ind:ind+SIZE['PIXEL-FORMAT_NUM-ALPHA-BITS']])[0]; ind += SIZE['PIXEL-FORMAT_NUM-ALPHA-BITS']
        self.red_bitmask = unpack('I', data[ind:ind+SIZE['PIXEL-FORMAT_RED-BITMASK']])[0]; ind += SIZE['PIXEL-FORMAT_RED-BITMASK']
        self.green_bitmask = unpack('I', data[ind:ind+SIZE['PIXEL-FORMAT_GREEN-BITMASK']])[0]; ind += SIZE['PIXEL-FORMAT_GREEN-BITMASK']
        self.blue_bitmask = unpack('I', data[ind:ind+SIZE['PIXEL-FORMAT_BLUE-BITMASK']])[0]; ind += SIZE['PIXEL-FORMAT_BLUE-BITMASK']
        self.alpha_bitmask = unpack('I', data[ind:ind+SIZE['PIXEL-FORMAT_ALPHA-BITMASK']])[0]; ind += SIZE['PIXEL-FORMAT_ALPHA-BITMASK']
        self.red_shift = unpack('I', data[ind:ind+SIZE['PIXEL-FORMAT_RED-SHIFT']])[0]; ind += SIZE['PIXEL-FORMAT_RED-SHIFT']
        self.green_shift = unpack('I', data[ind:ind+SIZE['PIXEL-FORMAT_GREEN-SHIFT']])[0]; ind += SIZE['PIXEL-FORMAT_GREEN-SHIFT']
        self.blue_shift = unpack('I', data[ind:ind+SIZE['PIXEL-FORMAT_BLUE-SHIFT']])[0]; ind += SIZE['PIXEL-FORMAT_BLUE-SHIFT']
        self.alpha_shift = unpack('I', data[ind:ind+SIZE['PIXEL-FORMAT_ALPHA-SHIFT']])[0]; ind += SIZE['PIXEL-FORMAT_ALPHA-SHIFT']
        self.eight_minus_num_red_bits = unpack('I', data[ind:ind+SIZE['PIXEL-FORMAT_8-MINUS-NUM-RED-BITS']])[0]; ind += SIZE['PIXEL-FORMAT_8-MINUS-NUM-RED-BITS']
        self.eight_minus_num_green_bits = unpack('I', data[ind:ind+SIZE['PIXEL-FORMAT_8-MINUS-NUM-GREEN-BITS']])[0]; ind += SIZE['PIXEL-FORMAT_8-MINUS-NUM-GREEN-BITS']
        self.eight_minus_num_blue_bits = unpack('I', data[ind:ind+SIZE['PIXEL-FORMAT_8-MINUS-NUM-BLUE-BITS']])[0]; ind += SIZE['PIXEL-FORMAT_8-MINUS-NUM-BLUE-BITS']
        self.eight_minus_num_alpha_bits = unpack('I', data[ind:ind+SIZE['PIXEL-FORMAT_8-MINUS-NUM-ALPHA-BITS']])[0]; ind += SIZE['PIXEL-FORMAT_8-MINUS-NUM-ALPHA-BITS']
        self.red_max = unpack('I', data[ind:ind+SIZE['PIXEL-FORMAT_RED-MAX']])[0]; ind += SIZE['PIXEL-FORMAT_RED-MAX']
        self.green_max = unpack('I', data[ind:ind+SIZE['PIXEL-FORMAT_GREEN-MAX']])[0]; ind += SIZE['PIXEL-FORMAT_GREEN-MAX']
        self.blue_max = unpack('I', data[ind:ind+SIZE['PIXEL-FORMAT_BLUE-MAX']])[0]; ind += SIZE['PIXEL-FORMAT_BLUE-MAX']
        self.alpha_max = unpack('I', data[ind:ind+SIZE['PIXEL-FORMAT_ALPHA-MAX']])[0]; ind += SIZE['PIXEL-FORMAT_ALPHA-MAX']

        # read header 2
        self.color_key_array_flag = unpack('I', data[ind:ind+SIZE['HEADER-2_COLOR-KEY-ARRAY-FLAG']])[0]; ind += SIZE['HEADER-2_COLOR-KEY-ARRAY-FLAG']
        self.runtime_data2 = data[ind:ind+SIZE['HEADER-2_RUNTIME-DATA2']]; ind += SIZE['HEADER-2_RUNTIME-DATA2']
        self.reference_alpha = unpack('I', data[ind:ind+SIZE['HEADER-2_REFERENCE-ALPHA']])[0]; ind += SIZE['HEADER-2_REFERENCE-ALPHA']
        self.runtime_data3 = data[ind:ind+SIZE['HEADER-2_RUNTIME-DATA3']]; ind += SIZE['HEADER-2_RUNTIME-DATA3']
        self.unknown6 = data[ind:ind+SIZE['HEADER-2_UNKNOWN6']]; ind += SIZE['HEADER-2_UNKNOWN6']
        self.palette_index = unpack('I', data[ind:ind+SIZE['HEADER-2_PALETTE-INDEX']])[0]; ind += SIZE['HEADER-2_PALETTE-INDEX']
        self.runtime_data4 = data[ind:ind+SIZE['HEADER-2_RUNTIME-DATA4']]; ind += SIZE['HEADER-2_RUNTIME-DATA4']
        self.unknown7 = data[ind:ind+SIZE['HEADER-2_UNKNOWN7']]; ind += SIZE['HEADER-2_UNKNOWN7']

        # read palette data
        palette = list()
        if palette_flag == 1:
            for _ in range(palette_size):
                curr_blue = unpack('B', data[ind:ind+SIZE['PALETTE-ENTRY_BLUE']])[0]; ind += SIZE['PALETTE-ENTRY_BLUE']
                curr_green = unpack('B', data[ind:ind+SIZE['PALETTE-ENTRY_GREEN']])[0]; ind += SIZE['PALETTE-ENTRY_GREEN']
                curr_red = unpack('B', data[ind:ind+SIZE['PALETTE-ENTRY_RED']])[0]; ind += SIZE['PALETTE-ENTRY_RED']
                curr_alpha = unpack('B', data[ind:ind+SIZE['PALETTE-ENTRY_ALPHA']])[0]; ind += SIZE['PALETTE-ENTRY_ALPHA']
                palette.append(tuple([curr_red, curr_green, curr_blue, curr_alpha])) # I read them as BGRA, but I like saving them as RGBA

        # read pixel data
        self.image = Image.new('RGBA', (width,height))
        bpp_over_4 = int(bytes_per_pixel/4) # for use with Pixel Format Specification
        for y in range(height):
            for x in range(width):
                if len(palette) == 0:
                    cp = list()
                    for _ in range(4): # BGRA format
                        cp.append(unpack(BYTES_TO_FORMAT[bpp_over_4], data[ind:ind+bpp_over_4])[0]); ind += bpp_over_4
                    color = (cp[2], cp[1], cp[0], cp[3])
                else:
                    color = palette[unpack(BYTES_TO_FORMAT[bytes_per_pixel], data[ind:ind+bytes_per_pixel])[0]]; ind += bytes_per_pixel
                self.image.putpixel((x,y), color)

    def get_bytes(self):
        '''Return the bytes encoding this TEX file

        Returns:
            ``bytes``: The data encoding this TEX file
        '''
        # prepare stuff
        out = bytearray()
        pal = list(set(self.image.getdata()))
        col_to_ind = {c:i for i,c in enumerate(pal)}
        if len(pal) <= 256:
            bytes_per_pixel = 1; pal_index_format = 'B'
        elif len(pal) <= 65536:
            bytes_per_pixel = 2; pal_index_format = 'H'
        else:
            bytes_per_pixel = 4; pal_index_format = 'I'
        bits_per_pixel = BITS_PER_BYTE * bytes_per_pixel

        # add header
        out += pack('I', 1)                 # version
        out += self.unknown1
        out += pack('I', 1)                 # color key flag
        out += self.unknown2
        out += self.unknown3
        out += pack('I', 0)                 # minimum bits per color
        out += pack('I', 8)                 # maximum bits per color
        out += pack('I', 0)                 # minimum alpha bits
        out += pack('I', 8)                 # maximum alpha bits
        out += pack('I', 8)                 # minimum bits per pixel
        out += pack('I', 32)                # maximum bits per pixel
        out += self.unknown4
        out += pack('I', 1)                 # number of palettes
        out += pack('I', len(pal))          # number of colors per palette
        out += pack('I', self.bit_depth)
        out += pack('I', self.get_width())
        out += pack('I', self.get_height())
        out += pack('I', bytes_per_pixel*self.get_width())
        out += self.unknown5
        out += pack('I', 1)                 # palette flag
        out += pack('I', BITS_PER_BYTE)
        out += pack('I', 0)                 # IndexedTo8bitsFlag
        out += pack('I', len(pal))          # palette size
        out += pack('I', len(pal))          # number of colors per palette (duplicate)
        out += self.runtime_data1
        out += pack('I', bits_per_pixel)
        out += pack('I', bytes_per_pixel)

        # don't use pixel format (just use palette instead)
        for _ in range(20):
            out += pack('I', 0)

        # add header 2
        out += pack('I', 0)                 # color key array flag
        out += self.runtime_data2
        out += pack('I', 255)               # reference alpha
        out += self.runtime_data3
        out += self.unknown6
        out += pack('I', 0)                 # palette index
        out += self.runtime_data4
        out += self.unknown7

        # add palette data
        for r,g,b,a in pal:
            out += pack('B', b)
            out += pack('B', g)
            out += pack('B', r)
            out += pack('B', a)

        # add pixels
        for y in range(self.get_height()):
            for x in range(self.get_width()):
                out += pack(pal_index_format, col_to_ind[self.image.getpixel((x,y))])
        return out

    def get_height(self):
        '''Get the image height of this TEX file

        Returns:
            ``int``: The image height of this TEX file
        '''
        return self.image.size[1]

    def get_width(self):
        '''Get the image width of this TEX file

        Returns:
            ``int``: The image width of this TEX file
        '''
        return self.image.size[0]

    def get_image(self):
        '''Get a Pillow image object from this TEX file

        Returns:
            ``Image``: A Pillow image object
        '''
        return self.image

    def change_image(self, img):
        '''Change this TEX file's image

        Args:
            ``img`` (``Image``): The image to set this TEX file to
        '''
        if isinstance(img,str):
            img = Image.open(img)
        self.image = img.convert('RGBA')

    def num_colors(self):
        '''Return the number of unique RGBA colors in this TEX file's image

        Returns:
            ``int``: The number of unique RGBA colors in this TEX file's image
        '''
        return len(set(self.image.getdata()))

    def unique_colors(self):
        '''Return a set containing the unique RGBA colors in this TEX file's image

        Returns:
            ``set`` of ``tuple`` of ``int``: The unique RGBA colors in this TEX file's image
        '''
        return set(self.image.getdata())
