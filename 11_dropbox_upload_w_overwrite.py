#!/usr/bin/python


from  data_mgmt_utils_py.generic_utils import *
from  data_mgmt_utils_py.dropbox_utils import *


####################################
DROPBOX_TOKEN = os.environ['DROPBOX_TOKEN']
dbx = dropbox.Dropbox(DROPBOX_TOKEN)


####################################
def upload_w_overwrite(dbx, dropbox_folder, local_dir, subfolder, file_to_move):

	subdir = subfolder
	local_file_path = "/".join([local_dir, subdir, file_to_move])
	dbx_path =  "/".join([dropbox_folder, subfolder, file_to_move])
	print dbx_path,  "uploading with overwrite"
	if check_dbx_path(dbx, dbx_path):
		dbx.files_delete(dbx_path) # I cannot get the overwrite mode to work
	upload (dbx, local_file_path, dbx_path, overwrite=True)



####################################
def main():

	if len(sys.argv) < 4:
		print  "usage: %s <local dir (ex /data01)> <subdir (ex: 2016/022)>  <extensions> ..." % sys.argv[0]
		exit(1)

	local_dir  = sys.argv[1]
	print local_dir
	subdir = sys.argv[2]
	print subdir
	extensions = [x.rstrip() for x in sys.argv[3:]]

	print local_dir, subdir, extensions

	dropbox_folder = "/raw_data"

	if not check_local_path(local_dir): exit(1)
	if not check_dbx_path (dbx, dropbox_folder): exit(1)

	print local_dir

	for dirpath, dirs, files in os.walk(local_dir + "/" + subdir):
		subfolder = dirpath[len(local_dir):].strip(os.path.sep)
		print subfolder, files
		for file in files:
			if file=='ARCHIVED': continue
			print file
			for extension in extensions:
				if file[-len (extension):] == extension:
					print subfolder, file
					upload_w_overwrite(dbx, dropbox_folder, local_dir, subfolder, file)


####################################
if __name__ == '__main__':
	main()
