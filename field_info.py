#!/usr/bin/env python3
'''
Read the information of a Field File
Niema Moshiri 2019
'''
from PyFF7.field import FieldFile
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
        print("* Section 1: Field Script")
        print("  * Name: %s" % ff.field_script.name)
        print("  * Creator: %s" % ff.field_script.creator)
        print("  * Version: %d" % ff.field_script.version)
        print("  * Scale: %d" % ff.field_script.scale)
        print("  * Number of Actors: %d" % len(ff.field_script.actor_names))
        print("  * Actor Names: %s" % ', '.join(ff.field_script.actor_names))
        print("  * Number of Models: %d" % ff.field_script.num_models)
        print("  * Length of Script Code: %d bytes" % len(ff.field_script.script_code))
        print("  * Number of Strings: %d" % len(ff.field_script.string_data))
        for s in ff.field_script.get_strings():
            print("    * %s" % s.replace('\n','\\n'))
        print("  * Number of Akao/Tutorial Blocks: %d" % len(ff.field_script.akao))
        '''
        print("* File Name: %s" % argv[1])
        print("* File Creator: %s" % lgp.header['file_creator'])
        print("* File Terminator: %s" % lgp.terminator)
        print("* File ToC and Lookup Match: %s" % lgp.valid_lookup())
        print("* Number of Files: %d" % len(lgp))
        print("* Number of Filenames with Conflicts: %d" % lgp.num_conflicting_filenames)
        print()
        print("Table of Contents")
        print("* FILENAME\tFILESIZE\tSTART\tCHECK\tCONFLICT TABLE INDEX")
        for entry in lgp.toc:
            print("* %s\t%d\t%d\t%d\t%d" % (entry['filename'], entry['filesize'], entry['data_start'], entry['check'], entry['conflict_index']))
        '''
    except BrokenPipeError:
        stderr.close()
