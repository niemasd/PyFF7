#!/usr/bin/env python3
'''
Functions and classes for handling TMD files
Niema Moshiri 2019
'''
from struct import pack,unpack

# constants
PRIMITIVE_FLAG_GRD_MASK = 0b00000100
PRIMITIVE_FLAG_FCE_MASK = 0b00000010
PRIMITIVE_FLAG_LGT_MASK = 0b00000001
PRIMITIVE_FLAG_GRD_SHIFT = 2
PRIMITIVE_FLAG_FCE_SHIFT = 1
PRIMITIVE_FLAG_LGT_SHIFT = 0
PRIMITIVE_MODE_CODE_MASK   = 0b11100000
PRIMITIVE_MODE_OPTION_MASK = 0b00011111
PRIMITIVE_MODE_CODE_SHIFT = 5
PRIMITIVE_MODE_OPTION_SHIFT = 0
VALID_FLAG_GRD = {0,1}
VALID_FLAG_FCE = {0,1}
VALID_FLAG_LGT = {0,1}
VALID_MODE_CODE = {0,1,2,3}

# size of various items in an TMD file (in bytes)
SIZE = {
    # Header
    'HEADER_VERSION':            4, # Header: Version
    'HEADER_FLAGS':              4, # Header: Flags
    'HEADER_NUM-OBJECTS':        4, # Header: Number of Objects

    # Object
    'OBJECT_VERTEX-LIST-START':  4, # Object: Vertex List Start Offset
    'OBJECT_VERTEX-LIST-LENGTH': 4, # Object: Number of Vertices
    'OBJECT_NORMAL-LIST-START':  4, # Object: Normal List Start Offset
    'OBJECT_NORMAL-LIST-LENGTH': 4, # Object: Number of Normals
    'OBJECT_PRIM-LIST-START':    4, # Object: Primitive List Start Offset
    'OBJECT_PRIM-LIST-LENGTH':   4, # Object: Number of Primitives
    'OBJECT_SCALE':              4, # Object: Scale (ignored)

    # Vertex
    'VERTEX_X':                  2, # Vertex: X Dimension
    'VERTEX_Y':                  2, # Vertex: Y Dimension
    'VERTEX_Z':                  2, # Vertex: Z Dimension
    'VERTEX_PAD':                2, # Vertex: Padding (unused)

    # Normal
    'NORMAL_X':                  2, # Normal: X Dimension
    'NORMAL_Y':                  2, # Normal: Y Dimension
    'NORMAL_Z':                  2, # Normal: Z Dimension
    'NORMAL_PAD':                2, # Normal: Padding (unused)

    # Primitive
    'PRIMITIVE-HEADER_OLEN':     1, # Primitive Header: Olen (size of 2D drawing primitives)
    'PRIMITIVE-HEADER_ILEN':     1, # Primitive Header: Ilen (size of packet data section)
    'PRIMITIVE-HEADER_FLAGS':    1, # Primitive Header: Flags
    'PRIMITIVE-HEADER_MODE':     1, # Primitive Header: Mode
    'PRIMITIVE_CBA':             2, # Primitive: CBA (position where CLUT is stored in VRAM)
    'PRIMITIVE_COLOR':           1, # Primitive: Color Byte
    'PRIMITIVE_MODE2':           1, # Primitive: Mode Repeat (unused)
    'PRIMITIVE_NORMAL':          1, # Primitive: Normal
    'PRIMITIVE_PAD-BYTE':        1, # Primitive: Pad Byte (unused)
    'PRIMITIVE_TSB':             2, # Primitive: TSB (info about texture/sprite pattern)
    'PRIMITIVE_UV':              1, # Primitive: U# and V#
    'PRIMITIVE_VERTEX':          1, # Primitive: Vertex
}
for prefix in ['HEADER', 'OBJECT', 'VERTEX', 'NORMAL', 'PRIMITIVE-HEADER']:
    SIZE[prefix] = sum(SIZE[k] for k in SIZE if k.startswith('%s_'%prefix))

# other defaults
DEFAULT_VERSION = 65
MAX_NUM_OBJECTS = 5000

# error messages
ERROR_INVALID_TMD_FILE = "Invalid TMD file"
ERROR_INVALID_VERTEX = "Invalid vertex"
ERROR_INVALID_NORMAL = "Invalid normal"
ERROR_INVALID_PRIMITIVE = "Invalid primitive"
ERROR_INVALID_PRIMITIVE_FLAGS = "Invalid primitive flags"
ERROR_INVALID_PRIMITIVE_MODE = "Invalid primitive mode"

def parse_vertex(data):
    '''Parse a vertex from given data
    
    Args:
        ``data`` (``bytes``): The input data

    Returns:
        ``tuple`` of ``int``: The resulting vector as (x,y,z)
    '''
    if len(data) != SIZE['VERTEX']:
        raise ValueError(ERROR_INVALID_VERTEX)
    return [unpack('h', data[i*SIZE[k] : (i+1)*SIZE[k]])[0] for i,k in enumerate(['VERTEX_X', 'VERTEX_Y', 'VERTEX_Z'])]

def parse_normal(data):
    '''Parse a normal from given data

    Args:
        ``data`` (``bytes``): The input data

    Returns:
        ``tuple`` of ``int``: The resulting normal as (x,y,z)
    '''
    if len(data) != SIZE['NORMAL']:
        raise ValueError(ERROR_INVALID_NORMAL)
    return [unpack('h', data[i*SIZE[k] : (i+1)*SIZE[k]])[0] for i,k in enumerate(['NORMAL_X', 'NORMAL_Y', 'NORMAL_Z'])]

def unpack_prim_flags(flags):
    '''Parse the GRD, FCE, and LGT flags from a primitive's "flags" byte (00000GFL)

    Args:
        ``flags`` (``int``): The input primitive "flags" byte

    Returns:
        ``int``: The GRD flag

        ``int``: The FCE flag

        ``int``: The LGT flag
    '''
    grd = (flags & PRIMITIVE_FLAG_GRD_MASK) >> PRIMITIVE_FLAG_GRD_SHIFT
    fce = (flags & PRIMITIVE_FLAG_FCE_MASK) >> PRIMITIVE_FLAG_FCE_SHIFT
    lgt = (flags & PRIMITIVE_FLAG_LGT_MASK) >> PRIMITIVE_FLAG_LGT_SHIFT
    if grd not in VALID_FLAG_GRD or fce not in VALID_FLAG_FCE or lgt not in VALID_FLAG_LGT:
        raise ValueError(ERROR_INVALID_PRIMITIVE_FLAGS)
    return grd,fce,lgt

def unpack_prim_mode(mode):
    '''Parse the Code and Option values from a primitive's "mode" byte (CCCOOOOO)

    Args:
        ``mode`` (``int``): The input primitive "mode" byte

    Returns:
        ``int``: The Code value

        ``int``: The Option value
    '''
    code = (mode & PRIMITIVE_MODE_CODE_MASK) >> PRIMITIVE_MODE_CODE_SHIFT
    option = (mode & PRIMITIVE_MODE_OPTION_MASK) >> PRIMITIVE_MODE_OPTION_SHIFT
    if code not in VALID_MODE_CODE: # TODO CHECK OPTION?
        raise ValueError(ERROR_INVALID_PRIMITIVE_MODE)
    return code,option

def parse_prim_cba(cba):
    raise NotImplementedError

def parse_prim_tsb(tsb):
    raise NotImplementedError

class TMD:
    '''TMD file class'''
    def __init__(self, data):
        '''``TMD`` constructor

        Args:
            ``data`` (``bytes``): The input TMD file
        '''
        if isinstance(data,str): # if filename instead of bytes, read bytes
            with open(data,'rb') as f:
                data = f.read()
        ind = 0

        # read header
        self.version = unpack('I', data[ind:ind+SIZE['HEADER_VERSION']])[0]; ind += SIZE['HEADER_VERSION']
        if self.version != DEFAULT_VERSION:
            raise TypeError(ERROR_INVALID_TMD_FILE)
        flags = unpack('I', data[ind:ind+SIZE['HEADER_FLAGS']])[0]; ind += SIZE['HEADER_FLAGS']
        if flags != 0 and self.flags != 1:
            raise TypeError(ERROR_INVALID_TMD_FILE)
        if flags == 0:
            offset_add = SIZE['HEADER']
        else:
            offset_add = 0
        num_objects = unpack('I', data[ind:ind+SIZE['HEADER_NUM-OBJECTS']])[0]; ind += SIZE['HEADER_NUM-OBJECTS']

        # read objects
        self.objects = list()
        for _ in range(num_objects):
            # initialize object
            obj = dict()
            vertex_list_start = offset_add + unpack('I', data[ind:ind+SIZE['OBJECT_VERTEX-LIST-START']])[0]; ind += SIZE['OBJECT_VERTEX-LIST-START']
            num_vertices = unpack('I', data[ind:ind+SIZE['OBJECT_VERTEX-LIST-LENGTH']])[0]; ind += SIZE['OBJECT_VERTEX-LIST-LENGTH']
            normal_list_start = offset_add + unpack('I', data[ind:ind+SIZE['OBJECT_NORMAL-LIST-START']])[0]; ind += SIZE['OBJECT_NORMAL-LIST-START']
            num_normals = unpack('I', data[ind:ind+SIZE['OBJECT_NORMAL-LIST-LENGTH']])[0]; ind += SIZE['OBJECT_NORMAL-LIST-LENGTH']
            primitive_list_start = offset_add + unpack('I', data[ind:ind+SIZE['OBJECT_PRIM-LIST-START']])[0]; ind += SIZE['OBJECT_PRIM-LIST-START']
            num_primitives = unpack('I', data[ind:ind+SIZE['OBJECT_PRIM-LIST-LENGTH']])[0]; ind += SIZE['OBJECT_PRIM-LIST-LENGTH']
            obj['scale'] = unpack('i', data[ind:ind+SIZE['OBJECT_SCALE']])[0]; ind += SIZE['OBJECT_SCALE']

            # load vertices and normals
            obj['vertices'] = [parse_vertex(data[vertex_list_start+i*SIZE['VERTEX'] : vertex_list_start+(i+1)*SIZE['VERTEX']]) for i in range(num_vertices)]
            obj['normals'] = [parse_normal(data[normal_list_start+i*SIZE['NORMAL'] : normal_list_start+(i+1)*SIZE['NORMAL']]) for i in range(num_normals)]

            # load primitives
            obj['primitives'] = list()
            for i in range(num_primitives):
                # load primitive info
                p_ind = primitive_list_start + i*SIZE['PRIMITIVE-HEADER']; prim = {'flags':dict(), 'mode':dict()}
                prim['olen'] = unpack('B', data[p_ind:p_ind+SIZE['PRIMITIVE-HEADER_OLEN']])[0]; p_ind += SIZE['PRIMITIVE-HEADER_OLEN']
                prim['ilen'] = unpack('B', data[p_ind:p_ind+SIZE['PRIMITIVE-HEADER_ILEN']])[0]; p_ind += SIZE['PRIMITIVE-HEADER_ILEN']
                flags = unpack('B', data[p_ind:p_ind+SIZE['PRIMITIVE-HEADER_FLAGS']])[0]; p_ind += SIZE['PRIMITIVE-HEADER_FLAGS']
                prim['flags']['GRD'], prim['flags']['FCE'], prim['flags']['LGT'] = unpack_prim_flags(flags)
                prim['mode'] = unpack('B', data[p_ind:p_ind+SIZE['PRIMITIVE-HEADER_MODE']])[0]; p_ind += SIZE['PRIMITIVE-HEADER_MODE']

                # 3-Vertex, Flat, No-Texture (Solid), Light Source Calculation
                if prim['mode'] == 0x20 and prim['flags']['GRD'] == 0 and prim['flags']['LGT'] == 0:
                    r = unpack('B', data[p_ind:p_ind+SIZE['PRIMITIVE_COLOR']])[0]; p_ind += SIZE['PRIMITIVE_COLOR']
                    g = unpack('B', data[p_ind:p_ind+SIZE['PRIMITIVE_COLOR']])[0]; p_ind += SIZE['PRIMITIVE_COLOR']
                    b = unpack('B', data[p_ind:p_ind+SIZE['PRIMITIVE_COLOR']])[0]; p_ind += SIZE['PRIMITIVE_COLOR']
                    mode2 = unpack('B', data[p_ind:p_ind+SIZE['PRIMITIVE_MODE2']])[0]; p_ind += SIZE['PRIMITIVE_MODE2']
                    if mode2 != mode:
                        raise ValueError(ERROR_INVALID_PRIMITIVE)
                    norm = unpack('h', data[p_ind:p_ind+SIZE['PRIMITIVE_NORMAL']])[0]; p_ind += SIZE['PRIMITIVE_NORMAL']
                    vert0 = unpack('h', data[p_ind:p_ind+SIZE['PRIMITIVE_VERTEX']])[0]; p_ind += SIZE['PRIMITIVE_VERTEX']
                    vert1 = unpack('h', data[p_ind:p_ind+SIZE['PRIMITIVE_VERTEX']])[0]; p_ind += SIZE['PRIMITIVE_VERTEX']
                    vert2 = unpack('h', data[p_ind:p_ind+SIZE['PRIMITIVE_VERTEX']])[0]; p_ind += SIZE['PRIMITIVE_VERTEX']
                    prim['data'] = {'colors':[[r,g,b]], 'normals':[norm], 'vertices':[vert0,vert1,vert2]}

                # 3-Vertex, Flat, No-Texture (Gradation), Light Source Calculation
                elif prim['mode'] == 0x20 and prim['flags']['GRD'] == 1 and prim['flags']['LGT'] == 0:
                    r0 = unpack('B', data[p_ind:p_ind+SIZE['PRIMITIVE_COLOR']])[0]; p_ind += SIZE['PRIMITIVE_COLOR']
                    g0 = unpack('B', data[p_ind:p_ind+SIZE['PRIMITIVE_COLOR']])[0]; p_ind += SIZE['PRIMITIVE_COLOR']
                    b0 = unpack('B', data[p_ind:p_ind+SIZE['PRIMITIVE_COLOR']])[0]; p_ind += SIZE['PRIMITIVE_COLOR']
                    mode2 = unpack('B', data[p_ind:p_ind+SIZE['PRIMITIVE_MODE2']])[0]; p_ind += SIZE['PRIMITIVE_MODE2']
                    if mode2 != mode:
                        raise ValueError(ERROR_INVALID_PRIMITIVE)
                    r1 = unpack('B', data[p_ind:p_ind+SIZE['PRIMITIVE_COLOR']])[0]; p_ind += SIZE['PRIMITIVE_COLOR']
                    g1 = unpack('B', data[p_ind:p_ind+SIZE['PRIMITIVE_COLOR']])[0]; p_ind += SIZE['PRIMITIVE_COLOR']
                    b1 = unpack('B', data[p_ind:p_ind+SIZE['PRIMITIVE_COLOR']])[0]; p_ind += SIZE['PRIMITIVE_COLOR']
                    p_ind += SIZE['PRIMITIVE_PAD-BYTE'] # 1 padding byte (unused)
                    r2 = unpack('B', data[p_ind:p_ind+SIZE['PRIMITIVE_COLOR']])[0]; p_ind += SIZE['PRIMITIVE_COLOR']
                    g2 = unpack('B', data[p_ind:p_ind+SIZE['PRIMITIVE_COLOR']])[0]; p_ind += SIZE['PRIMITIVE_COLOR']
                    b2 = unpack('B', data[p_ind:p_ind+SIZE['PRIMITIVE_COLOR']])[0]; p_ind += SIZE['PRIMITIVE_COLOR']
                    p_ind += SIZE['PRIMITIVE_PAD-BYTE'] # 1 padding byte (unused)
                    norm = unpack('h', data[p_ind:p_ind+SIZE['PRIMITIVE_NORMAL']])[0]; p_ind += SIZE['PRIMITIVE_NORMAL']
                    vert0 = unpack('h', data[p_ind:p_ind+SIZE['PRIMITIVE_VERTEX']])[0]; p_ind += SIZE['PRIMITIVE_VERTEX']
                    vert1 = unpack('h', data[p_ind:p_ind+SIZE['PRIMITIVE_VERTEX']])[0]; p_ind += SIZE['PRIMITIVE_VERTEX']
                    vert2 = unpack('h', data[p_ind:p_ind+SIZE['PRIMITIVE_VERTEX']])[0]; p_ind += SIZE['PRIMITIVE_VERTEX']
                    prim['data'] = {'colors':[[r0,g0,b0], [r1,g1,b1], [r2,g2,b2]], 'normals':[norm], 'vertices':[vert0,vert1,vert2]}
                    
                # 3-Vertex, Flat, Texture, Light Source Calculation
                elif prim['mode'] == 0x24 and prim['flags']['LGT'] == 0:
                    u0 = unpack('B', data[p_ind:p_ind+SIZE['PRIMITIVE_UV']])[0]; p_ind += SIZE['PRIMITIVE_UV']
                    v0 = unpack('B', data[p_ind:p_ind+SIZE['PRIMITIVE_UV']])[0]; p_ind += SIZE['PRIMITIVE_UV']
                    cba = data[p_ind:p_ind+SIZE['PRIMITIVE_CBA']]; p_ind += SIZE['PRIMITIVE_CBA']
                    u1 = unpack('B', data[p_ind:p_ind+SIZE['PRIMITIVE_UV']])[0]; p_ind += SIZE['PRIMITIVE_UV']
                    v1 = unpack('B', data[p_ind:p_ind+SIZE['PRIMITIVE_UV']])[0]; p_ind += SIZE['PRIMITIVE_UV']
                    tsb = data[p_ind:p_ind+SIZE['PRIMITIVE_TSB']]; p_ind += SIZE['PRIMITIVE_TSB']
                    u2 = unpack('B', data[p_ind:p_ind+SIZE['PRIMITIVE_UV']])[0]; p_ind += SIZE['PRIMITIVE_UV']
                    v2 = unpack('B', data[p_ind:p_ind+SIZE['PRIMITIVE_UV']])[0]; p_ind += SIZE['PRIMITIVE_UV']
                    p_ind += 2*SIZE['PRIMITIVE_PAD-BYTE'] # 2 padding bytes (unused)
                    norm = unpack('h', data[p_ind:p_ind+SIZE['PRIMITIVE_NORMAL']])[0]; p_ind += SIZE['PRIMITIVE_NORMAL']
                    vert0 = unpack('h', data[p_ind:p_ind+SIZE['PRIMITIVE_VERTEX']])[0]; p_ind += SIZE['PRIMITIVE_VERTEX']
                    vert1 = unpack('h', data[p_ind:p_ind+SIZE['PRIMITIVE_VERTEX']])[0]; p_ind += SIZE['PRIMITIVE_VERTEX']
                    vert2 = unpack('h', data[p_ind:p_ind+SIZE['PRIMITIVE_VERTEX']])[0]; p_ind += SIZE['PRIMITIVE_VERTEX']
                    prim['data'] = {'U':[u0,u1,u2], 'V':[v0,v1,v2], 'CBA':parse_prim_cba(cba), 'TSB':parse_prim_tsb(tsb), 'normals':[norm], 'vertices':[vert0,vert1,vert2]}

                # 4-vertex, Flat, No-Texture (Solid), Light Source Calculation
                elif prim['mode'] == 0x28 and prim['flags']['GRD'] == 0 and prim['flags']['LGT'] == 0:
                    r = unpack('B', data[p_ind:p_ind+SIZE['PRIMITIVE_COLOR']])[0]; p_ind += SIZE['PRIMITIVE_COLOR']
                    g = unpack('B', data[p_ind:p_ind+SIZE['PRIMITIVE_COLOR']])[0]; p_ind += SIZE['PRIMITIVE_COLOR']
                    b = unpack('B', data[p_ind:p_ind+SIZE['PRIMITIVE_COLOR']])[0]; p_ind += SIZE['PRIMITIVE_COLOR']
                    mode2 = unpack('B', data[p_ind:p_ind+SIZE['PRIMITIVE_MODE2']])[0]; p_ind += SIZE['PRIMITIVE_MODE2']
                    if mode2 != mode:
                        raise ValueError(ERROR_INVALID_PRIMITIVE)
                    norm = unpack('h', data[p_ind:p_ind+SIZE['PRIMITIVE_NORMAL']])[0]; p_ind += SIZE['PRIMITIVE_NORMAL']
                    vert0 = unpack('h', data[p_ind:p_ind+SIZE['PRIMITIVE_VERTEX']])[0]; p_ind += SIZE['PRIMITIVE_VERTEX']
                    vert1 = unpack('h', data[p_ind:p_ind+SIZE['PRIMITIVE_VERTEX']])[0]; p_ind += SIZE['PRIMITIVE_VERTEX']
                    vert2 = unpack('h', data[p_ind:p_ind+SIZE['PRIMITIVE_VERTEX']])[0]; p_ind += SIZE['PRIMITIVE_VERTEX']
                    vert3 = unpack('h', data[p_ind:p_ind+SIZE['PRIMITIVE_VERTEX']])[0]; p_ind += SIZE['PRIMITIVE_VERTEX']
                    prim['data'] = {'colors':[[r,g,b]], 'normals':[norm], 'vertices':[vert0,vert1,vert2,vert3]}

                # 3-Vertex, Gouraud, No-Texture (Solid), Light Source Calculation
                elif prim['mode'] == 0x30 and prim['flags']['GRD'] == 0 and prim['flags']['LGT'] == 0:
                    r = unpack('B', data[p_ind:p_ind+SIZE['PRIMITIVE_COLOR']])[0]; p_ind += SIZE['PRIMITIVE_COLOR']
                    g = unpack('B', data[p_ind:p_ind+SIZE['PRIMITIVE_COLOR']])[0]; p_ind += SIZE['PRIMITIVE_COLOR']
                    b = unpack('B', data[p_ind:p_ind+SIZE['PRIMITIVE_COLOR']])[0]; p_ind += SIZE['PRIMITIVE_COLOR']
                    mode2 = unpack('B', data[p_ind:p_ind+SIZE['PRIMITIVE_MODE2']])[0]; p_ind += SIZE['PRIMITIVE_MODE2']
                    if mode2 != mode:
                        raise ValueError(ERROR_INVALID_PRIMITIVE)
                    norm0 = unpack('h', data[p_ind:p_ind+SIZE['PRIMITIVE_NORMAL']])[0]; p_ind += SIZE['PRIMITIVE_NORMAL']
                    vert0 = unpack('h', data[p_ind:p_ind+SIZE['PRIMITIVE_VERTEX']])[0]; p_ind += SIZE['PRIMITIVE_VERTEX']
                    norm1 = unpack('h', data[p_ind:p_ind+SIZE['PRIMITIVE_NORMAL']])[0]; p_ind += SIZE['PRIMITIVE_NORMAL']
                    vert1 = unpack('h', data[p_ind:p_ind+SIZE['PRIMITIVE_VERTEX']])[0]; p_ind += SIZE['PRIMITIVE_VERTEX']
                    norm2 = unpack('h', data[p_ind:p_ind+SIZE['PRIMITIVE_NORMAL']])[0]; p_ind += SIZE['PRIMITIVE_NORMAL']
                    vert2 = unpack('h', data[p_ind:p_ind+SIZE['PRIMITIVE_VERTEX']])[0]; p_ind += SIZE['PRIMITIVE_VERTEX']
                    prim['data'] = {'colors':[[r,g,b]], 'normals':[norm0,norm1,norm2], 'vertices':[vert0,vert1,vert2]}

                # 3-Vertex, Gouraud, No-Texture (Gradation), Light Source Calculation
                elif prim['mode'] == 0x30 and prim['flags']['GRD'] == 1 and prim['flags']['LGT'] == 0:
                    r0 = unpack('B', data[p_ind:p_ind+SIZE['PRIMITIVE_COLOR']])[0]; p_ind += SIZE['PRIMITIVE_COLOR']
                    g0 = unpack('B', data[p_ind:p_ind+SIZE['PRIMITIVE_COLOR']])[0]; p_ind += SIZE['PRIMITIVE_COLOR']
                    b0 = unpack('B', data[p_ind:p_ind+SIZE['PRIMITIVE_COLOR']])[0]; p_ind += SIZE['PRIMITIVE_COLOR']
                    mode2 = unpack('B', data[p_ind:p_ind+SIZE['PRIMITIVE_MODE2']])[0]; p_ind += SIZE['PRIMITIVE_MODE2']
                    if mode2 != mode:
                        raise ValueError(ERROR_INVALID_PRIMITIVE)
                    r1 = unpack('B', data[p_ind:p_ind+SIZE['PRIMITIVE_COLOR']])[0]; p_ind += SIZE['PRIMITIVE_COLOR']
                    g1 = unpack('B', data[p_ind:p_ind+SIZE['PRIMITIVE_COLOR']])[0]; p_ind += SIZE['PRIMITIVE_COLOR']
                    b1 = unpack('B', data[p_ind:p_ind+SIZE['PRIMITIVE_COLOR']])[0]; p_ind += SIZE['PRIMITIVE_COLOR']
                    p_ind += SIZE['PRIMITIVE_PAD-BYTE'] # 1 padding byte (unused)
                    r2 = unpack('B', data[p_ind:p_ind+SIZE['PRIMITIVE_COLOR']])[0]; p_ind += SIZE['PRIMITIVE_COLOR']
                    g2 = unpack('B', data[p_ind:p_ind+SIZE['PRIMITIVE_COLOR']])[0]; p_ind += SIZE['PRIMITIVE_COLOR']
                    b2 = unpack('B', data[p_ind:p_ind+SIZE['PRIMITIVE_COLOR']])[0]; p_ind += SIZE['PRIMITIVE_COLOR']
                    p_ind += SIZE['PRIMITIVE_PAD-BYTE'] # 1 padding byte (unused)
                    norm0 = unpack('h', data[p_ind:p_ind+SIZE['PRIMITIVE_NORMAL']])[0]; p_ind += SIZE['PRIMITIVE_NORMAL']
                    vert0 = unpack('h', data[p_ind:p_ind+SIZE['PRIMITIVE_VERTEX']])[0]; p_ind += SIZE['PRIMITIVE_VERTEX']
                    norm1 = unpack('h', data[p_ind:p_ind+SIZE['PRIMITIVE_NORMAL']])[0]; p_ind += SIZE['PRIMITIVE_NORMAL']
                    vert1 = unpack('h', data[p_ind:p_ind+SIZE['PRIMITIVE_VERTEX']])[0]; p_ind += SIZE['PRIMITIVE_VERTEX']
                    norm2 = unpack('h', data[p_ind:p_ind+SIZE['PRIMITIVE_NORMAL']])[0]; p_ind += SIZE['PRIMITIVE_NORMAL']
                    vert2 = unpack('h', data[p_ind:p_ind+SIZE['PRIMITIVE_VERTEX']])[0]; p_ind += SIZE['PRIMITIVE_VERTEX']
                    prim['data'] = {'colors':[[r0,g0,b0], [r1,g1,b1], [r2,g2,b2]], 'normals':[norm0,norm1,norm2], 'vertices':[vert0,vert1,vert2]}

                # 3-Vertex, Gouraud, Texture, Light Source Calculation
                elif prim['mode'] == 0x34 and prim['flags']['LGT'] == 0:
                    u0 = unpack('B', data[p_ind:p_ind+SIZE['PRIMITIVE_UV']])[0]; p_ind += SIZE['PRIMITIVE_UV']
                    v0 = unpack('B', data[p_ind:p_ind+SIZE['PRIMITIVE_UV']])[0]; p_ind += SIZE['PRIMITIVE_UV']
                    cba = data[p_ind:p_ind+SIZE['PRIMITIVE_CBA']]; p_ind += SIZE['PRIMITIVE_CBA']
                    u1 = unpack('B', data[p_ind:p_ind+SIZE['PRIMITIVE_UV']])[0]; p_ind += SIZE['PRIMITIVE_UV']
                    v1 = unpack('B', data[p_ind:p_ind+SIZE['PRIMITIVE_UV']])[0]; p_ind += SIZE['PRIMITIVE_UV']
                    tsb = data[p_ind:p_ind+SIZE['PRIMITIVE_TSB']]; p_ind += SIZE['PRIMITIVE_TSB']
                    u2 = unpack('B', data[p_ind:p_ind+SIZE['PRIMITIVE_UV']])[0]; p_ind += SIZE['PRIMITIVE_UV']
                    v2 = unpack('B', data[p_ind:p_ind+SIZE['PRIMITIVE_UV']])[0]; p_ind += SIZE['PRIMITIVE_UV']
                    p_ind += 2*SIZE['PRIMITIVE_PAD-BYTE'] # 2 padding bytes (unused)
                    norm0 = unpack('h', data[p_ind:p_ind+SIZE['PRIMITIVE_NORMAL']])[0]; p_ind += SIZE['PRIMITIVE_NORMAL']
                    vert0 = unpack('h', data[p_ind:p_ind+SIZE['PRIMITIVE_VERTEX']])[0]; p_ind += SIZE['PRIMITIVE_VERTEX']
                    norm1 = unpack('h', data[p_ind:p_ind+SIZE['PRIMITIVE_NORMAL']])[0]; p_ind += SIZE['PRIMITIVE_NORMAL']
                    vert1 = unpack('h', data[p_ind:p_ind+SIZE['PRIMITIVE_VERTEX']])[0]; p_ind += SIZE['PRIMITIVE_VERTEX']
                    norm2 = unpack('h', data[p_ind:p_ind+SIZE['PRIMITIVE_NORMAL']])[0]; p_ind += SIZE['PRIMITIVE_NORMAL']
                    vert2 = unpack('h', data[p_ind:p_ind+SIZE['PRIMITIVE_VERTEX']])[0]; p_ind += SIZE['PRIMITIVE_VERTEX']
                    prim['data'] = {'U':[u0,u1,u2], 'V':[v0,v1,v2], 'CBA':parse_prim_cba(cba), 'TSB':parse_prim_tsb(tsb), 'normals':[norm0,norm1,norm2], 'vertices':[vert0,vert1,vert2]}

                # Invalid Mode
                else:
                    raise ValueError("Unknown TMD Primitive Mode: 0x%02x" % prim['mode'])
                obj['primitives'].append(prim)

            # add to object list
            self.objects.append(obj)
        exit()

    def get_bytes(self):
        '''Return the bytes encoding this TMD file

        Returns:
            ``bytes``: The data encoding this TMD file
        '''
        # prepare stuff
        out = bytearray()
        return out
