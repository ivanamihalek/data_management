#!/usr/bin/python

import os,sys
import pysftp

from  data_mgmt_utils_py.generic_utils import *
from  data_mgmt_utils_py.mysqldb import *


###################################
CODIFED_HOSTNAME  = "216.230.226.115"
CODIFIED_ID    = os.environ['CODIFIED_ID']
CODIFIED_TOKEN = os.environ['CODIFIED_PASS']

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
    # check md5 sums
    # add file name and md5sum info to family info table
    # output/save  family info table to csv file

    # upload the bam files - chek if exist
    # establish sftp connection
    # make family folder
    # upload alignment files and the info file in csv format
    #with pysftp.Connection(CODIFED_HOSTNAME, username=CODIFIED_ID, password=CODIFIED_PASS) as sftp:
    #    with sftp.cd('public'):             # temporarily chdir to public
            #sftp.put('/my/local/filename')  # upload file to public/ on remote
            #sftp.get('remote_file')         # get a remote file

 
####################################
if __name__ == '__main__':
    main()
