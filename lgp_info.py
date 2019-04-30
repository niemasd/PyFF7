#!/usr/bin/env python3
'''
Read the information of an LGP file
Niema Moshiri 2019
'''
from ff7toolkit.lgp import read_lgp_info
from sys import argv
USAGE = "USAGE: %s <lgp_file>" % argv[0]

if __name__ == "__main__":
    if len(argv) != 2:
        print(USAGE); exit(1)
    header,toc,crc = read_lgp_info(argv[1])
    print("=== Header ===")
    print("- File Creator: %s" % header['file_creator'])
    print("- Number of Files: %d" % header['num_files'])
    print()
    print("=== Table of Contents ===")
