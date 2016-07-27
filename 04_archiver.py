#! /usr/bin/python

# for mafs, fastqs, and tarballs:

# try find ing in Dropbox
# if not found sound alarm and exit
# if found in dropbox, download to scratch

# check if the md5sum is the saem as the original
# if the sums are not ok:  sound alarm and exit

# store the name of the file to ARCHIVED
# delete the original and the file in the scratch

import os
import dropbox

from data_mgmt_utils.utils import *
from data_mgmt_utils.dropbox import *



####################################
DROPBOX_TOKEN = os.environ['DROPBOX_TOKEN']
CHUNK_SIZE    = 10 * 1024 * 1024
MAX_RETRIES   = 20

dbx = dropbox.Dropbox(DROPBOX_TOKEN)

####################################
def main():

    local_dir      = "/data01"
    dropbox_folder = "/raw_data"
    scratch_dir   = "/home/ivana/scratch"

    if not check_local_path(local_dir): exit(1)
    if not check_dbx_path (dropbox_folder): exit(1)

    subdir = ""

    for dirpath, dirs, files in os.walk(local_dir + "/" + subdir):
        subfolder = dirpath[len(local_dir):].strip(os.path.sep)
        for file in files:
            # for bams, fastqs, and tarballs
            # #bams are binaries and compression does not further reduce ther size
            if not file[-3:] in ["bz2", ".bam"]: continue
            # try finding in Dropbox
            local_file_path = "/".join([local_dir, subdir, file])
            dbx_path = "/".join([dropbox_folder, subfolder, file])
            # if not found sound alarm and exit
            if not check_dbx_path(dbx, dbx_path):
                print local_file_path, "not found in Dropbox"
                print "(I checked in %s)" % dbx_path
                exit(1)
            # if found in dropbox, download to scratch
            scratch_path = "%s/%s" % (scratch_dir, file)
            print local_file_path
            print dbx_path
            print scratch_path
            print " ... "
            download (dbx, scratch_path, dbx_path)
            print "done"
            exit(1)
            # check if the md5sum is the same as the original

            # if the sums are not ok:  sound alarm and exit

            # store the name of the file to ARCHIVED

            # delete the original and the file in the scratch


####################################
if __name__ == '__main__':
    main()