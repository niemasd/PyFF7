#!/usr/bin/env python3
'''
Read the information of a TMD file
Niema Moshiri 2019
'''
from PyFF7.tmd import TMD
from sys import argv,stderr
USAGE = "USAGE: %s <input_tmd_file>" % argv[0]

if __name__ == "__main__":
    if len(argv) != 2 or argv[1] == '-h' or argv[1] == '--help':
        print(USAGE); exit(1)
    tmd = TMD(argv[1])
    try:
        print("Information")
        print("* File Name: %s" % argv[1])
        print("* Version: %d" % tmd.version)
        print("* Number of Objects: %d" % len(tmd.objects))
        for i,obj in enumerate(tmd.objects):
            print("* Object %d" % (i+1))
            print("  * Scale: %d" % obj['scale'])
    except BrokenPipeError:
        stderr.close()
