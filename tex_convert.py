#!/usr/bin/env python3
'''
Convert a TEX file to a regular image file
Niema Moshiri 2019
'''
from PyFF7.tex import TEX
from os.path import isdir,isfile
from sys import argv,stderr
USAGE = "USAGE: %s <input_tex_file> <output_image_file>" % argv[0]

if __name__ == "__main__":
    if len(argv) != 3:
        print(USAGE); exit(1)
    if isdir(argv[2]) or isfile(argv[2]):
        raise ValueError("ERROR: Specified output file exists: %s" % argv[2])
    images = TEX(argv[1]).get_images()
    if len(images) == 1:
        images[0].save(argv[2])
    else: # multiple color palettes
        pre = '.'.join(argv[2].split('.')[:-1]); suf = argv[2].split('.')[-1]; numlen = len(str(len(images)-1))
        for i,img in enumerate(images):
            img.save("%s.pal%s.%s" % (pre, str(i).zfill(numlen), suf))
