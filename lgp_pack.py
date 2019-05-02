#!/usr/bin/env python3
'''
Pack an LGP archive
Niema Moshiri 2019
'''
from PyFF7.lgp import pack_lgp,SIZE
from glob import glob
from os.path import isdir,isfile
from sys import argv
USAGE = "USAGE: %s <file_directory> <output_lgp_file>" % argv[0]

def iterate_file_data(folder, filenames):
    for filename in filenames:
        with open('%s/%s' % (folder,filename), 'rb') as f:
            yield (filename, f.read())

if __name__ == "__main__":
    if len(argv) != 3:
        print(USAGE); exit(1)
    if not isdir(argv[1]):
        raise ValueError("Invalid directory: %s" % argv[1])
    if isfile(argv[2]) or isdir(argv[2]):
        raise ValueError("File exists: %s" % argv[2])
    filenames = sorted([f.split('/')[-1] for f in glob('%s/*'%argv[1])], key=lambda x: x.lower())
    for f in filenames:
        if len(f) > SIZE['TOC-ENTRY_FILENAME']:
            raise ValueError("File name longer than %d characters: %s" % (SIZE['TOC-ENTRY_FILENAME'],f))
        if isdir('%s/%s' % (argv[1],f)):
            raise ValueError("File directory contains a directory: %s" % f)
    print("File Directory: %s" % argv[1])
    print("Number of Files: %d" % len(filenames))
    print("Output LGP: %s" % argv[2])
    pack_lgp(len(filenames), iterate_file_data(argv[1],filenames), argv[2])
