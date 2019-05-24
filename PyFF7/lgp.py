#!/usr/bin/env python3
'''
Functions and classes for handling LGP archives
Niema Moshiri 2019
'''
from . import MAX_UNSIGNED_INT,MAX_UNSIGNED_SHORT,NULL_BYTE,NULL_STR
from os.path import getsize
from struct import pack,unpack

# constants
LOOKUP_VALUE_MAX = 30
NUM_LOOKTAB_ENTRIES = LOOKUP_VALUE_MAX*LOOKUP_VALUE_MAX # Lookup Table has 900 entries
MAX_CONFLICTS = 4096

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
    'CONTAB-ENTRY_NUM-LOCATIONS':  2, # Conflict Table Entry: Number of Folder Locations
    'CONTAB-ENTRY_FOLDER-NAME':  128, # Conflict Table Entry: Folder Name
    'CONTAB-ENTRY_TOC-INDEX':      2, # Conflict Table Entry: ToC Index

    # Data Entries
    'DATA-ENTRY_FILENAME':        20, # Data Entry: Filename
    'DATA-ENTRY_FILESIZE':         4, # Data Entry: File Size

    # Other
    'TERMINATOR':                 14, # File Terminator (default: "FINAL FANTASY7")
}
SIZE['HEADER'] = sum(SIZE[k] for k in SIZE if k.startswith('HEADER_')) # 16 bytes
SIZE['TOC-ENTRY'] = sum(SIZE[k] for k in SIZE if k.startswith('TOC-ENTRY_')) # 27 bytes
SIZE['LOOKTAB-ENTRY'] = sum(SIZE[k] for k in SIZE if k.startswith('LOOKTAB-ENTRY_')) # 4 bytes
SIZE['LOOKTAB'] = NUM_LOOKTAB_ENTRIES*SIZE['LOOKTAB-ENTRY'] # 3600 bytes
SIZE['DATA-ENTRY_HEADER'] = sum(SIZE[k] for k in SIZE if k.startswith('DATA-ENTRY_')) # 24 bytes

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
DEFAULT_TERMINATOR = "FINAL FANTASY7"

# error messages
ERROR_CHAR_INPUT = "Input must be a single character"
ERROR_FILENAME_START_PERIOD = "Filename cannot begin with '.'"
ERROR_INVALID_TOC_ENTRY = "Invalid Table of Contents entry"
ERROR_LOOKUP_TOC_MISMATCH = "Lookup Table and Table of Contents do not match"
ERROR_NOT_STR = "Input is not a string"
ERROR_TERMINATOR_SIZE = "Terminator is the wrong size"

def char_to_lookup_value(c):
    '''Convert a character ``c`` to a value for the Lookup Table index (this is done to the first and second characters of a filename)

    Args:
        ``c`` (``str``): The character to convert

    Returns:
        ``int``: The converted value for the Lookup Table index
    '''
    if not isinstance(c,str) or len(c) != 1: # must be a single character
        raise ValueError(ERROR_CHAR_INPUT)
    if c == '.':
        return -1 # this is actually correct: period returns -1
    elif c == '_':
        return 10 # 'k' - 'a'
    elif c == '-':
        return 11 # 'l' - 'a'
    elif str.isdigit(c):
        return ord(c) - ord('0')
    elif str.isalpha(c):
        return ord(c.lower()) - ord('a')
    else:
       raise ValueError("Invalid character: %s" % c)

def filename_to_lookup_index(filename):
    '''Convert ``filename`` to a Lookup Table index

    I got the algorithm from here: https://github.com/Vgr255/LGP/blob/467c31e6c600ac33b701cc7f7baa7242b7b1ec7e/legacy/lgp.c#L111

    Args:
        ``filename`` (``str``): The filename to convert to a Lookup Table index

    Returns:
        ``int``: The converted Lookup Table index
    '''
    filename = filename.split('/')[-1]
    if not isinstance(filename,str):
        raise TypeError(ERROR_NOT_STR)
    if filename[0] == '.':
        raise ValueError(ERROR_FILENAME_START_PERIOD)
    lv1 = char_to_lookup_value(filename[0])
    lv2 = char_to_lookup_value(filename[1])
    return lv1*LOOKUP_VALUE_MAX + lv2 + 1

def toc_to_lookup_table(toc):
    '''Convert a Table of Contents ``toc`` to a Lookup Table

    Args:
        ``toc`` (iterable of ``dict``): The Table of Contents to convert

    Returns:
        ``list`` of ``tuple``: The Lookup Table as a list of 900 (toc_index, file_count) tuples
    '''
    file_count = [0]*NUM_LOOKTAB_ENTRIES; toc_index = [0]*NUM_LOOKTAB_ENTRIES
    for i,entry in enumerate(toc):
        if 'filename' not in entry:
            raise TypeError(ERROR_INVALID_TOC_ENTRY)
        lookup_index = filename_to_lookup_index(entry['filename'].split('/')[-1])
        file_count[lookup_index] += 1
        if toc_index[lookup_index] == 0:
            toc_index[lookup_index] = i+1
    return [(toc_index[i], file_count[i]) for i in range(NUM_LOOKTAB_ENTRIES)]


def pack_lgp(files, lgp_filename, creator=DEFAULT_CREATOR, terminator=DEFAULT_TERMINATOR):
    '''Pack the files in ``files`` into an LGP archive ``lgp_filename``. Note that we specify the number of files just in case ``files`` streams data for memory purposes.

    Args:
        ``files`` (iterable of tuple of ``str``): The filenames to pack as (full path in archive, full path on disk) tuples

        ``lgp_filename`` (``str``): The filename to write the packed LGP archive
    '''
    if len(creator) > SIZE['HEADER_FILE-CREATOR']:
        raise ValueError("Creator name longer than %d characters: %s" % (SIZE['HEADER_FILE-CREATOR'],creator))

    # check filenames for validity and start building ToC
    toc = list(); file2path = dict()
    for i,e in enumerate(files):
        archive_path, disk_path = e
        f = archive_path.split('/')[-1]
        if len(f) > SIZE['TOC-ENTRY_FILENAME']:
            raise ValueError("File name longer than %d characters: %s" % (SIZE['TOC-ENTRY_FILENAME'],f))
        path = '/'.join(archive_path.split('/')[:-1])
        if len(path) > SIZE['CONTAB-ENTRY_FOLDER-NAME']:
            raise ValueError("Path name longer than %d characters: %s" % (SIZE['CONTAB-ENTRY_FOLDER-NAME'],path))
        if f not in file2path:
            file2path[f] = list()
        file2path[f].append((path,i)) # (location, ToC index) tuple
        entry = {'filename':f, 'path':path, 'diskpath':disk_path, 'filesize': getsize(disk_path)}
        entry['check'] = 14 # It seems like most programs just give 14 (the most common value) and FF7 doesn't care. Hopefully somebody can figure out a correct way some day. I thought it might be User+Group file permissions (7+7=14)
        toc.append(entry)
    if len(toc) > MAX_UNSIGNED_INT:
        raise ValueError("Number of files (%d) exceeds maximum allowed (%d)" % (len(toc),MAX_UNSIGNED_INT))

    # get information for conflict table
    conflict2file = list(); file2conflict = dict()
    for e in toc:
        if len(file2path[e['filename']]) > MAX_UNSIGNED_SHORT:
            raise ValueError("Number of duplicate locations for filename '%s' (%d) exceeds maximum allowed (%d)" % (e['filename'],len(file2path[e['filename']]),MAX_UNSIGNED_SHORT))
        if len(file2path[e['filename']]) > 1:
            if e['filename'] not in file2conflict:
                conflict2file.append(e['filename']); file2conflict[e['filename']] = len(conflict2file)
        else:
            file2conflict[e['filename']] = 0
        e['conflict_index'] = file2conflict[e['filename']]
    if len(conflict2file) > MAX_UNSIGNED_SHORT:
        raise ValueError("Number of conflicting filenames (%d) exceeds maximum allowed (%d)" % (len(conflict2file),MAX_UNSIGNED_SHORT))

    # compute data start positions
    toc_size = len(toc) * SIZE['TOC-ENTRY']
    contab_size = SIZE['CONTAB_NUM-CONFLICTS'] + sum((SIZE['CONTAB-ENTRY_NUM-LOCATIONS'] + len(file2path[f])*(SIZE['CONTAB-ENTRY_FOLDER-NAME']+SIZE['CONTAB-ENTRY_TOC-INDEX'])) for f in file2conflict if file2conflict[f] != 0)
    data_start = SIZE['HEADER'] + toc_size + SIZE['LOOKTAB'] + contab_size
    curr_start = data_start
    for e in toc:
        e['data_start'] = curr_start; curr_start += (SIZE['DATA-ENTRY_FILENAME'] + SIZE['DATA-ENTRY_FILESIZE'] + e['filesize'])

    # build LGP file
    with open(lgp_filename, 'wb') as outfile:
        # write header
        outfile.write((SIZE['HEADER_FILE-CREATOR']-len(creator))*NULL_BYTE); outfile.write(creator.encode()) # file creator (12 bytes)
        outfile.write(pack('I', len(toc))) # number of files (4 bytes)

        # write table of contents
        for e in toc:
            outfile.write(e['filename'].encode()); outfile.write((SIZE['TOC-ENTRY_FILENAME']-len(e['filename']))*NULL_BYTE) # filename (20 bytes)
            outfile.write(pack('I', e['data_start'])) # data start position (4 bytes)
            outfile.write(bytes([e['check']])) # check code (1 byte)
            outfile.write(pack('H', e['conflict_index'])) # conflict table index (2 bytes)
        
        # write lookup table
        for pair in toc_to_lookup_table(toc):
            for e in pair:
                outfile.write(pack('H', e)) # lookup table index and count (2 bytes each)

        # write conflict table
        outfile.write(pack('H', len(conflict2file)))
        for f in conflict2file:
            outfile.write(pack('H', len(file2path[f]))) # number of locations (2 bytes)
            for p,i in file2path[f]:
                outfile.write(p.encode()); outfile.write((SIZE['CONTAB-ENTRY_FOLDER-NAME']-len(p))*NULL_BYTE) # location path (128 bytes)
                outfile.write(pack('H', i)) # ToC index (2 bytes)

        # write file data
        for e in toc:
            if outfile.tell() != e['data_start']:
                raise RuntimeError("File %s should be written at offset %d, but file is currently at offset %d" % (e['diskpath'],e['data_start'],outfile.tell()))
            outfile.write(e['filename'].encode()); outfile.write((SIZE['DATA-ENTRY_FILENAME']-len(e['filename']))*NULL_BYTE) # filename (20 bytes)
            outfile.write(pack('I', e['filesize'])) # filesize (4 bytes)
            with open(e['diskpath'],'rb') as tmpfile:
                outfile.write(tmpfile.read())

        # write file terminator
        outfile.write(terminator.encode())

class LGP:
    '''LGP Archive class'''
    def __init__(self, filename, check=False):
        '''``LGP`` constructor

        Args:
            ``filename`` (``str``): The filename of the LGP archive

            ``check`` (``bool``): ``True`` to check the Lookup Table vs. Table of Contents for validity, otherwise ``False``
        '''
        self.filename = filename; self.file = open(filename, 'rb'); total_filesize = getsize(self.filename)

        # read header
        tmp = self.file.read(SIZE['HEADER'])
        self.header = {
            'file_creator': tmp[START['HEADER_FILE-CREATOR']:START['HEADER_FILE-CREATOR']+SIZE['HEADER_FILE-CREATOR']].decode().strip(NULL_STR),
            'num_files': unpack('I', tmp[START['HEADER_NUM-FILES']:START['HEADER_NUM-FILES']+SIZE['HEADER_NUM-FILES']])[0],
        }

        # read table of contents
        self.toc = list(); self.conflicting_filenames = set()
        for i in range(self.header['num_files']):
            tmp = self.file.read(SIZE['TOC-ENTRY'])
            tmp_filename = tmp[START['TOC-ENTRY_FILENAME']:START['TOC-ENTRY_FILENAME']+SIZE['TOC-ENTRY_FILENAME']].decode().strip(NULL_STR)
            tmp_data_start = unpack('I', tmp[START['TOC-ENTRY_DATA-START']:START['TOC-ENTRY_DATA-START']+SIZE['TOC-ENTRY_DATA-START']])[0]
            tmp_check = ord(tmp[START['TOC-ENTRY_CHECK']:START['TOC-ENTRY_CHECK']+SIZE['TOC-ENTRY_CHECK']])
            tmp_conflict_index = unpack('H', tmp[START['TOC-ENTRY_CONFLICT-INDEX']:START['TOC-ENTRY_CONFLICT-INDEX']+SIZE['TOC-ENTRY_CONFLICT-INDEX']])[0]
            self.toc.append({'filename':tmp_filename, 'data_start':tmp_data_start, 'check':tmp_check, 'conflict_index':tmp_conflict_index})
            if tmp_conflict_index != 0:
                self.conflicting_filenames.add(tmp_filename)

        # read lookup table (3600 bytes)
        tmp = self.file.read(SIZE['LOOKTAB'])
        self.lookup_table = list()
        for i in range(NUM_LOOKTAB_ENTRIES):
            start = i*SIZE['LOOKTAB-ENTRY']
            tmp_toc_index = unpack('H', tmp[start : start + SIZE['LOOKTAB-ENTRY_INDEX']])[0]
            tmp_file_count = unpack('H', tmp[start + SIZE['LOOKTAB-ENTRY_INDEX'] : start + SIZE['LOOKTAB-ENTRY']])[0]
            self.lookup_table.append((tmp_toc_index,tmp_file_count))

        # read conflict table (2 bytes for number of conflicts, and for files with num_conflicts != 0, the actual table)
        self.num_conflicting_filenames = unpack('H', self.file.read(SIZE['CONTAB_NUM-CONFLICTS']))[0] # the first 2 bytes of the conflict table are the number of conflicts
        for i in range(self.num_conflicting_filenames): # if there were conflicts, handle them (e.g. magic.lgp); other files work properly (num_conflicting = 0)
            curr_num_conflicts = unpack('H', self.file.read(SIZE['CONTAB-ENTRY_NUM-LOCATIONS']))[0]
            for j in range(curr_num_conflicts):
                curr_folder_name = self.file.read(SIZE['CONTAB-ENTRY_FOLDER-NAME']).decode().strip(NULL_STR)
                curr_toc_index = unpack('H', self.file.read(SIZE['CONTAB-ENTRY_TOC-INDEX']))[0] #- 1 # it's 1-based, so subtract 1 to get indexing into self.toc
                self.toc[curr_toc_index]['filename'] = "%s/%s" % (curr_folder_name, self.toc[curr_toc_index]['filename']) # update filename in Table of Contents

        # read file sizes
        for entry in self.toc:
            self.file.seek(entry['data_start']+SIZE['DATA-ENTRY_FILENAME'], 0); entry['filesize'] = unpack('I', self.file.read(SIZE['DATA-ENTRY_FILESIZE']))[0]

        # read any remaining files that weren't in Table of Contents (e.g. in battle.lgp)
        self.non_toc_files = list()
        self.file.seek(self.toc[-1]['data_start']+SIZE['DATA-ENTRY_FILENAME'], 0) # move to filesize of last file
        self.file.seek(unpack('I', self.file.read(SIZE['DATA-ENTRY_FILESIZE']))[0], 1) # move forward to end of last file's data
        stopping_point = total_filesize - SIZE['TERMINATOR']
        while self.file.tell() < stopping_point:
            entry = dict()
            entry['data_start'] = self.file.tell()
            entry['filename'] = self.file.read(SIZE['TOC-ENTRY_FILENAME']).decode().strip(NULL_STR)
            entry['filesize'] = unpack('I', self.file.read(SIZE['DATA-ENTRY_FILESIZE']))[0]
            self.file.seek(self.file.tell()+entry['filesize'])
            self.non_toc_files.append(entry)

        # read terminator
        if total_filesize - self.file.tell() != SIZE['TERMINATOR']:
            raise ValueError(ERROR_TERMINATOR_SIZE)
        self.terminator = self.file.read().decode().strip(NULL_STR)

        # check lookup table for validity
        if check and not self.valid_lookup():
            raise ValueError(ERROR_LOOKUP_TOC_MISMATCH)

    def __del__(self):
        '''``LGP`` destructor'''
        if hasattr(self, 'file'):
            self.file.close()

    def __len__(self):
        '''Return the number of files in this archive

        Returns:
            ``int``: The number of files in this archive
        '''
        return self.header['num_files']+len(self.non_toc_files)

    def __iter__(self):
        '''Iterate over the file entires in this LGP'''
        for entry in self.toc+self.non_toc_files:
            yield entry

    def load_bytes(self, start, size):
        '''Load the first ``size`` bytes starting with position ``start``

        Args:
            ``start`` (``int``): The start position

            ``size`` (``int``): The number of bytes to read

        Returns:
            ``bytes``: The first ``size`` bytes starting with position ``start``
        '''
        self.file.seek(start, 0)
        return self.file.read(size)

    def load_toc_entry(self, entry):
        '''Load the data for a given Table of Contents entry

        Args:
            ``entry`` (``dict``): The Table of Contents entry to load

        Returns:
            ``bytes``: The data corresponding to the given Table of Contents entry
        '''
        if 'data_start' not in entry or 'filesize' not in entry:
            raise TypeError(ERROR_INVALID_TOC_ENTRY)
        return self.load_bytes(entry['data_start']+SIZE['DATA-ENTRY_HEADER'], entry['filesize'])

    def load_files(self):
        '''Load each file contained in the LGP archive, yielding (filename, data) tuples'''
        for entry in self.toc+self.non_toc_files:
            yield (entry['filename'], self.load_toc_entry(entry))

    def valid_lookup(self):
        '''Check if this LGP file's Lookup Table is valid with respect to its Table of Contents

        Returns:
            ``bool``: ``True`` if Lookup Table is valid with respect to Table of Contents, otherwise ``False``
        '''
        return self.lookup_table == toc_to_lookup_table(self.toc)
