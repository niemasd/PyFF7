#!/usr/bin/env python3
'''
Read the information of an HRC file
Niema Moshiri 2019
'''
from PyFF7.hrc import HRC
from sys import argv,stderr
USAGE = "USAGE: %s <input_hrc_file>" % argv[0]

if __name__ == "__main__":
    if len(argv) != 2 or argv[1] == '-h' or argv[1] == '--help':
        print(USAGE); exit(1)
    hrc = HRC(argv[1])
    try:
        print("Information")
        print("* File Name: %s" % argv[1])
        print("* Header Block: %d Attributes" % len(hrc.header))
        for k,v in hrc.header:
            print("  * %s: %s" % (str(k),str(v)))
        print("* Number of Bones: %d" % len(hrc.bones))
        for i,bone in enumerate(hrc.bones):
            print("  * Bone %d:" % (i+1))
            print("    * Name: %s" % bone['name'])
            print("    * Parent Name: %s" % bone['parent'])
            print("    * Length: %f" % bone['length'])
            print("    * RSD Files: %d" % len(bone['rsd']))
            for j,rsd in enumerate(bone['rsd']):
                print("      * RSD File %d: %s" % (j+1,rsd))
    except BrokenPipeError:
        stderr.close()
