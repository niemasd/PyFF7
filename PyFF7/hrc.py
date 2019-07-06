#!/usr/bin/env python3
'''
Functions and classes for handling HRC files
Niema Moshiri 2019
'''

# line prefixes
START = {
    'HEADER-BLOCK_LENGTH': ':HEADER_BLOCK ', # Header Block: Length
}

# error messages
ERROR_INVALID_HRC_FILE = "Invalid HRC file"

class HRC:
    '''HRC file class'''
    def __init__(self, lines):
        '''``HRC`` constructor

        Args:
            ``lines`` (iterable of ``str``): The lines of the input HRC file
        '''
        if isinstance(lines,str): # if filename instead of lines, open filestream
            with open(lines,'r') as f:
                lines = f.readlines()
        lines = [l.strip() for l in lines if len(l.strip()) != 0] # remove empty lines
        ind = 0

        # read header
        if not lines[ind].startswith(START['HEADER-BLOCK_LENGTH']):
            raise ValueError(ERROR_INVALID_HRC_FILE)
        header_length = int(lines[ind].lstrip(START['HEADER-BLOCK_LENGTH'])); ind += 1
        self.header = list() # list of (key,value) tuples to maintain order
        for _ in range(header_length):
            curr = lines[ind]; ind += 1
            if curr[0] != ':':
                raise ValueError(ERROR_INVALID_HRC_FILE)
            k,v = curr[1:].split(' ')
            try:
                self.header.append((k,int(v)))
            except:
                self.header.append((k,v))
        header_dict = {k:v for k,v in self.header}
        if 'SKELETON' not in header_dict or 'BONES' not in header_dict or lines[ind][0] == ':':
            raise ValueError(ERROR_INVALID_HRC_FILE)

        # read bones
        self.bones = list()
        for _ in range(header_dict['BONES']):
            bone = dict()
            bone['name'] = lines[ind]; ind += 1
            bone['parent'] = lines[ind]; ind += 1
            bone['length'] = float(lines[ind]); ind += 1
            rsds = lines[ind].split(' '); ind += 1
            if int(rsds[0]) != len(rsds)-1:
                raise ValueError(ERROR_INVALID_HRC_FILE)
            bone['rsd'] = rsds[1:]
            self.bones.append(bone)
