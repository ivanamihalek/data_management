#! /usr/bin/python

# for mafs, fastqs, and tarballs:

# try finding in Dropbox
# if not found sound alarm and exit
# if found in dropbox, download to scratch

# check if the md5sum is the saem as the original
# if the sums are not ok:  sound alarm and exit

# store the name of the file to ARCHIVED
# delete the original and the file in the scratch


from  data_mgmt_utils_py.generic_utils import *
from  data_mgmt_utils_py.dropbox_utils import *



####################################
DROPBOX_TOKEN = os.environ['DROPBOX_TOKEN']

dbx = dropbox.Dropbox(DROPBOX_TOKEN)


####################################
def store_archived (local_dir, subfolder):
    archived_file = "/".join([local_dir, subfolder, "ARCHIVED"])
    if not os.path.exists(archived_file):  # read and append this name if not present
        pass
    else:  # create new file and write the name to it
        pass

####################################
def main():

    local_dir      = "/data01"
    dropbox_folder = "/raw_data"
    scratch_dir    = "/home/ivana/scratch"

    if not check_local_path(local_dir): exit(1)
    if not check_dbx_path (dbx, dropbox_folder): exit(1)

    subdir = ""

    for dirpath, dirs, files in os.walk(local_dir + "/" + subdir):
        subfolder = dirpath[len(local_dir):].strip(os.path.sep)
        print dirpath, dirs, files
        for file in files:
            # for bams, fastqs, and tarballs
            # (bams are binaries and compression does not further reduce their size)
            print file
            print file.split('.')
            print file.split('.')[-1]
            if not file.split('.')[-1] in ["gz", "bz2", "bam", "tar", "fastq"]: continue
            # local version of the file and its checksum
            local_file_path = "/".join([local_dir, subfolder, file])
            local_md5_path  = "/".join([local_dir, subfolder, "md5sums", file+".md5"])
            print local_file_path
            print local_md5_path
            md5sum_local = os.popen("cat %s | cut -d' ' -f 1" % local_md5_path).read().rstrip()
            print "md5sum_local: ", md5sum_local
            continue
            # try finding in Dropbox
            dbx_path = "/".join([dropbox_folder, subfolder, file])
            # if not found sound alarm and exit
            if not check_dbx_path(dbx, dbx_path):
                print local_file_path, "not found in Dropbox"
                print "(I checked in %s)" % dbx_path
                exit(1)
            # if found in dropbox, download to scratch
            scratch_path = "%s/%s" % (scratch_dir, file)
            time_start = time()
            print local_file_path
            print dbx_path
            print scratch_path
            print " ... "
            download (dbx, scratch_path, dbx_path)
            print "done in %.1fs" % (time() - time_start)
            # check if the md5sum is the same as the original
            md5sum_scratch = os.popen("md5sum %s | cut -d' ' -f 1" % scratch_path).read()
            print "md5sum_scratch: ", md5sum_scratch
            # if the sums are not ok:  sound alarm and exit
            if md5sum_scratch != md5sum_local:
                print "md5sum mismatch"
                exit(1)
            # store the name of the file to ARCHIVED
            store_archived (local_dir, subfolder)

            # delete the original and the file in the scratch
            exit(1)

####################################
if __name__ == '__main__':
    main()
