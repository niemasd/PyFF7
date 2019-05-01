#!/usr/bin/env python3
'''
Unpack an LGP archive
Niema Moshiri 2019
'''
from ff7toolkit.lgp import LGP
from os import mkdir
from os.path import isdir,isfile
from sys import argv,stdout
USAGE = "USAGE: %s <lgp_file> <output_directory>" % argv[0]

if __name__ == "__main__":
    if len(argv) != 3:
        print(USAGE); exit(1)
    if isdir(argv[2]) or isfile(argv[2]):
        raise ValueError("ERROR: Specified output directory exists: %s" % argv[2])
    lgp = LGP(argv[1]); mkdir(argv[2])
    print("LGP File: %s" % argv[1])
    print("Output Directory: %s" % argv[2])
    for i,e in enumerate(lgp.load_files()):
        print("Extracting file %d of %d..." % (i+1,len(lgp.toc)), end='\r')
        f = open("%s/%s" % (argv[2],e[0]), 'wb'); f.write(e[1]); f.close()
    print("Extracted %d files successfully" % len(lgp.toc))
