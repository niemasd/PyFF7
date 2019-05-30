#!/usr/bin/env python3
'''
Change the background of a Field file
Niema Moshiri 2019
'''
from PyFF7.field import FieldFile
from os.path import isdir,isfile
from sys import argv,stderr
USAGE = "USAGE: %s <input_field_file> <input_image_file> <output_field_file>" % argv[0]

if __name__ == "__main__":
    if len(argv) != 4:
        print(USAGE); exit(1)
    if isdir(argv[3]) or isfile(argv[3]):
        raise ValueError("ERROR: Specified output file exists: %s" % argv[3])
    print("Input Field File: %s" % argv[1])
    print("Input Image File: %s" % argv[2])
    print("Output Field File: %s" % argv[3])
    ff = FieldFile(argv[1])
    ff.change_bg_image(argv[2])
    data = ff.get_bytes()
    f = open(argv[3],'wb'); f.write(data); f.close()
