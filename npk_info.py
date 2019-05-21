#!/usr/bin/env python3
'''
Read the information of an NPK archive
Niema Moshiri 2019
'''
from PyFF7.npk import NPK
from sys import argv,stderr
USAGE = "USAGE: %s <npk_file>" % argv[0]

# error messages
#ERROR_HEADER_TOC_LENGTH_MISMATCH = "Number of files in header doesn't match Table of Contents length"
#ERROR_TOC_CONTAB_NUM_CONFLICTS_MISMATCH = "Number of conflicting files in Conflict Table doesn't match Table of Contents"

if __name__ == "__main__":
    if len(argv) != 2 or argv[1] == '-h' or argv[1] == '--help':
        print(USAGE); exit(1)
    npk = NPK(argv[1])
    try:
        print("Information")
        print("* File Name: %s" % argv[1])
        print("* Number of Files: %d" % len(npk))
        for i,f in enumerate(npk):
            print("  File %d: %d bytes" % (i+1,len(f)))
    except BrokenPipeError:
        stderr.close()
