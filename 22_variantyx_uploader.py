#!/usr/bin/python

import sys
import pysftp
from os import listdir
import  subprocess 

from  data_mgmt_utils_py.generic_utils import *
from  data_mgmt_utils_py.mysqldb import *


###################################
VARIANTYX_HOSTNAME = "variantyxinc.sharefileftp.com"
VARIANTYX_TOKEN    = os.environ['VARIANTYX_TOKEN']
VARAINTYX_PASS     = os.environ['VARIANTYX_PASS']

####################################
def get_family_info (case_boid):
    info  = {}
    db     = connect_to_mysql()
    cursor = db.cursor()
    switch_to_db (cursor, 'blimps_production')
    qry = 'select i.boid, i.gender, i.relationship, c.affected  from individuals as i, clinical_data as c '
    qry += 'where i.boid like "%s%%" and i.id=c.individual_id ' % case_boid 
    rows  = search_db (cursor, qry)
    for row in rows:
        [boid, gender, relationship, affected]  = row
        info [boid]  = [gender, relationship, affected]
    cursor.close()
    db.close()
    return info
    
####################################
def find_bamfile (topdir, year, boid, alignment_preference):
   bamfile = None
   md5file = None
   caseno = boid[4:7]
   path   = "/".join([topdir, year, caseno, boid])
   for root, dirs, files in os.walk(path):
       if not alignment_preference in root: continue
       for name in files:
            if name[-4:] != ".bam": continue
            bamfile = "/".join([root,name])
            md5file = "/".join([root+"/md5sums", name+".md5"])
            if not os.path.isfile(md5file): md5file = None
            break
       if bamfile: break
   return [bamfile, md5file]


####################################
def find_fqfiles (topdir, year, boid):
   fqfiles  = []
   md5files = []
   caseno = boid[4:7]
   path   = "/".join([topdir, year, caseno, boid])
   for root, dirs, files in os.walk(path):
       if not "reads" in root: continue
       for name in files:
            name_field = name.split(".")
            if  (name_field[-1]  in ["fq", "fastq"])\
                    or (name_field[-2]  in ["fq", "fastq"] and name_field[-1] in ["gz", "zip", "bz2"] ):
                fqfile  =  "/".join([root,name])
                md5file =  "/".join([root+"/md5sums", name+".md5"])
                fqfiles.append(fqfile)
                if  os.path.isfile(md5file): md5files.append(md5file)

   if len(fqfiles)>0:
     return [fqfiles, md5files]

   return [None, None]

####################################
def  output_csv(case_boid, family_info):
    csv_name = case_boid + ".csv"
    outf = open (case_boid + ".csv","w")
    print >>outf, "\t".join(["case id","relationship", "affected", "md5 checksum","file name"])
    for boid, info in family_info.iteritems():
        print >>outf, "\t".join( [case_boid] + [str(d) for d in info[1:-1]] + [info[-1].split("/")[-1]] )
    outf.close()
    return csv_name

####################################
def md5check (bamfile, md5file):
    
    f =  open (md5file, "r")
    md5sum = f.readline().rstrip()
    f.close()
    # check the md5sum
    p = subprocess.Popen(['md5sum', bamfile], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    checkmd5 =  out.split(' ')[0]
    if md5sum==checkmd5:
        print "md5sum checks"
        return md5sum
    else:
        print "md5sum check failed: "
        print "in", md5file, md5sum
        print "recalculated:", checkmd5
        exit(1)
    return None

####################################
def main():

    if len(sys.argv) < 3:
        print  "usage: %s <case BOid> <seqmule/seq_center> " % sys.argv[0]
        exit(1)

    [case_boid, alignment_preference]  = sys.argv[1:3]
    print case_boid, alignment_preference
    # connect to blimps
    # find info about the family on blips
    family_info = get_family_info(case_boid)
    print family_info

    # find file in the directory structure
    year = "20"+case_boid[2:4]
    for boid in family_info.keys():
        [fqfiles, bamfile] = [None, None]
        for topdir in ['/data01','/data02']:
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
            if not md5files or not len(fqfiles)==len(md5files):
                print "not all md5files found for fqfiles for", boid
                exit(1)
            for i in range(fqfiles):
                print fqfiles[i]
                print md5files[i]
                md5sum = md5check (fqfiles[i], md5files[i]) # will die here if it doesn't check
                # add file name and md5sum info to family info table
                family_info[boid].append(md5sum)
                family_info[boid].append(fqfiles[i])

        elif bamfile:
            if not md5file:
                print "md5file not found for mdfile for", boid
                exit(1)
            print bamfile
            print md5file
            md5sum = md5check (bamfile, md5file) # will die here if it doesn't check
            # add file name and md5sum info to family info table
            family_info[boid].append(md5sum)
            family_info[boid].append(bamfile)

    
    # output/save  family info table to csv file
    csv_name = output_csv(case_boid, family_info)
    exit()

	# output script
	# the script itself contains credentials
	# then pipe the script inot lftp
	# example test.script
	#
	# open -u <token>,<pass> variantyxinc.sharefileftp.com
	# cd Boston_Childrens_Dr_Bodamer
	# mkdir testdir
	# cd testdir
	# put /home/ivana/scratch/hello.txt
	#
	# to be run with
	# lftp -f  test.script



    # establish sftp connection
    with pysftp.Connection(VARIANTYX_HOSTNAME, username=VARIANTYX_ID, password=VARIANTYX_PASS) as sftp:
        print sftp.pwd
        # check family folder exists
        if sftp.exists(case_boid):
            print "\t %s found" % case_boid
        else:
            # make family folder
            sftp.mkdir(case_boid)
        # move to family dir
        sftp.chdir(case_boid)
        print sftp.pwd
        #for each bmfile
        for boid, info in family_info.iteritems():
            bamfile_path = info[-1]
            bamfile_name = bamfile_path.split("/")[-1]
            # check exists
            if sftp.exists(bamfile_name):
                print "\t %s found" % bamfile_name
            else:
                # upload if it  does not
                print "\t uploading %s " % bamfile_name
                sftp.put(bamfile_path)
            
        # upload alignment files and the info file in csv format
        if sftp.exists(csv_name):
            print "\t %s found" % csv_name
        else:
            # upload if it  does not
            print "\t uploading %s " % csv_name
            sftp.put(csv_name)
            
        sftp.close()
 
 
####################################
if __name__ == '__main__':
    main()
