#!/usr/bin/python

import os

local_dir = "/Users/ivana/Dropbox/Olaf"
print local_dir
print(os.path.isdir(local_dir))
for dirpath, dirs, files in os.walk(local_dir):
    print dirpath
    subfolder = dirpath[len(local_dir):].strip(os.path.sep)
    print subfolder
    for file in files:
        print "\t\t" + file
    print


