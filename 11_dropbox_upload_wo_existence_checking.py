#!/usr/bin/python


from  data_mgmt_utils_py.generic_utils import *
from  data_mgmt_utils_py.dropbox_utils import *


####################################
DROPBOX_TOKEN = os.environ['DROPBOX_TOKEN']
dbx = dropbox.Dropbox(DROPBOX_TOKEN)


####################################
def upload_no_existence_checking(dbx, dropbox_folder, local_dir, subfolder, file_to_move):

    subdir = subfolder
    local_file_path = "/".join([local_dir, subdir, file_to_move])
    dbx_path =  "/".join([dropbox_folder, subfolder, file_to_move])
    print dbx_path,  "uploading without existence check"
    upload (dbx, local_file_path, dbx_path, overwrite=True)

####################################
def main():

    local_dir      = "/data02"
    dropbox_folder = "/raw_data"

    if not check_local_path(local_dir): exit(1)
    if not check_dbx_path (dbx, dropbox_folder): exit(1)

    subdir = "2016/022"

    for dirpath, dirs, files in os.walk(local_dir + "/" + subdir):
        subfolder = dirpath[len(local_dir):].strip(os.path.sep)
        for file in files:
            if file[-10:] != "bedcov.csv": continue
            if file=='ARCHIVED': continue
            print subfolder, file
            upload_no_existence_checking(dbx, dropbox_folder, local_dir, subfolder, file)


####################################
if __name__ == '__main__':
    main()
