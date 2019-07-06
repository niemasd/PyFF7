#!/usr/bin/env python3
'''
Read the information of an RSD file
Niema Moshiri 2019
'''
from PyFF7.rsd import RSD
from sys import argv,stderr
USAGE = "USAGE: %s <input_rsd_file>" % argv[0]

if __name__ == "__main__":
    if len(argv) != 2 or argv[1] == '-h' or argv[1] == '--help':
        print(USAGE); exit(1)
    rsd = RSD(argv[1])
    try:
        print("Information")
        print("* File Name: %s" % argv[1])
        print("* ID: %s" % rsd.ID)
        print("* Polygon Mesh File (PLY): %s" % rsd.attr['PLY'])
        print("* Material File (MAT): %s" % rsd.attr['MAT'])
        print("* Group File (GRP): %s" % rsd.attr['GRP'])
        print("* Number of Textures: %d" % len(rsd.attr['TEX']))
        for i,tex in enumerate(rsd.attr['TEX']):
            print("  * Texture %d: %s" % ((i+1),tex))
    except BrokenPipeError:
        stderr.close()
