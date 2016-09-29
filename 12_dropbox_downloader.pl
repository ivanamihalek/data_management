#!/usr/bin/python


from  data_mgmt_utils_py.generic_utils import *
from  data_mgmt_utils_py.dropbox_utils import *


####################################
DROPBOX_TOKEN = os.environ['DROPBOX_TOKEN']

dbx = dropbox.Dropbox(DROPBOX_TOKEN)

####################################
def download_with_existence_checking(dbx, dbx_path, local_file_path):

    print 'Dropbox path:',    dbx_path 
    print 'Local file path:', local_file_path
    exit(1)
    # check file exists locally already
    if check_local_path(local_file_path):
        print local_file_path + "   found"
    else:
        print local_file_path + "   not found - downloading"   
        try:
            metadata, response = dbx.files_download_to_file (local_file_path, dbx_path)
        except dropbox.files.DownloadError as err:
            print('*** download  error', err)
            exit(1)
        print metadata
    exit(1)

####################################
def scan_through_folder (dbx, dropbox_folder, subfolder, local_dir):

    dbx_path =  "/".join([dropbox_folder, subfolder])

    try:
        response = dbx.files_list_folder(dbx_path, recursive = True)
    except dropbox.exceptions.ApiError as err:
        print('Folder listing failed for', path, '-- assumped empty:', err)
        exit(1)
    else:
        for entry in response.entries:
            if type(entry)!=dropbox.files.FileMetadata: continue
            print entry.name
            print entry.path_display
            dbx_path = entry.path_display
            local_path = dbx_path.replace(subfolder,local_dir)
            download_with_existence_checking(dbx, dbx_path, local_path)
            #exit(1)
 

####################################
def main():

    local_dir      = "/data01"
    dropbox_folder = "/raw_data"

    if not check_local_path(local_dir): exit(1)
    if not check_dbx_path (dbx, dropbox_folder): exit(1)

    subfolder = "2012/007"

    scan_through_folder(dbx, dropbox_folder, subfolder, local_dir)

####################################
if __name__ == '__main__':
    main()
