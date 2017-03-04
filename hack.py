#! /usr/bin/python


import os

####################################
def main():

	local_dir = "/data01"

	for dirpath, dirs, files in os.walk(local_dir + "/" + subdir):
		subfolder = dirpath[len(local_dir):].strip(os.path.sep)
		if not 'archived' in dirs: continue
		print dirpath, 'archived', subfolder

####################################
if __name__ == '__main__':
	main()
