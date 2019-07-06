#!/usr/bin/env python3
'''
Functions and classes for handling RSD files
Niema Moshiri 2019
'''

# other defaults
DEFAULT_ID = "RSD940102"

# error messages
ERROR_INVALID_RSD_FILE = "Invalid RSD file"

class RSD:
    '''RSD file class'''
    def __init__(self, lines):
        '''``RSD`` constructor

        Args:
            ``lines`` (iterable of ``str``): The lines of the input RSD file
        '''
        if isinstance(lines,str): # if filename instead of lines, open filestream
            with open(lines,'r') as f:
                lines = f.readlines()
        lines = [l.strip() for l in lines if len(l.strip()) != 0 and l[0] != '#'] # remove empty lines
        ind = 0

        # read ID
        if lines[ind][0] != '@':
            raise ValueError(ERROR_INVALID_RSD_FILE)
        self.ID = lines[ind][1:]; ind += 1

        # read other attributes
        self.attr = {'TEX':list()}; num_tex = None
        while ind < len(lines):
            if lines[ind].count('=') != 1:
                raise ValueError(ERROR_INVALID_RSD_FILE)
            k,v = lines[ind].split('='); ind += 1
            if k.startswith('TEX['):
                if int(k.split('[')[1].split(']')[0]) != len(self.attr['TEX']):
                    raise ValueError(ERROR_INVALID_RSD_FILE)
                self.attr['TEX'].append(v)
            elif k == 'NTEX':
                num_tex = int(v)
            else:
                self.attr[k] = v
        if num_tex != len(self.attr['TEX']):
            raise ValueError(ERROR_INVALID_RSD_FILE)
