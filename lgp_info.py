#!/usr/bin/env python3
'''
Read the information of an LGP archive
Niema Moshiri 2019
'''
from PyFF7.lgp import LGP
from sys import argv,stderr
USAGE = "USAGE: %s <lgp_file>" % argv[0]

if __name__ == "__main__":
    if len(argv) != 2:
        print(USAGE); exit(1)
    lgp = LGP(argv[1])
    if lgp.header['num_files'] != len(lgp.toc):
        raise ValueError("Number of files in header doesn't match Table of Contents length")
    if lgp.num_conflicting_filenames != len(lgp.conflicting_filenames):
        raise ValueError("Number of conflicting files in Conflict Table doesn't match Table of Contents")
    try:
        print("Information")
        print("* File Name: %s" % argv[1])
        print("* File Creator: %s" % lgp.header['file_creator'])
        print("* File Terminator: %s" % lgp.terminator)
        print("* Number of Files: %d" % lgp.header['num_files'])
        print("* Number of Filenames with Conflicts: %d" % lgp.num_conflicting_filenames)
        #print("* Length of Conflict Table: %d" % len(lgp.conflict_table))
        print()
        print("Table of Contents")
        print("* FILENAME\tFILESIZE\tSTART\tCHECK\tCONFLICT TABLE INDEX")
        for entry in lgp.toc:
            print("* %s\t%d\t%d\t%d\t%d" % (entry['filename'], entry['filesize'], entry['data_start'], entry['check'], entry['conflict_index']))
    except BrokenPipeError:
        stderr.close()
