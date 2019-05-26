#!/usr/bin/env python3
'''
Unpack an LGP archive
Niema Moshiri 2019
'''
from PyFF7.lgp import LGP
from os import makedirs
from os.path import isdir,isfile
from sys import argv
from warnings import warn
USAGE = "USAGE: %s <input_lgp_file> <output_directory>" % argv[0]

if __name__ == "__main__":
    if len(argv) != 3:
        print(USAGE); exit(1)
    if isdir(argv[2]) or isfile(argv[2]):
        raise ValueError("ERROR: Specified output directory exists: %s" % argv[2])
    lgp = LGP(argv[1]); makedirs(argv[2])
    print("LGP File: %s" % argv[1])
    print("Output Directory: %s" % argv[2])
    tot = len(lgp)
    for i,e in enumerate(lgp.load_files()):
        print("Extracting file %d of %d..." % (i+1,len(lgp)), end='\r')
        if '/' in e[0]:
            makedirs('%s/%s' % (argv[2], '/'.join(e[0].split('/')[:-1])), exist_ok=True)
        filename = "%s/%s" % (argv[2],e[0])
        try:
            isfile(filename)
        except:
            filename = filename[:filename.index('.')+4] # weird characters in filename, so truncate extension
        if isfile(filename):
            warn("Duplicate file not unpacked: %s" % filename); tot -= 1
        f = open(filename, 'wb'); f.write(e[1]); f.close()
    print("Extracted %d of %d files successfully" % (tot,len(lgp)))
