#!/usr/bin/env python3
'''
Change the image inside of a TEX file
Niema Moshiri 2019
'''
from PyFF7.tex import TEX
from os.path import isdir,isfile
from sys import argv,stderr
USAGE = "USAGE: %s <input_tex_file> <input_image_file> <output_tex_file>" % argv[0]

if __name__ == "__main__":
    if len(argv) != 4:
        print(USAGE); exit(1)
    if isdir(argv[3]) or isfile(argv[3]):
        raise ValueError("ERROR: Specified output file exists: %s" % argv[3])
    tex = TEX(argv[1])
    tex.change_image(argv[2])
    data = tex.get_bytes()
    f = open(argv[3],'wb'); f.write(data); f.close()
