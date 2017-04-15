#!/usr/bin/python

import sys
from os import listdir
import subprocess

from  data_mgmt_utils_py.generic_utils import *
from  data_mgmt_utils_py.mysqldb import *

###################################
VARIANTYX_HOSTNAME = "variantyxinc.sharefileftp.com"
VARIANTYX_TOKEN = os.environ['VARIANTYX_TOKEN']
VARAINTYX_PASS = os.environ['VARIANTYX_PASS']


####################################
def get_family_info(case_boid):
	info = {}
	db = connect_to_mysql()
	cursor = db.cursor()
	switch_to_db(cursor, 'blimps_production')
	qry = 'select i.boid, i.gender, i.relationship, c.affected  from individuals as i, clinical_data as c '
	qry += 'where i.boid like "%s%%" and i.id=c.individual_id ' % case_boid
	rows = search_db(cursor, qry)
	for row in rows:
		[boid, gender, relationship, affected] = row
		info[boid] = [gender, relationship, affected]
	cursor.close()
	db.close()
	return info


####################################
def find_bamfile(topdir, year, boid, alignment_preference):
	bamfile = None
	md5file = None
	caseno = boid[4:7]
	path = "/".join([topdir, year, caseno, boid])
	for root, dirs, files in os.walk(path):
		if not alignment_preference in root: continue
		for name in files:
			if name[-4:] != ".bam": continue
			bamfile = "/".join([root, name])
			md5file = "/".join([root + "/md5sums", name + ".md5"])
			if not os.path.isfile(md5file): md5file = None
			break
		if bamfile: break
	return [bamfile, md5file]


####################################
def find_fqfiles(topdir, year, boid):
	fqfiles = []
	md5files = []
	caseno = boid[4:7]
	path = "/".join([topdir, year, caseno, boid])
	for root, dirs, files in os.walk(path):
		if not "reads" in root: continue
		for name in files:
			name_field = name.split(".")
			if len(name_field) < 2: continue
			if (name_field[-1] in ["fq", "fastq"]) \
					or (name_field[-2] in ["fq", "fastq"] and name_field[-1] in ["gz", "zip", "bz2"]):
				fqfile = "/".join([root, name])
				md5file = "/".join([root + "/md5sums", name + ".md5"])
				fqfiles.append(fqfile)
				if os.path.isfile(md5file): md5files.append(md5file)
	if len(fqfiles) > 0:
		return [fqfiles, md5files]

	return [None, None]


####################################
def output_csv(case_boid, family_info):
	csv_name = case_boid + ".csv"
	outf = open(case_boid + ".csv", "w")
	# first value in the hash is an info list, we want its length, - first three elements
	header_names = ["case_id", "relationship", "affected"] + \
				   ["md5_checksum", "file_name"] * (len(family_info.itervalues().next()) - 3)
	print >> outf, "\t".join(header_names)
	for boid, info in family_info.iteritems():
		print >> outf, "\t".join([case_boid] + [str(d).split("/")[-1] for d in info])
	outf.close()
	return csv_name


####################################
def md5check(bamfile, md5file):
	f = open(md5file, "r")
	md5sum = f.readline().rstrip()
	f.close()
	# check the md5sum
	p = subprocess.Popen(['md5sum', bamfile], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	out, err = p.communicate()
	checkmd5 = out.split(' ')[0]
	if md5sum == checkmd5:
		print "md5sum checks"
		return md5sum
	else:
		print "md5sum check failed: "
		print "in", md5file, md5sum
		print "recalculated:", checkmd5
		exit(1)
	return None


####################################
def output_upload_script(case_boid, family_info):

	script_name = case_boid + ".upload.lftp"
	outf = open(script_name, "w")
	# to be run with
	# lftp -f  script_name

	outf.write("open -u %s,%s  %s\n" % (VARIANTYX_TOKEN, VARAINTYX_PASS, VARIANTYX_HOSTNAME))
	outf.write("cd Boston_Childrens_Dr_Bodamer\n")
	outf.write("mkdir %s\n" % case_boid)
	outf.write("cd %s\n" % case_boid)
	# meta file
	outf.write("put %s.csv\n" % case_boid)
	for boid, info in family_info.iteritems():
		for i in range(4,len(info),2):
			fqfile_path = info[i]
			fqfile_name = fqfile_path.split("/")[-1]
			outf.write("put %s\n" % fqfile_name)
	outf.close()

	return script_name

####################################
def main():
	if len(sys.argv) < 3:
		print  "usage: %s <case BOid> <seqmule/seq_center> " % sys.argv[0]
		exit(1)

	[case_boid, alignment_preference] = sys.argv[1:3]
	print case_boid, alignment_preference
	# connect to blimps
	# find info about the family on blips
	family_info = get_family_info(case_boid)
	print family_info

	# find file in the directory structure
	year = "20" + case_boid[2:4]
	for boid in family_info.keys():
		[fqfiles, bamfile] = [None, None]
		for topdir in ['/data01', '/data02']:
			if not year in listdir(topdir): continue
			print  topdir, year
			[fqfiles, md5files] = find_fqfiles(topdir, year, boid)
			if not fqfiles:
				[bamfile, md5file] = find_bamfile(topdir, year, boid, alignment_preference)
			break
		if not fqfiles and not bamfile:
			print "neither fq file(s) nor bamfile not found for", boid
			print " ... removing ..."
			del family_info[boid]
			continue
		if fqfiles:
			if not md5files or not len(fqfiles) == len(md5files):
				print "not all md5files found for fqfiles for", boid
				exit(1)
			for i in range(len(fqfiles)):
				print fqfiles[i]
				print md5files[i]
				md5sum = md5check(fqfiles[i], md5files[i])  # will die here if it doesn't check
				# add file name and md5sum info to family info table
				family_info[boid].append(md5sum)
				family_info[boid].append(fqfiles[i])

		elif bamfile:
			if not md5file:
				print "md5file not found for mdfile for", boid
				exit(1)
			print bamfile
			print md5file
			md5sum = md5check(bamfile, md5file)  # will die here if it doesn't check
			# add file name and md5sum info to family info table
			family_info[boid].append(md5sum)
			family_info[boid].append(bamfile)

	# output/save  family info table to csv file
	csv_name = output_csv(case_boid, family_info)
	# run lftp through script that we are going to prepare here
	script_name = output_upload_script(case_boid, family_info)
	# run with
	# lftp -f script_name

	print "to login and check, see the top of %s" % script_name


####################################
if __name__ == '__main__':
	main()
