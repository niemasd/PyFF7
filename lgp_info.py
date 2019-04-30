#!/usr/bin/env python3
'''
Read the information of an LGP archive
Niema Moshiri 2019
'''
from ff7toolkit import NULL_STR
from ff7toolkit.lgp import read_lgp_info
from sys import argv
USAGE = "USAGE: %s <lgp_file>" % argv[0]

if __name__ == "__main__":
    if len(argv) != 2:
        print(USAGE); exit(1)
    header,toc,crc = read_lgp_info(argv[1])
    if header['num_files'] != len(toc):
        raise ValueError("Number of files in header doesn't match Table of Contents length")
    print("Information")
    print("* File Creator: %s" % header['file_creator'].strip(NULL_STR))
    print("* Number of Files: %d" % header['num_files'])
    print("* Length of CRC: %d bytes" % len(crc))
    print()
    print("Table of Contents")
    print("* FILENAME\tSTART\tCHECK\tDUPLICATE IDENTIFIER")
    for entry in toc:
        print("* %s\t%d\t%d\t%d" % (entry['filename'].strip(NULL_STR), entry['data_start'], entry['check'], entry['dup-ident']))
