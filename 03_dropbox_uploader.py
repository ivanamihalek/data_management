#!/usr/bin/python

import contextlib
import datetime
import os
import sys
from time import time, gmtime
import unicodedata


import dropbox

####################################
DROPBOX_TOKEN = os.environ['DROPBOX_TOKEN']
CHUNK_SIZE    = 10 * 1024 * 1024
MAX_RETRIES   = 20

dbx = dropbox.Dropbox(DROPBOX_TOKEN)

####################################
def check_local_path(path):
    if not os.path.exists(path):
        print path, "not found"
        return False
    if not os.path.isdir(path):
        print path, "does not seem to be a directory"
        return False
    return True

####################################
def check_dbx_path(dbx_path):
    try:
        dbx.files_get_metadata(dbx_path)
        return True
    except:
        return False

####################################
def upload(local_file_path, dbx_path):
    f = open(local_file_path)
    file_size = os.path.getsize(local_file_path)

    print
    print "#"*20
    
    if file_size <= CHUNK_SIZE:
        print "file size %d smaller than CHUNK_SIZE %d " % (file_size, CHUNK_SIZE)
        print dbx.files_upload(f, dbx_path)

    else:
        approx_number_of_chunks =  file_size/CHUNK_SIZE
        print "file size = %d, CHUNK_SIZE = %d  ==> approx %d chunks to upload" % (file_size, CHUNK_SIZE, approx_number_of_chunks)
        t_start = time()
        try:
            upload_session_start_result = dbx.files_upload_session_start(f.read(CHUNK_SIZE))
        except dropbox.exceptions.ApiError as err:
            print "Failed to start the upload session: %s. Exiting." % err
            exit(1)
        try:
            cursor = dropbox.files.UploadSessionCursor(session_id=upload_session_start_result.session_id, offset=f.tell())
        except dropbox.exceptions.ApiError as err:
            print "Failed to obtain cursor: %s. Exiting." % err
            exit(1)
        try:
            commit = dropbox.files.CommitInfo(path=dbx_path)
        except dropbox.exceptions.ApiError as err:
            print "Commit failure: %s. Exiting." % err
            exit(1)


        chunk_counter = 0
        panic_ctr     = 0
        while f.tell() < file_size:
            if ((file_size - f.tell()) <= CHUNK_SIZE):
                try:
                    dbx.files_upload_session_finish(f.read(CHUNK_SIZE), cursor, commit)
                except dropbox.exceptions.ApiError as err:
                    print "Upload finish failure:", err
                    print "Not sure what that means, so I'll exit."
                    exit(1)
            else:
                try :
                    dbx.files_upload_session_append(f.read(CHUNK_SIZE), cursor.session_id, cursor.offset)
                except dropbox.exceptions.ApiError as err:
                    print "Chunk upload failure:", err
                    panic_ctr += 1
                    if panic_ctr > MAX_RETRIES:
                        print "REached max number of retries. Bailing out."
                        exit(1)
                    print "Will retry ..."
                    continue
                panic_ctr = 0
                cursor.offset = f.tell()
                chunk_counter += 1
                if not chunk_counter%10:
                    time_elapsed    = time() - t_start
                    estimated_speed = chunk_counter*1./time_elapsed
                    time_remaining  = (approx_number_of_chunks - chunk_counter)/estimated_speed/60;
                    print "Uploaded %d chunks in %.1fs. Estimated time remaining %.1f min." % (chunk_counter, time_elapsed, time_remaining)
        print "Finished uploading in %.1f s." % (time() - t_start)
    f.close()
    exit(1)

####################################
def upload_with_existence_checking(dbx, dropbox_folder, local_dir, subfolder, file_to_move):

    subdir = subfolder
    local_file_path = "/".join([local_dir, subdir, file_to_move])
    dbx_path =  "/".join([dropbox_folder, subfolder, file_to_move])
    print('Dropbox path:',    dbx_path)
    print('Local file path:', local_file_path)
    # check file exists in Dbx already
    if check_dbx_path(dbx_path):
        print dbx_path + "   found"
    else:
        print dbx_path + "   not found - uploading"
        upload(local_file_path, dbx_path)



####################################
def main():

    local_dir      = "/data01"
    dropbox_folder = "/raw_data"

    if not check_local_path(local_dir): exit(1)
    if not check_dbx_path (dropbox_folder): exit(1)

    subdir = ""

    for dirpath, dirs, files in os.walk(local_dir + "/" + subdir):
        subfolder = dirpath[len(local_dir):].strip(os.path.sep)
        for file in files:
            if "bz2" != file[-3:]: continue
            print subfolder, file
            upload_with_existence_checking(dbx, dropbox_folder, local_dir, subfolder, file)


####################################
if __name__ == '__main__':
    main()