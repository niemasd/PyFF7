#!/usr/bin/env python3
'''
Read the information of a TEX file
Niema Moshiri 2019
'''
from PyFF7.tex import TEX
from sys import argv,stderr
USAGE = "USAGE: %s <input_tex_file>" % argv[0]

if __name__ == "__main__":
    if len(argv) != 2 or argv[1] == '-h' or argv[1] == '--help':
        print(USAGE); exit(1)
    tex = TEX(argv[1])
    try:
        print("* File Name: %s" % argv[1])
        print("* Image Width: %d" % tex.get_width())
        print("* Image Height: %d" % tex.get_height())
        print("* Unique RGBA Colors: %d" % tex.num_colors())
        for c in tex.unique_colors():
            print("  * (%d,%d,%d,%d)" % c)
    except BrokenPipeError:
        stderr.close()
