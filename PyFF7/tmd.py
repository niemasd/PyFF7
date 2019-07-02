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
    'PRIMITIVE_OLEN':            1, # Primitive: Olen (size of 2D drawing primitives)
    'PRIMITIVE_ILEN':            1, # Primitive: Ilen (size of packet data section)
    'PRIMITIVE_FLAGS':           1, # Primitive: Flags
    'PRIMITIVE_MODE':            1, # Primitive: Mode
}
for prefix in ['HEADER', 'OBJECT', 'VERTEX', 'NORMAL', 'PRIMITIVE']:
    SIZE[prefix] = sum(SIZE[k] for k in SIZE if k.startswith('%s_'%prefix))

# other defaults
DEFAULT_VERSION = 65
MAX_NUM_OBJECTS = 5000

# error messages
ERROR_INVALID_TMD_FILE = "Invalid TMD file"
ERROR_INVALID_VERTEX = "Invalid vertex"
ERROR_INVALID_NORMAL = "Invalid normal"
ERROR_INVALID_PRIMITIVE = "Invalid primitive"

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

def parse_primitive(data):
    '''Parse a primitive from given data

    Args:
        ``data`` (``bytes``): The input data

    Returns:
        ``tuple`` of ``int``: The resulting primitive TODO FIX
    '''
    if len(data) != SIZE['PRIMITIVE']:
        raise ValueError(ERROR_INVALID_PRIMITIVE)
    olen, ilen, flags, mode = [unpack('B', data[i*SIZE[k] : (i+1)*SIZE[k]])[0] for i,k in enumerate(['PRIMITIVE_OLEN', 'PRIMITIVE_ILEN', 'PRIMITIVE_FLAGS', 'PRIMITIVE_MODE'])]
    flag_grd = (flags & PRIMITIVE_FLAG_GRD_MASK) >> PRIMITIVE_FLAG_GRD_SHIFT
    flag_fce = (flags & PRIMITIVE_FLAG_FCE_MASK) >> PRIMITIVE_FLAG_FCE_SHIFT
    flag_lgt = (flags & PRIMITIVE_FLAG_LGT_MASK) >> PRIMITIVE_FLAG_LGT_SHIFT
    out = dict()
    out['olen'] = olen
    out['ilen'] = ilen
    out['flags'] = {'GRD':flag_grd, 'FCE':flag_fce, 'LGT':flag_lgt}
    out['mode'] = mode
    return out

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

            # load object data
            obj['vertices'] = [parse_vertex(data[vertex_list_start+i*SIZE['VERTEX'] : vertex_list_start+(i+1)*SIZE['VERTEX']]) for i in range(num_vertices)]
            obj['normals'] = [parse_normal(data[normal_list_start+i*SIZE['NORMAL'] : normal_list_start+(i+1)*SIZE['NORMAL']]) for i in range(num_normals)]
            primitive_info = [parse_primitive(data[primitive_list_start+i*SIZE['PRIMITIVE'] : primitive_list_start+(i+1)*SIZE['PRIMITIVE']]) for i in range(num_primitives)]

            # helper function to build primitive from primitive info
            def build_primitive(p):
                return None # TODO IMPLEMENT
            obj['primitives'] = [build_primitive(p) for p in primitive_info]

            # add to object list
            self.objects.append(obj)

    def get_bytes(self):
        '''Return the bytes encoding this TMD file

        Returns:
            ``bytes``: The data encoding this TMD file
        '''
        # prepare stuff
        out = bytearray()
        return out
