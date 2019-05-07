#!/usr/bin/env python3
'''
Read the information of a Field File
Niema Moshiri 2019
'''
from PyFF7.field import FieldFile
from sys import argv,stderr
USAGE = "USAGE: %s <field_file>" % argv[0]

if __name__ == "__main__":
    if len(argv) != 2 or argv[1] == '-h' or argv[1] == '--help':
        print(USAGE); exit(1)
    ff = FieldFile(argv[1])
    try:
        print("Information")
        '''
        print("* File Name: %s" % argv[1])
        print("* File Creator: %s" % lgp.header['file_creator'])
        print("* File Terminator: %s" % lgp.terminator)
        print("* File ToC and Lookup Match: %s" % lgp.valid_lookup())
        print("* Number of Files: %d" % len(lgp))
        print("* Number of Filenames with Conflicts: %d" % lgp.num_conflicting_filenames)
        print()
        print("Table of Contents")
        print("* FILENAME\tFILESIZE\tSTART\tCHECK\tCONFLICT TABLE INDEX")
        for entry in lgp.toc:
            print("* %s\t%d\t%d\t%d\t%d" % (entry['filename'], entry['filesize'], entry['data_start'], entry['check'], entry['conflict_index']))
        '''
    except BrokenPipeError:
        stderr.close()
