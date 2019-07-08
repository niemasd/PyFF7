#!/usr/bin/env python3
'''
Read the information of a save file
Niema Moshiri 2019
'''
from PyFF7.save import PROP,Save
from sys import argv,stderr
USAGE = "USAGE: %s <input_save_file>" % argv[0]

if __name__ == "__main__":
    if len(argv) != 2 or argv[1] == '-h' or argv[1] == '--help':
        print(USAGE); exit(1)
    sav = Save(argv[1]); prop = PROP[sav.save_type]
    try:
        print("* File Name: %s" % argv[1])
        print("* Save Type: %s" % prop['label'])
        print("* Number of Save Slots: %s" % len(sav))
        for i,save_slot in enumerate(sav):
            print("*   Save Slot %d:" % (i+1))
    except BrokenPipeError:
        stderr.close()
