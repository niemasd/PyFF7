#!/usr/bin/env python3
'''
Read the information of an NPK archive
Niema Moshiri 2019
'''
from PyFF7.npk import NPK
from sys import argv,stderr
USAGE = "USAGE: %s <input_npk_file>" % argv[0]

if __name__ == "__main__":
    if len(argv) != 2 or argv[1] == '-h' or argv[1] == '--help':
        print(USAGE); exit(1)
    npk = NPK(argv[1])
    try:
        print("Information")
        print("* File Name: %s" % argv[1])
        print("* Number of Files: %d" % len(npk))
        for i,f in enumerate(npk):
            print("  File %d: %d bytes" % (i+1,len(f)))
    except BrokenPipeError:
        stderr.close()
