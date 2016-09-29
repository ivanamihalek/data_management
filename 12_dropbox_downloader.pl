#!/usr/bin/python


from  data_mgmt_utils_py.generic_utils import *
from  data_mgmt_utils_py.dropbox_utils import *


####################################
DROPBOX_TOKEN = os.environ['DROPBOX_TOKEN']

dbx = dropbox.Dropbox(DROPBOX_TOKEN)


####################################
def list_folder(dbx, folder, subfolder):
    """List a folder.
    Return a dict mapping unicode filenames to
    FileMetadata|FolderMetadata entries.
    """
    path = '/%s/%s' % (folder, subfolder.replace(os.path.sep, '/'))
    while '//' in path:
        path = path.replace('//', '/')
    path = path.rstrip('/')
    try:
        res = dbx.files_list_folder(path)
    except dropbox.exceptions.ApiError as err:
        print('Folder listing failed for', path, '-- assumped empty:', err)
        return {}
    else:
        rv = {}
        for entry in res.entries:
            rv[entry.name] = entry
            print entry.name
        return rv

####################################
def main():

    local_dir      = "/data01"
    dropbox_folder = "/raw_data"

    if not check_local_path(local_dir): exit(1)
    if not check_dbx_path (dbx, dropbox_folder): exit(1)

    subfolder = "2012/007"

    list_folder(dbx, dropbox_folder, subfolder)

####################################
if __name__ == '__main__':
    main()
