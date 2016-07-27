#!/usr/bin/python

import os
import dropbox

import data_mgmt_utils


####################################
DROPBOX_TOKEN = os.environ['DROPBOX_TOKEN']

dbx = dropbox.Dropbox(DROPBOX_TOKEN)


####################################
def upload_with_existence_checking(dbx, dropbox_folder, local_dir, subfolder, file_to_move):

    subdir = subfolder
    local_file_path = "/".join([local_dir, subdir, file_to_move])
    dbx_path =  "/".join([dropbox_folder, subfolder, file_to_move])
    print('Dropbox path:',    dbx_path)
    print('Local file path:', local_file_path)
    # check file exists in Dbx already
    if check_dbx_path(dbx, dbx_path):
        print dbx_path + "   found"
    else:
        print dbx_path + "   not found - uploading"
        upload(dbx, local_file_path, dbx_path)


####################################
def main():

    local_dir      = "/data01"
    dropbox_folder = "/raw_data"

    if not check_local_path(local_dir): exit(1)
    if not check_dbx_path (dbx, dropbox_folder): exit(1)

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