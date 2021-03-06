#!/usr/bin/python

import os

from  data_mgmt_utils_py.generic_utils import *
from  data_mgmt_utils_py.dropbox_utils import *


from  data_mgmt_utils_py.generic_utils import *
from  data_mgmt_utils_py.mysqldb import *

####################################
DROPBOX_TOKEN = os.environ['DROPBOX_TOKEN']

dbx = dropbox.Dropbox(DROPBOX_TOKEN)

def extension_checks(filename):
    for ext in ["bam", "fastq", "fastq.bz2", "fastq.gz"]:
        if len(filename)>len(ext) and filename[-len(ext):]==ext: return ext
    return False

####################################
def scan_through_folder (dbx, dropbox_folder, subfolder):
    boids = []
    fastqs = {}
    bams   = {}
    dbx_path = "/".join([dropbox_folder, subfolder])
    try:
        response = dbx.files_list_folder(dbx_path, recursive = True)
    except dropbox.exceptions.ApiError as err:
        print('Folder listing failed for', dbx_path, '-- assumed empty:', err)
        exit(1)
    else:
        #print " ** ", response
        for entry in response.entries:
            if type(entry)!=dropbox.files.FileMetadata: continue
            if not "reads" in entry.path_display and not "alignments/by_seq_center" in entry.path_display: continue
            ext = extension_checks(entry.name)
            if not ext: continue
            field =  entry.path_display.split("/")
            boid = field[4]
            file = field[-1]
            if not boid in boids: boids.append(boid)
            if "bam" in ext:
                if not  bams.has_key(boid): bams[boid] = []
                bams[boid].append(entry.path_display)
            elif "fastq" in ext:
                if not  fastqs.has_key(boid): fastqs[boid] = []
                fastqs[boid].append(entry.path_display)
            #dbx_path = entry.path_display
            #local_path = dbx_path.replace(dropbox_folder,local_dir)
    return boids, fastqs, bams

####################################
def main():

    dropbox_folder = "/raw_data"
    if not check_dbx_path (dbx, dropbox_folder): exit(1)

    db     = connect_to_mysql()
    cursor = db.cursor()
    switch_to_db (cursor, 'blimps_production')

    headers = ["sample number", "source name", "consent version", "gender", "family number", "family structure", "affected"]
    print "\t".join(headers)
    line_count = 0
    family_number = 0
    old_family_id = ""
    for subfolder in ["2011","2012","2013","2014","2015","2016","2017"]:
    #for subfolder in ["2015"]:
        #print " *************** ", subfolder, " ****************** "
        boids, fastqs, bams = scan_through_folder(dbx, dropbox_folder, subfolder)
        for boid in sorted(boids):
            if not fastqs.has_key(boid) and not bams.has_key(boid): continue

            qry = 'select i.boid, i.gender, i.relationship, c.affected, x.xref from individuals as i, clinical_data as c, identifiers as x '
            qry += 'where i.boid="%s" and c.individual_id=i.id and x.name="%s" ' % (boid, boid)
            rows  = search_db (cursor, qry)
            if not rows: continue
                #print qry
                #exit(1)
            [boid, gender, relationship, affected, xrefs] = [""]*5
            for row in rows:
                [boid, gender, relationship, affected, xrefs]  = row
                mants = ""
                if xrefs:
                     allx = xrefs.split(";")
                     mants = ";".join([x for x in allx if 'manton' in x.lower()])

            line_count += 1
            family_id = boid[:-2]
            if old_family_id != family_id:
                old_family_id = family_id
                family_number += 1
            out_list = []
            out_list.append(str(line_count))
            out_list.append(boid)
            out_list.append(mants)
            out_list.append(gender)
            out_list.append(str(family_number))
            out_list.append(relationship)
            if affected == 1:
                out_list.append("affected")
            else:
                out_list.append("unaffected")
            if fastqs.has_key(boid): out_list += fastqs[boid]
            if bams.has_key(boid): out_list += bams[boid]

            print "\t".join(out_list)

####################################
if __name__ == '__main__':
    main()
