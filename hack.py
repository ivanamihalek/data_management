#! /usr/bin/python


import os

####################################
def main():

	local_dir = "/data01"

	for dirpath, dirs, files in os.walk(local_dir):
		if not 'archived' in dirs: continue
		print dirpath, 'archived'
		os.system("ls %s/archived > %s/RCHIVED " % (dirpath, dirpath))
		exit()

####################################
if __name__ == '__main__':
	main()
