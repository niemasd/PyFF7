#!/usr/bin/env python3
'''
Extract the background from a Field file
Niema Moshiri 2019
'''
from PyFF7.field import FieldFile
from os.path import isdir,isfile
from sys import argv,stderr
USAGE = "USAGE: %s <input_field_file> <output_image_file>" % argv[0]

if __name__ == "__main__":
    if len(argv) != 3:
        print(USAGE); exit(1)
    if isdir(argv[2]) or isfile(argv[2]):
        raise ValueError("ERROR: Specified output directory exists: %s" % argv[2])
    print("Input File: %s" % argv[1])
    print("Output File: %s" % argv[2])
    FieldFile(argv[1]).get_bg_image().save(argv[2])
