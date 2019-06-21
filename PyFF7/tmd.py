#!/usr/bin/env python3
'''
Functions and classes for handling TMD files
Niema Moshiri 2019
'''
from struct import pack,unpack

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
}
for prefix in ['HEADER', 'OBJECT', 'VERTEX']:
    SIZE[prefix] = sum(SIZE[k] for k in SIZE if k.startswith('%s_'%prefix))

# other defaults
DEFAULT_VERSION = 65
MAX_NUM_OBJECTS = 5000

# error messages
ERROR_INVALID_TMD_FILE = "Invalid TMD file"
ERROR_INVALID_VERTEX = "Invalid vertex"

def parse_vertex(data):
    '''Parse a vertex from given data
    
    Args:
        ``data`` (``bytes``): The input data

    Returns:
        ``tuple`` of ``int``: The resulting vector as (x,y,z)
    '''
    if len(data) != SIZE['VERTEX']:
        print(len(data))
        raise ValueError(ERROR_INVALID_VERTEX)
    return

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
        num_objects = unpack('I', data[ind:ind+SIZE['HEADER_NUM-OBJECTS']])[0]; ind += SIZE['HEADER_NUM-OBJECTS']

        # read objects
        self.objects = list()
        for _ in range(num_objects):
            # initialize object
            obj = dict()
            if flags == 0:
                offset_add = ind
            else:
                offset_add = 0
            vertex_list_start = offset_add + unpack('I', data[ind:ind+SIZE['OBJECT_VERTEX-LIST-START']])[0]; ind += SIZE['OBJECT_VERTEX-LIST-START']
            num_vertices = unpack('I', data[ind:ind+SIZE['OBJECT_VERTEX-LIST-LENGTH']])[0]; ind += SIZE['OBJECT_VERTEX-LIST-LENGTH']
            normal_list_start = offset_add + unpack('I', data[ind:ind+SIZE['OBJECT_NORMAL-LIST-START']])[0]; ind += SIZE['OBJECT_NORMAL-LIST-START']
            num_normals = unpack('I', data[ind:ind+SIZE['OBJECT_NORMAL-LIST-LENGTH']])[0]; ind += SIZE['OBJECT_NORMAL-LIST-LENGTH']
            prim_list_start = offset_add + unpack('I', data[ind:ind+SIZE['OBJECT_PRIM-LIST-START']])[0]; ind += SIZE['OBJECT_PRIM-LIST-START']
            num_prims = unpack('I', data[ind:ind+SIZE['OBJECT_PRIM-LIST-LENGTH']])[0]; ind += SIZE['OBJECT_PRIM-LIST-LENGTH']
            obj['scale'] = unpack('i', data[ind:ind+SIZE['OBJECT_SCALE']])[0]; ind += SIZE['OBJECT_SCALE']
            obj['vertices'] = [parse_vertex(data[vertex_list_start+i*SIZE['VERTEX'] : vertex_list_start+(i+1)*SIZE['VERTEX']]) for i in range(num_vertices)]

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
