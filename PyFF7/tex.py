#!/usr/bin/env python3
'''
Functions and classes for handling TEX files
Niema Moshiri 2019
'''
from . import BYTES_TO_FORMAT,NULL_BYTE
from .field import color_to_rgba as two_byte_color_to_rgba
from .field import color_convert_bit
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
    'HEADER-2_RUNTIME-DATA4':              4, # Header 2: Runtime Data 4
    'HEADER-2_RUNTIME-DATA5':              4, # Header 2: Runtime Data 5
    'HEADER-2_UNKNOWN7':                   4, # Header 2: Unknown 7
    'HEADER-2_UNKNOWN8':                   4, # Header 2: Unknown 8
    'HEADER-2_UNKNOWN9':                   4, # Header 2: Unknown 9
    'HEADER-2_UNKNOWN10':                  4, # Header 2: Unknown 10
    'HEADER-2_UNKNOWN11':                  4, # Header 2: Unknown 11 (TEX version 2 only)

    # Palette Entry (BGRA)
    'PALETTE-ENTRY_BLUE':                  1, # Palette Entry: Blue
    'PALETTE-ENTRY_GREEN':                 1, # Palette Entry: Green
    'PALETTE-ENTRY_RED':                   1, # Palette Entry: Red
    'PALETTE-ENTRY_ALPHA':                 1, # Palette Entry: Alpha
}
SIZE['HEADER'] = sum(SIZE[k] for k in SIZE if k.startswith('HEADER_')) # 108

# other defaults
DEFAULT_VERSION = 1

# error messages
ERROR_INVALID_TEX_FILE = "Invalid TEX file"

class TEX:
    '''TEX file class'''
    def __init__(self, data):
        '''``TEX`` constructor

        Args:
            ``data`` (``bytes``): The input TEX file
        '''
        # if data is a PIL Image, just create TEX
        typestr = str(type(data)).lstrip("<class '").rstrip("'>")
        if typestr.startswith('PIL.') and 'Image' in typestr:
            self.images = [data.convert('RGBA')]; return

        # if data is filename, load actual bytes
        if isinstance(data,str): # if filename instead of bytes, read bytes
            with open(data,'rb') as f:
                data = f.read()

        # parse header
        version = unpack('I', data[0:0+SIZE['HEADER_VERSION']])[0]
        if version not in {1,2}:
            raise ValueError("Invalid version number: %d" % version)
        num_palettes = unpack('I', data[48:48+SIZE['HEADER_NUM-PALETTES']])[0]
        num_colors_per_palette = unpack('I', data[52:52+SIZE['HEADER_NUM-COLORS-PER-PALETTE']])[0]
        width = unpack('I', data[60:60+SIZE['HEADER_IMAGE-WIDTH']])[0]
        height = unpack('I', data[64:64+SIZE['HEADER_IMAGE-HEIGHT']])[0]
        palette_flag = unpack('I', data[76:76+SIZE['HEADER_PALETTE-FLAG']])[0]
        palette_size = unpack('I', data[88:88+SIZE['HEADER_PALETTE-SIZE']])[0]
        bytes_per_pixel = unpack('I', data[104:104+SIZE['HEADER_BYTES-PER-PIXEL']])[0]

        # read palette data
        palette = list()
        if version == 1:
            ind = 236
        else: # version 2 (e.g. FF8)
            ind = 240
        if palette_flag == 1:
            for _ in range(num_palettes):
                palette.append(list())
                for __ in range(num_colors_per_palette):
                    curr_blue = unpack('B', data[ind:ind+SIZE['PALETTE-ENTRY_BLUE']])[0]; ind += SIZE['PALETTE-ENTRY_BLUE']
                    curr_green = unpack('B', data[ind:ind+SIZE['PALETTE-ENTRY_GREEN']])[0]; ind += SIZE['PALETTE-ENTRY_GREEN']
                    curr_red = unpack('B', data[ind:ind+SIZE['PALETTE-ENTRY_RED']])[0]; ind += SIZE['PALETTE-ENTRY_RED']
                    curr_alpha = unpack('B', data[ind:ind+SIZE['PALETTE-ENTRY_ALPHA']])[0]; ind += SIZE['PALETTE-ENTRY_ALPHA']
                    palette[-1].append(tuple([curr_red, curr_green, curr_blue, curr_alpha])) # I read them as BGRA, but I like saving them as RGBA

        # read pixel data
        if len(palette) == 0:
            self.images = [Image.new('RGBA', (width,height))]
        else:
            self.images = [Image.new('RGBA', (width,height)) for _ in range(num_palettes)]
        bpp_over_4 = int(bytes_per_pixel/4) # for use with Pixel Format Specification
        for y in range(height):
            for x in range(width):
                if len(palette) == 0:
                    if bytes_per_pixel == 2:
                        tmp = color_convert_bit(two_byte_color_to_rgba(unpack('H', data[ind:ind+2])[0]), 5, 8); ind += 2
                        if tuple(tmp) == (0,0,0,0):
                            alpha = 0
                        else:
                            alpha = 255 # [255,0][tmp[3]] # just forcing no transparency for now
                        color = (tmp[0], tmp[1], tmp[2], alpha)
                    else:
                        cp = list()
                        for _ in range(4): # BGRA format
                            cp.append(unpack(BYTES_TO_FORMAT[bpp_over_4], data[ind:ind+bpp_over_4])[0]); ind += bpp_over_4
                        color = (cp[2], cp[1], cp[0], cp[3])
                    self.images[0].putpixel((x,y), color)
                else:
                    val = unpack(BYTES_TO_FORMAT[bytes_per_pixel], data[ind:ind+bytes_per_pixel])[0]; ind += bytes_per_pixel
                    for pal_num in range(num_palettes):
                        self.images[pal_num].putpixel((x,y), palette[pal_num][val])

    def get_bytes(self, bmp_mode=False, version=DEFAULT_VERSION):
        '''Return the bytes encoding this TEX file

        Args:
            ``bmp_mode`` (``bool``): Use the BMP mode of encoding the image. File sizes will be (much) larger, but transparency will always work. Try it if transparency is messed up in a game of interest

            ``version`` (``int``): 1 for Final Fantasy VII, but some Final Fantasy VIII TEX files have 2

        Returns:
            ``bytes``: The data encoding this TEX file
        '''
        out = bytearray()

        # check TEX version
        if version not in {1,2}:
            raise ValueError("Invalid TEX version: %d" % version)

        # BMP mode (larger sizes, but works for all transparency)
        if bmp_mode:
            bytes_per_pixel = 4; num_pal = 0; pal_len = 0; pal_flag = 0; bits_per_index = 0
        else:
            pal = list(set(self.images[0].getdata())); num_pal = 1; pal_len = len(pal); pal_flag = 1
            col_to_ind = {c:i for i,c in enumerate(pal)}
            if pal_len <= 256:
                bytes_per_pixel = 1; pal_index_format = 'B'
            elif pal_len <= 65536:
                bytes_per_pixel = 2; pal_index_format = 'H'
            else:
                bytes_per_pixel = 4; pal_index_format = 'I'
            bits_per_index = 8 * bytes_per_pixel
        bits_per_pixel = 8 * bytes_per_pixel
        color_key_flag = int(bmp_mode or len({a for r,g,b,a in pal}-{255}) != 0)
        bytes_per_row = bytes_per_pixel * self.get_width()

        # add header
        out += pack('I', 1)                  # version
        out += pack('I', 0)                  # unknown 1
        out += pack('I', color_key_flag)     # color key flag
        out += pack('I', 1)                  # unknown 2
        out += pack('I', 5)                  # unknown 3
        out += pack('I', 4)                  # min bits per color
        out += pack('I', 8)                  # max bits per color
        out += pack('I', 4)                  # min alpha bits
        out += pack('I', 8)                  # max alpha bits
        out += pack('I', 8)                  # min bits per pixel
        out += pack('I', 32)                 # max bits per pixel
        out += pack('I', 0)                  # unknown 4
        out += pack('I', num_pal)            # number of palettes
        out += pack('I', pal_len)            # number of colors per palette
        out += pack('I', 32)                 # bit depth
        out += pack('I', self.get_width())   # width
        out += pack('I', self.get_height())  # height
        out += pack('I', bytes_per_row)      # bytes per row (bytes per pixel * width)
        out += pack('I', 0)                  # unknown 5
        out += pack('I', pal_flag)           # palette flag
        out += pack('I', bits_per_index)     # bits per index
        out += pack('I', 0)                  # indexed to 8 bit flag
        out += pack('I', pal_len)            # palette size
        out += pack('I', pal_len)            # number of colors per palette (duplicate)
        out += pack('I', 19752016)           # runtime data 1
        out += pack('I', bits_per_pixel)     # bits per pixel
        out += pack('I', bytes_per_pixel)    # bytes per pixel

        # add pixel format
        for _ in range(4):
            out += pack('I', 8)              # num [red,green,blue,alpha] bits
        out += pack('I', 0x00FF0000)         # red bit mask
        out += pack('I', 0xFFFFFF00)         # green bit mask
        out += pack('I', 0x000000FF)         # blue bit mask
        out += pack('I', 0xFF000000)         # alpha bit mask
        out += pack('I', 16)                 # red shift
        out += pack('I', 8)                  # green shift
        out += pack('I', 0)                  # blue shift
        out += pack('I', 24)                 # alpha shift
        for _ in range(4):
            out += pack('I', 8)              # 8 - num [red,gree,blue,alpha] bits
        for _ in range(4):
            out += pack('I', 255)            # [red,gree,blue,alpha] max

        # add header 2
        out += pack('I', 0)                  # color key array flag
        out += pack('I', 0)                  # runtime data 2
        out += pack('I', 255)                # default reference alpha
        out += pack('I', 4)                  # runtime data 3
        out += pack('I', 1)                  # unknown 6
        out += pack('I', 0)                  # palette index
        out += pack('I', 34546076)           # runtime data 4
        out += pack('I', 0)                  # runtime data 5
        out += pack('I', 0)                  # unknown 7
        out += pack('I', 480)                # unknown 8
        out += pack('I', 320)                # unknown 9
        out += pack('I', 512)                # unknown 10
        if version == 2:
            out += pack('I', 0)              # unknown 11

        # image data (BMP Mode)
        if bmp_mode:
            for y in range(self.get_height()):
                for x in range(self.get_width()):
                    r,g,b,a = self.images[0].getpixel((x,y))
                    for v in [b,g,r,a]:
                        out += pack('B', v)

        # image data (Palette Mode)
        else:
            # add palette
            for r,g,b,a in pal:
                out += pack('B', b)
                out += pack('B', g)
                out += pack('B', r)
                out += pack('B', a)

            # add pixels
            for y in range(self.get_height()):
                for x in range(self.get_width()):
                    out += pack(pal_index_format, col_to_ind[self.images[0].getpixel((x,y))])
            
        return out
    
    def __iter__(self):
        '''Iterate over this image's colors'''
        for img in self.images:
            yield img

    def get_height(self):
        '''Get the image height of this TEX file

        Returns:
            ``int``: The image height of this TEX file
        '''
        return self.images[0].size[1]

    def get_width(self):
        '''Get the image width of this TEX file

        Returns:
            ``int``: The image width of this TEX file
        '''
        return self.images[0].size[0]

    def get_images(self):
        '''Get a Pillow image object from this TEX file

        Returns:
            ``list`` of ``Image``: Pillow image object(s)
        '''
        return self.images

    def show(self):
        '''Show this TEX file's image(s)'''
        for img in self.images:
            img.show()

    def num_colors(self):
        '''Return the number of unique RGBA colors in this TEX file's image

        Returns:
            ``int``: The number of unique RGBA colors in this TEX file's image
        '''
        return len(self.unique_colors())

    def unique_colors(self):
        '''Return a set containing the unique RGBA colors in this TEX file's image

        Returns:
            ``set`` of ``tuple`` of ``int``: The unique RGBA colors in this TEX file's image
        '''
        out = set()
        for img in self.images:
            out |= set(img.getdata())
        return out
