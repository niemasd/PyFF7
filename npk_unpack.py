#!/usr/bin/env python3
'''
Unpack an NPK archive
Niema Moshiri 2019
'''
from PyFF7.npk import NPK
from os import makedirs
from os.path import isdir,isfile
from sys import argv
USAGE = "USAGE: %s <input_npk_file> <output_directory>" % argv[0]

if __name__ == "__main__":
    if len(argv) != 3:
        print(USAGE); exit(1)
    if isdir(argv[2]) or isfile(argv[2]):
        raise ValueError("ERROR: Specified output directory exists: %s" % argv[2])
    print("Loading NPK File: %s" % argv[1])
    npk = NPK(argv[1]); makedirs(argv[2]); NUM_LEN = len(str(len(npk)))
    print("Output Directory: %s" % argv[2])
    for i,data in enumerate(npk):
        print("Extracting file %d of %d..." % (i+1,len(npk)), end='\r')
        num = str(i+1).zfill(NUM_LEN); f = open("%s/file%s" % (argv[2],num), 'wb'); f.write(data); f.close()
    print("Extracted %d files successfully" % len(npk))
