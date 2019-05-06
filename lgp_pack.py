#!/usr/bin/env python3
'''
Pack an LGP archive
Niema Moshiri 2019
'''
from PyFF7.lgp import pack_lgp
from glob import glob
from os.path import isdir,isfile
from sys import argv,stderr
USAGE = "USAGE: %s <file_directory> <output_lgp_file>" % argv[0]

if __name__ == "__main__":
    if len(argv) != 3:
        print(USAGE); exit(1)
    if not isdir(argv[1]):
        raise ValueError("Invalid directory: %s" % argv[1])
    if isfile(argv[2]) or isdir(argv[2]):
        raise ValueError("File exists: %s" % argv[2])
    filenames = sorted([('/'.join(f.split('/')[1:]), f) for f in glob('%s/**'%argv[1], recursive=True) if not isdir(f)], key=lambda x: x[0].split('/')[-1].lower())
    try:
        print("File Directory: %s" % argv[1])
        print("Number of Files: %d" % len(filenames))
        print("Output LGP: %s" % argv[2])
        pack_lgp(filenames, argv[2])
    except BrokenPipeError:
        stderr.close()
