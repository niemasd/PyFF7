#!/usr/bin/env python3
'''
View a TEX file
Niema Moshiri 2019
'''
from PyFF7.tex import TEX
from sys import argv,stderr
USAGE = "USAGE: %s <input_tex_file>" % argv[0]

if __name__ == "__main__":
    if len(argv) != 2 or argv[1] == '-h' or argv[1] == '--help':
        print(USAGE); exit(1)
    TEX(argv[1]).show()
