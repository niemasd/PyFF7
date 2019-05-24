#!/usr/bin/env python3
'''
Read the information of an LGP archive
Niema Moshiri 2019
'''
from PyFF7.lgp import LGP
from sys import argv,stderr
USAGE = "USAGE: %s <lgp_file>" % argv[0]

# error messages
ERROR_HEADER_TOC_LENGTH_MISMATCH = "Number of files in header doesn't match Table of Contents length"
ERROR_TOC_CONTAB_NUM_CONFLICTS_MISMATCH = "Number of conflicting files in Conflict Table doesn't match Table of Contents"

if __name__ == "__main__":
    if len(argv) != 2 or argv[1] == '-h' or argv[1] == '--help':
        print(USAGE); exit(1)
    lgp = LGP(argv[1], check=False)
    if lgp.header['num_files'] != len(lgp.toc):
        raise ValueError(ERROR_HEADER_TOC_LENGTH_MISMATCH)
    if lgp.num_conflicting_filenames != len(lgp.conflicting_filenames):
        raise ValueError(ERROR_TOC_CONTAB_NUM_CONFLICTS_MISMATCH)
    try:
        print("Information")
        print("* File Name: %s" % argv[1])
        print("* File Creator: %s" % lgp.header['file_creator'])
        print("* File Terminator: %s" % lgp.terminator)
        print("* File ToC and Lookup Match: %s" % lgp.valid_lookup())
        print("* Number of Files: %d" % len(lgp))
        print("* Number of Filenames with Conflicts: %d" % lgp.num_conflicting_filenames)
        print()
        print("Table of Contents")
        print("* FILENAME\tFILESIZE\tSTART\tCHECK\tCONFLICT TABLE INDEX")
        for entry in lgp:
            if 'check' in entry:
                print("* %s\t%d\t%d\t%d\t%d" % (entry['filename'], entry['filesize'], entry['data_start'], entry['check'], entry['conflict_index']))
            else:
                print("* %s\t%d\t%d\tN/A\tN/A" % (entry['filename'], entry['filesize'], entry['data_start']))
    except BrokenPipeError:
        stderr.close()
