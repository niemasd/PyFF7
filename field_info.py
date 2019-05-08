#!/usr/bin/env python3
'''
Read the information of a Field File
Niema Moshiri 2019
'''
from PyFF7.field import FieldFile,SECTION_NAME
from sys import argv,stderr
USAGE = "USAGE: %s <field_file>" % argv[0]

if __name__ == "__main__":
    if len(argv) != 2 or argv[1] == '-h' or argv[1] == '--help':
        print(USAGE); exit(1)
    ff = FieldFile(argv[1])
    try:
        print("Information")
        print("* File Name: %s" % argv[1])
        print()
        print("* Section 1: %s" % SECTION_NAME[0])
        print("  * Name: %s" % ff.field_script.name)
        print("  * Creator: %s" % ff.field_script.creator)
        print("  * Version: %d" % ff.field_script.version)
        print("  * Scale: %d" % ff.field_script.scale)
        print("  * Number of Actors: %d" % len(ff.field_script.actor_names))
        print("  * Actor Names: %s" % ', '.join(ff.field_script.actor_names))
        print("  * Number of Models: %d" % ff.field_script.num_models)
        print("  * Length of Script Code: %d bytes" % len(ff.field_script.script_code))
        print("  * Number of Akao/Tutorial Blocks: %d" % len(ff.field_script.akao))
        print("  * Number of Strings: %d" % len(ff.field_script.string_data))
        for s in ff.field_script.get_strings():
            print("    * %s" % s.replace('\n','\\n'))
        print()
        print("* Section 2: %s" % SECTION_NAME[1])
        print("  * Number of Cameras: %d" % len(ff.camera_matrix))
        for i,cam in enumerate(ff.camera_matrix):
            print("  * Camera %d:" % (i+1))
            for a in ('x','y','z'):
                print("    * %s-Axis Vector: %s" % (a, str(cam['vector_%s'%a])))
            print("    * Position (Camera Space): %s" % str(cam['position_camera_space']))
            print("    * Zoom: %d" % cam['zoom'])

    except BrokenPipeError:
        stderr.close()
