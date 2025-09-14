#!/usr/bin/env python3
'''
Pack an NPK archive
Niema Moshiri 2025
'''
from PyFF7.npk import pack_npk
from glob import glob
from os.path import isdir,isfile
from sys import argv,stderr
USAGE = "USAGE: %s <input_directory> <output_npk_file>" % argv[0]

if __name__ == "__main__":
    if len(argv) != 3:
        print(USAGE); exit(1)
    if not isdir(argv[1]):
        raise ValueError("Invalid directory: %s" % argv[1])
    if isfile(argv[2]) or isdir(argv[2]):
        raise ValueError("File exists: %s" % argv[2])
    filenames = sorted(glob('%s/*' % argv[1]))
    try:
        print("File Directory: %s" % argv[1])
        print("Number of Files: %d" % len(filenames))
        print("Output NPK: %s" % argv[2])
        pack_npk(filenames, argv[2])
    except BrokenPipeError:
        stderr.close()
