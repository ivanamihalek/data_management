#!/usr/bin/python

import os,sys
import pysftp
from os import listdir
import  subprocess 

from  data_mgmt_utils_py.generic_utils import *
from  data_mgmt_utils_py.mysqldb import *


###################################
CODIFED_HOSTNAME  = "216.230.226.115"
CODIFIED_ID    = os.environ['CODIFIED_ID']
CODIFIED_PASS  = os.environ['CODIFIED_PASS']

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
            bamfile  =  "/".join([root,name])
            md5file  =  "/".join([root+"/md5sums", name+".md5"])
            if not os.path.isfile(md5file): md5file = None
            break
       if bamfile: break
   return [bamfile, md5file]


####################################
def  output_csv(case_boid, family_info):
    csv_name = case_boid + ".csv"
    outf = open (case_boid + ".csv","w")
    print >>outf, "\t".join(["case id","relationship", "affected", "md5 checksum","file name"])
    for boid, info in family_info.iteritems():
        print >>outf, "\t".join( [case_boid] +  [str(d) for d in info[1:-1] ] + [ info[-1].split("/")[-1] ] )
    outf.close()
    return csv_name

####################################
def md5check (bamfile, md5file):
    
    f =  open (md5file, "r")
    md5sum = f.readline().rstrip()
    f.close()
    return md5sum
    # check the md5sum
    p = subprocess.Popen(['md5sum', bamfile], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    checkmdd5 =  out.split(' ')[0]
    if md5sum==checkmdd5:
        print "md5sum checks"
        return md5sum
    else:
        print "md5sum check failed: "
        print "in", md5file, md5sum
        print "recalculated:", chckmd5
        exit(1)
    return None

####################################
def main():

    if len(sys.argv) < 3:
        print  "usage: %s <case BOid> <seqmule/seqcenter> " % sys.argv[0]
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
        for topdir in ['/data01','/data02']:
            if not year in listdir(topdir): continue
            print  topdir, year
            [bamfile, md5file] = find_bamfile (topdir, year, boid, alignment_preference)
            break
        if not bamfile:
            print "bamfile not foud for", boid
            exit(1)
        if not md5file: 
            print "md5file not found  for", boid
            exit(1)
        print bamfile
        print md5file
        md5sum = md5check (bamfile, md5file) # will die here if it doesn't check
        # add file name and md5sum info to family info table
        family_info[boid].append(md5sum)
        family_info[boid].append(bamfile)

    
    # output/save  family info table to csv file
    csv_name = output_csv(case_boid, family_info)

    # establish sftp connection
    with pysftp.Connection(CODIFED_HOSTNAME, username=CODIFIED_ID, password=CODIFIED_PASS) as sftp:
        # check family folder exists
        print sftp.getcwd() 
    # upload the bam files - chek if exist
    # make family folder
    # upload alignment files and the info file in csv format
    #    with sftp.cd('public'):             # temporarily chdir to public
            #sftp.put('/my/local/filename')  # upload file to public/ on remote
            #sftp.get('remote_file')         # get a remote file

 
####################################
if __name__ == '__main__':
    main()
