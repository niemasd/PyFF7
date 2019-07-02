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
            print("  * Number of Vertices: %d" % len(obj['vertices']))
            for j,v in enumerate(obj['vertices']):
                print("    * Vertex %d: %s" % ((j+1), str(tuple(v)).replace(' ','')))
            print("  * Number of Normals: %d" % len(obj['normals']))
            for j,v in enumerate(obj['normals']):
                print("    * Normal %d: %s" % ((j+1), str(tuple(v)).replace(' ','')))
            print("  * Number of Primitives: %d" % len(obj['primitives']))
            #for j,p in enumerate(obj['primitives']):
            #    print("    * Primitive %d" % (j+1))
            #    print("      * Size of 2D Drawing Primitives (olen): %d" % p['olen'])
            #    print("      * Size of Packet Data Section (ilen): %d" % p['ilen'])
            #    print("      * GRD Flag: %d" % p['flags']['GRD'])
            #    print("      * FCE Flag: %d" % p['flags']['FCE'])
            #    print("      * LGT Flag: %d" % p['flags']['LGT'])
            #    print("      * Mode: %s" % p['mode'])
    except BrokenPipeError:
        stderr.close()
