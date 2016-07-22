#!/usr/bin/python

import contextlib
import datetime
import os
import sys
from time import time, gmtime
import unicodedata


import dropbox
#from dropbox.files import FileMetadata, FolderMetadata

####################################
def upload(dbx, fullname, folder, subfolder, name, overwrite=False):
    """Upload a file.
    Return the request response, or None in case of error.
    """
    path = '/%s/%s/%s' % (folder, subfolder.replace(os.path.sep, '/'), name)
    while '//' in path:
        path = path.replace('//', '/')
    mode = (dropbox.files.WriteMode.overwrite
            if overwrite
            else dropbox.files.WriteMode.add)
    mtime = os.path.getmtime(fullname)

    with open(fullname, 'rb') as f:
        data = f.read()

    t0 = time()
    try:
        res = dbx.files_upload (data, path, mode,
            client_modified=datetime.datetime(*gmtime(mtime)[:6]),
            mute=True)
    except dropbox.exceptions.ApiError as err:
        print('*** Dropbox API error', err)
        return None

    print('Total elapsed time for %d bytes: %.3f s' % (len(data), time() - t0))

    print('uploaded as', res.name.encode('utf8'))
    return res

####################################
DROPBOX_TOKEN = os.environ['DROPBOX_TOKEN']

####################################
def simple_upload (dbx, dropbox_folder, local_dir, subfolder, file_to_move):
    print('Dropbox folder name:', dropbox_folder)
    print('Local file path:', local_dir+ "/"+ file_to_move)
    subdir = subfolder
    upload(dbx, "/".join([local_dir, subdir, file_to_move]), dropbox_folder, subfolder, file_to_move)

####################################
def recursive_upload(dbx, dropbox_folder, local_dir, subdir):
    for dirpath, dirs, files in os.walk(local_dir+"/"+subdir):
        subfolder = dirpath[len(local_dir):].strip(os.path.sep)
        for file in files:
            simple_upload(dbx, dropbox_folder, local_dir, subfolder, file)

####################################
def simple_upload_with_timestamp_checking(dbx, dropbox_folder, local_dir, subfolder, file_to_move):

    subdir = subfolder
    fullname = "/".join([local_dir, subdir, file_to_move])
    print('Dropbox folder name:', dropbox_folder)
    print('Local file path:', fullname)

    mtime    = os.path.getmtime(fullname)
    mtime_dt = datetime.datetime(*time.gmtime(mtime)[:6])
    size      = os.path.getsize(fullname)
    #thinking about this as

    upload(dbx, fullname, dropbox_folder, subfolder, file_to_move)


####################################
def recursive_upload_with_timestamp_checking(dbx, dropbox_folder, local_dir, subdir):
    for dirpath, dirs, files in os.walk(local_dir + "/" + subdir):
        subfolder = dirpath[len(local_dir):].strip(os.path.sep)
        for file in files:
            simple_upload(dbx, dropbox_folder, local_dir, subfolder, file)

####################################
def exercise1_simple_upload (dropbox_folder, local_dir, subfolder, file_to_move):
    dbx = dropbox.Dropbox(DROPBOX_TOKEN)
    simple_upload(dbx, dropbox_folder, local_dir, subfolder, file_to_move)

####################################
def exercise2_recursive_upload(dropbox_folder, local_dir, subfolder):
    dbx = dropbox.Dropbox(DROPBOX_TOKEN)
    recursive_upload(dbx, dropbox_folder, local_dir, subfolder)

####################################
def exercise3_recursive_upload_with_timestamp_checking(dropbox_folder, local_dir, subfolder):
    dbx = dropbox.Dropbox(DROPBOX_TOKEN)
    recursive_upload_with_timestamp_checking(dbx, dropbox_folder, local_dir, subfolder)

####################################
def main():
    #exercise1_simple_upload("raw_data", "/home/ivana/scratch", "", "hello")
    exercise2_recursive_upload("raw_data", "/home/ivana/scratch", "move_exercise")
    exercise3_recursive_upload_with_timestamp_checking("raw_data", "/home/ivana/scratch", "move_exercise")

####################################
if __name__ == '__main__':
    main()