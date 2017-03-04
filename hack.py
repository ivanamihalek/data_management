#! /usr/bin/python


import os

####################################
def main():

	local_dir = "/data01"

	for dirpath, dirs, files in os.walk(local_dir):
		if not 'archived' in dirs: continue
		print dirpath, 'archived'
		os.system("rm -rf %s/archived/archived  " % dirpath)
		os.system("ls %s/archived > %s/ARCHIVED " % (dirpath, dirpath))
		exit()

####################################
if __name__ == '__main__':
	main()
