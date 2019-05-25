#!/usr/bin/env python3
'''
Decompress an LZSS-compressed file
Niema Moshiri 2019
'''
from PyFF7.lzss import decompress_lzss
from os.path import isdir,isfile
from sys import argv
USAGE = "USAGE: %s <input_lzss_file> <output_file>" % argv[0]

if __name__ == "__main__":
    if len(argv) != 3:
        print(USAGE); exit(1)
    if isdir(argv[2]) or isfile(argv[2]):
        raise ValueError("ERROR: Specified output file exists: %s" % argv[2])
    print("LZSS File: %s" % argv[1])
    print("Output File: %s" % argv[2])
    out_bytes = decompress_lzss(argv[1])
    f = open(argv[2],'wb'); f.write(out_bytes); f.close()
