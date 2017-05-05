#!/usr/bin/python


import os

from  data_mgmt_utils_py.generic_utils import *
from  data_mgmt_utils_py.dropbox_utils import *


import dropbox

####################################
DROPBOX_TOKEN = os.environ['DROPBOX_TOKEN']

dbx = dropbox.Dropbox(DROPBOX_TOKEN)

####################################
def find_files_in_dbx_folder(dbx, dropbox_folder):

	paths = []
	try:
		response = dbx.files_list_folder(dropbox_folder, recursive = True)
	except dropbox.exceptions.ApiError as err:
		print('Fetching folder metadata failed for', dbx_path, '-- assumped empty:', err)
		exit(1)
	else:
		for entry in response.entries:
			if type(entry) != dropbox.files.FileMetadata: continue
			paths.append(entry.path_display)

	return paths

####################################
def check_if_ok_boid(element):
	if element[:2]!="BO": return False
	yr = int(element[2:4])
	if yr<11 or yr>20: return False
	year = "20"+str(yr)
	case    = element[4:7]
	individual = element[7:9]
	if not individual[0] in ['1','2', '3']: return False
	return [year, case, individual]

####################################
def main():
	# expect to find individual BOid somewhere on the path
	experiment = "wes"
	# for some reason the shit won't let me list the Lab folder
	# anything below it is ok
	dropbox_folder_from = "/colabs/FlemingLab/raw_data"
	dropbox_folder_to   = "/raw_data"
	scratch_path        = "/home/ivana/scratch" # download md5 file here
	if not check_dbx_path (dbx, dropbox_folder_from): exit(1)
	if not check_dbx_path (dbx, dropbox_folder_to): exit(1)

	md5sum_file =  dropbox_folder_from + "/md5sums.txt"
	md5sum_file_exist = check_dbx_path (dbx, md5sum_file)

	if md5sum_file_exist: download(dbx, scratch_path+ "/md5sums.txt", md5sum_file)

	paths = find_files_in_dbx_folder(dbx, dropbox_folder_from)
	for path in paths:
		full_path_elements = path.split("/")
		yci = False
		for element in full_path_elements:
			yci = check_if_ok_boid(element)
			if yci:
				boid = element
				break
		if not yci: continue
		print "valid boid %s found in %s" % (boid,path)
		[year, case, individual] = yci
		filename = full_path_elements[-1]
		target_folder = determine_folder_from_extension(filename)
		target_path = "/".join([dropbox_folder_to, year, case, boid, experiment, target_folder])
		print "copying to", target_path
		# dbx.files_copy(from_path, to_path, allow_shared_folder=False, autorename=False)
		# extract md5 and upload too

####################################
if __name__ == '__main__':
    main()