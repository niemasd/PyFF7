#!/usr/bin/env python3
'''
LZSS-compress a file
Niema Moshiri 2019
'''
from PyFF7.lzss import compress_lzss
from os.path import isdir,isfile
from sys import argv
USAGE = "USAGE: %s <input_file> <output_lzss_file>" % argv[0]

if __name__ == "__main__":
    if len(argv) != 3:
        print(USAGE); exit(1)
    if isdir(argv[2]) or isfile(argv[2]):
        raise ValueError("ERROR: Specified output file exists: %s" % argv[2])
    print("Input File: %s" % argv[1])
    print("Output File: %s" % argv[2])
    out_bytes = compress_lzss(argv[1])
    f = open(argv[2],'wb'); f.write(out_bytes); f.close()
