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

def determine_folder_from_extension(filename, source):
	field = filename.split(".")
	if len(field)<2: return 'other'
	ext = field[-1]
	if ext in ['gz','bz2','zip']: ext=field[-2]
	if ext=='bam': return "alignments/by_%s" % source
	if ext in ['fastq','fq']: return 'reads'
	if ext=='vcf': return "variants/called_by_%s" % source
	return 'other'

#################################
def get_checksums (dbx, dbx_folder, scratch_dir, md5sum_file):

	md5sum_file =  dbx_folder + "/md5sums.txt"
	if not check_dbx_path (dbx, md5sum_file): return None

	checksum = {}
	local_md5sum_file = scratch_dir + "/md5sums.txt"
	download(dbx, local_md5sum_file, md5sum_file)
	chksm = open(local_md5sum_file,'r')
	for line in chksm:
		field = line.rstrip().split()
		if len(field)<2: continue
		checksum[field[1].split("/")[-1]] = field[0]
	return checksum

####################################
def main():
	# expect to find individual BOid somewhere on the path
	experiment = "wes"
	source = "seq_center"
	# for some reason the shit won't let me list the Lab folder
	# anything below it is ok
	dropbox_folder_from = "/colabs/FlemingLab/raw_data"
	dropbox_folder_to   = "/raw_data"
	scratch_dir        = "/home/ivana/scratch" # download md5 file here
	if not check_dbx_path (dbx, dropbox_folder_from): exit(1)
	if not check_dbx_path (dbx, dropbox_folder_to): exit(1)

	# will return None if the file is not there
	checksum = get_checksums(dbx, dropbox_folder_from, scratch_dir, "/md5sums.txt")

	paths = find_files_in_dbx_folder(dbx, dropbox_folder_from)
	for path in paths:
		full_path_elements = path.split("/")
		yci = False
		for element in full_path_elements:
			yci = check_if_ok_boid(element)
			if not yci: continue
			boid = element
			break
		if not yci: continue
		print "valid boid %s found in %s" % (boid,path)
		[year, case, individual] = yci
		filename = full_path_elements[-1]
		target_folder = determine_folder_from_extension(filename, source)
		if target_folder=='other':
			target_path = "/".join([dropbox_folder_to, year, case, 'other', boid])
		else:
			target_path = "/".join([dropbox_folder_to, year, case, boid, experiment, target_folder])
		print "copying to", target_path
		if not check_dbx_path (dbx, target_path): dbx.files_create_folder(target_path)
		target_file_path = 	target_path+"/"+filename
		if check_dbx_path (dbx, target_file_path):
			print "\t", target_file_path, "found"
		else:
			dbx.files_copy(path,target_file_path)
		# extract md5 and upload too
		if checksum and checksum.has_key(filename):
			print "storing checksum", checksum[filename]
			md5_fnm = scratch_dir+"/"+filename+".md5"
			outf = open(md5_fnm,"w")
			outf.write("%s\n"%checksum[filename])
			outf.close()
			md5sums_path = target_path+"/md5sums"
			if not check_dbx_path(dbx, md5sums_path): dbx.files_create_folder(md5sums_path)
			upload(dbx, md5_fnm, md5sums_path+"/"+filename+".md5", overwrite=True)



####################################
if __name__ == '__main__':
    main()