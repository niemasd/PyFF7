#!/usr/bin/env python3
'''
Functions and classes for handling LGP archives
Niema Moshiri 2019
'''
from . import NULL_BYTE,NULL_STR,read_bytes
from struct import pack,unpack

# important numbers
NUM_LOOKTAB_ENTRIES = 900 # Lookup Table has 900 entries

# size of various items in an LGP archive (in bytes)
SIZE = {
    # Header
    'HEADER_FILE-CREATOR':        12, # File Creator
    'HEADER_NUM-FILES':            4, # Number of Files in Archive

    # Table of Contents Entries
    'TOC-ENTRY_FILENAME':         20, # ToC Entry: Filename
    'TOC-ENTRY_DATA-START':        4, # ToC Entry: Data Start Position
    'TOC-ENTRY_CHECK':             1, # ToC Entry: Check Code
    'TOC-ENTRY_CONFLICT-INDEX':    2, # ToC Entry: Conflict Table Index

    # Lookup Table
    'LOOKTAB-ENTRY_INDEX':         2, # Lookup Table Entry: Index
    'LOOKTAB-ENTRY_COUNT':         2, # Lookup Table Entry: Count

    # Conflict Table
    'CONTAB_NUM-CONFLICTS':        2, # Conflict Table: Number of Filenames with Conflicts
    'CONTAB-ENTRY_FOLDER-NAME': 128, # Conflict Table Entry: Folder Name
    'CONTAB-ENTRY_TOC-INDEX':      2, # Conflict Table Entry: ToC Index

    # Data Entries
    'DATA-ENTRY_FILENAME':        20, # Data Entry: Filename
    'DATA-ENTRY_FILESIZE':         4, # Data Entry: File Size
}
SIZE['HEADER'] = sum(SIZE[k] for k in SIZE if k.startswith('HEADER_'))
SIZE['TOC-ENTRY'] = sum(SIZE[k] for k in SIZE if k.startswith('TOC-ENTRY_'))
SIZE['LOOKTAB-ENTRY'] = sum(SIZE[k] for k in SIZE if k.startswith('LOOKTAB-ENTRY_'))
SIZE['LOOKTAB'] = NUM_LOOKTAB_ENTRIES*SIZE['LOOKTAB-ENTRY']
SIZE['DATA-ENTRY_HEADER'] = sum(SIZE[k] for k in SIZE if k.startswith('DATA-ENTRY_'))

# start positions of various items in an LGP archive (in bytes)
START = {
    # Header
    'HEADER_FILE-CREATOR': 0,
    'HEADER_NUM-FILES': SIZE['HEADER_FILE-CREATOR'],

    # Table of Contents
    'TOC': SIZE['HEADER'],
}
# ToC entries (0 = start of entry)
START['TOC-ENTRY_FILENAME'] = 0
START['TOC-ENTRY_DATA-START'] = START['TOC-ENTRY_FILENAME'] + SIZE['TOC-ENTRY_FILENAME']
START['TOC-ENTRY_CHECK'] = START['TOC-ENTRY_DATA-START'] + SIZE['TOC-ENTRY_DATA-START']
START['TOC-ENTRY_CONFLICT-INDEX'] = START['TOC-ENTRY_CHECK'] + SIZE['TOC-ENTRY_CHECK']
# Data entries (0 = start of entry)
START['DATA-ENTRY_FILENAME'] = 0
START['DATA-ENTRY_FILESIZE'] = START['DATA-ENTRY_FILENAME'] + SIZE['DATA-ENTRY_FILENAME']

# other defaults
DEFAULT_CREATOR = "SQUARESOFT"

def pack_lgp(num_files, files, lgp_filename, creator=DEFAULT_CREATOR):
    '''Pack the files in ``files`` into an LGP archive ``lgp_filename``. Note that we specify the number of files just in case ``files`` streams data for memory purposes.

    Args:
        ``num_files`` (``int``): Number of files to pack

        ``files`` (iterable of (``str``,``bytes``) tuples): The data to pack in the form of (filename, data) tuples

        ``lgp_filename`` (``str``): The filename to write the packed LGP archive
    '''
    exit(1) # TODO IMPLEMENT
    with open(lgp_filename, 'wb') as outfile:
        # write header
        outfile.write((12-len(DEFAULT_CREATOR))*NULL_BYTE); f.write(DEFAULT_CREATOR.encode())
        outfile.write(pack('i', num_files))

        # write 

class LGP:
    '''LGP Archive class'''
    def __init__(self, filename):
        '''``LGP`` constructor

        Args:
            ``filename`` (``str``): The filename of the LGP archive
        '''
        self.filename = filename; self.file = open(filename, 'rb')

        # read header
        tmp = self.file.read(SIZE['HEADER'])
        self.header = {
            'file_creator': tmp[START['HEADER_FILE-CREATOR']:START['HEADER_FILE-CREATOR']+SIZE['HEADER_FILE-CREATOR']].decode().strip(NULL_STR),
            'num_files': unpack('i', tmp[START['HEADER_NUM-FILES']:START['HEADER_NUM-FILES']+SIZE['HEADER_NUM-FILES']])[0],
        }

        # read table of contents
        self.toc = list(); self.conflicting_filenames = set()
        for i in range(self.header['num_files']):
            tmp = self.file.read(SIZE['TOC-ENTRY'])
            tmp_filename = tmp[START['TOC-ENTRY_FILENAME']:START['TOC-ENTRY_FILENAME']+SIZE['TOC-ENTRY_FILENAME']].decode().strip(NULL_STR)
            tmp_data_start = unpack('i', tmp[START['TOC-ENTRY_DATA-START']:START['TOC-ENTRY_DATA-START']+SIZE['TOC-ENTRY_DATA-START']])[0]
            tmp_check = ord(tmp[START['TOC-ENTRY_CHECK']:START['TOC-ENTRY_CHECK']+SIZE['TOC-ENTRY_CHECK']])
            tmp_conflict_index = unpack('h', tmp[START['TOC-ENTRY_CONFLICT-INDEX']:START['TOC-ENTRY_CONFLICT-INDEX']+SIZE['TOC-ENTRY_CONFLICT-INDEX']])[0]
            self.toc.append({'filename':tmp_filename, 'data_start':tmp_data_start, 'check':tmp_check, 'conflict_index':tmp_conflict_index})
            if tmp_conflict_index != 0:
                self.conflicting_filenames.add(tmp_filename)

        # read lookup table (3600 bytes)
        self.looktab_bytes = self.file.read(SIZE['LOOKTAB']) # ignore this for now becuase it's not clear how to use it

        # read conflict table (2 bytes for number of conflicts, and for files with num_conflicts != 0, the actual table)
        self.num_conflicting_filenames = unpack('h', self.file.read(SIZE['CONTAB_NUM-CONFLICTS']))[0] # the first 2 bytes of the conflict table are the number of conflicts
        for i in range(self.num_conflicting_filenames): # if there were conflicts, handle them (e.g. magic.lgp); other files work properly (num_conflicting = 0)
            curr_num_conflicts = unpack('h', self.file.read(SIZE['CONTAB_NUM-CONFLICTS']))[0]
            for j in range(curr_num_conflicts):
                curr_folder_name = self.file.read(SIZE['CONTAB-ENTRY_FOLDER-NAME']).decode().strip(NULL_STR)
                curr_toc_index = unpack('h', self.file.read(SIZE['CONTAB-ENTRY_TOC-INDEX']))[0] #- 1 # it's 1-based, so subtract 1 to get indexing into self.toc
                self.toc[curr_toc_index]['filename'] = "%s/%s" % (curr_folder_name, self.toc[curr_toc_index]['filename'])

        # read file sizes
        for entry in self.toc:
            self.file.seek(entry['data_start']+SIZE['DATA-ENTRY_FILENAME'], 0); entry['filesize'] = unpack('i', self.file.read(SIZE['DATA-ENTRY_FILESIZE']))[0]

        # read terminator
        self.file.seek(self.toc[-1]['data_start']+SIZE['DATA-ENTRY_FILENAME'], 0) # move to filesize of last file
        self.file.seek(unpack('i', self.file.read(SIZE['DATA-ENTRY_FILESIZE']))[0], 1)    # move forward to end of last file's data
        self.terminator = self.file.read().decode().strip(NULL_STR)
        
    def __del__(self):
        '''``LGP`` destructor'''
        self.file.close()

    def load_bytes(self, start, size):
        '''Load the first ``size`` bytes starting with position ``start``

        Args:
            ``size`` (``int``): The start position

            ``size`` (``int``): The number of bytes to read
        '''
        self.file.seek(start, 0)
        return self.file.read(size)

    def load_files(self):
        '''Load each file contained in the LGP archive, yielding (filename, data) tuples'''
        for entry in self.toc:
            yield (entry['filename'], self.load_bytes(entry['data_start']+SIZE['DATA-ENTRY_HEADER'], entry['filesize']))
