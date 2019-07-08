#!/usr/bin/env python3
'''
Create a TEX file from an image file
Niema Moshiri 2019
'''
from PyFF7.tex import TEX
from PIL import Image
from os.path import isdir,isfile
from sys import argv,stderr
USAGE = "USAGE: %s <input_image_file> <output_tex_file> [-bmp]" % argv[0]

if __name__ == "__main__":
    if len(argv) != 3 and (len(argv) != 4 or argv[-1].lower() != '-bmp'):
        print(USAGE); exit(1)
    if isdir(argv[2]) or isfile(argv[2]):
        raise ValueError("ERROR: Specified output file exists: %s" % argv[2])
    img = Image.open(argv[1])
    tex = TEX(img)
    data = tex.get_bytes(bmp_mode = (len(argv) == 4 and argv[-1].lower() == '-bmp'))
    f = open(argv[2],'wb'); f.write(data); f.close()
