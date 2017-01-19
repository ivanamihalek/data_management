#!/usr/bin/python

import os
from  sys import argv
from  data_mgmt_utils_py.dropbox_utils import *
import subprocess
import time
from datetime import datetime, timedelta

####################################
DROPBOX_TOKEN = os.environ['DROPBOX_TOKEN']
dbx = dropbox.Dropbox(DROPBOX_TOKEN)


###############################
def dump_database(login_path, database, sql_dump_location):
    cmd = ["mysqldump", "--login-path=" + login_path, database]
    errlog = sql_dump_location + ".stderr"
    try:
        exit_code = subprocess.call(cmd, stdout=open(sql_dump_location, "w"), stderr=open(errlog, "w"))
    except subprocess.CalledProcessError as e:
        print "got error from mysql:"
        print e.output
        exit(1)
    except OSError:
        print cmd[0], "not found, or something like that (OSError)"
        exit(1)
    if not exit_code == 0:  # I don't understand why is subprocess.call not intercepting this ....
        print os.popen("cat " + errlog).read()
        exit(1)

###############################
def compress_database(sql_dump_location):
    cmd = ["gzip", "-f", sql_dump_location]
    try:
        exit_code = subprocess.call(cmd)
    except subprocess.CalledProcessError as e:
        print "got error from mysql:"
        print e.output
        exit(1)
    except OSError:
        print cmd[0], "not found, or something like that (OSError)"
        exit(1)
    if not exit_code == 0:  # I don't understand why is subprocess.call not intercepting this ....
        print "error gzipping"
        exit(1)
    return sql_dump_location+".gz"

###############################
def remove_old(dropbox_folder, backup_schedule):
    if backup_schedule=="annual": return

    if backup_schedule=="daily":
        cutoff_date = datetime.now() - timedelta(days=5)
    elif  backup_schedule=="monthly":
        cutoff_date = datetime.now() - timedelta(months=6)
    else:
        return
    dbx_path =  "/".join([dropbox_folder, backup_schedule])

    try:
        response = dbx.files_list_folder(dbx_path, recursive = True)
    except dropbox.exceptions.ApiError as err:
        print('Folder listing failed for', path, '-- assumped empty:', err)
        return # don't delete anything if unsure

    for entry in response.entries:
        if type(entry)!=dropbox.files.FileMetadata: continue
        #print entry.name
        #print entry.path_display
        #print entry.client_modified
        if entry.client_modified < cutoff_date:
            print "deleting %s" % entry.client_modified
            dbx.files_delete(entry.path_display)

###############################
def main():

    backup_schedule = "daily"
    if len(sys.argv) > 1:
        if sys.argv[1] == "monthly": backup_schedule ="monthly"
        elif sys.argv[1] == "annual": backup_schedule ="annual"
    print "backup schedule: %s" % backup_schedule

    sql_dump_location = "/tmp/blimps_production.sql"
    dropbox_folder    = "/blimps_backup"
    remove_old(dropbox_folder, backup_schedule)
    exit(1)

    # dump mysql using local credentials to /tmp/blimps_dump.sql
    hostname = os.popen("hostname").read().rstrip()
    if hostname=='pegasus':
        dump_database(login_path="cookiemonster", database="blimps_development", sql_dump_location=sql_dump_location)
    else:
        dump_database(login_path="blimps", database="blimps_production", sql_dump_location=sql_dump_location)
    compressed_db = compress_database(sql_dump_location)

    #  upload current version to dropbox
    zip_ext = compressed_db.split(".").pop()
    dbx_path = "/".join([dropbox_folder, backup_schedule, ".".join(["blimps_production", time.strftime("%Y%b%d"), "sql", zip_ext]) ])
    print "Uploading from %s to %s" % (compressed_db, dbx_path)
    #upload (dbx, compressed_db, dbx_path)
    # if chronjob is daily remove from Dropbox everyting older than 3 days
    # if monthly, remove older than 6 months
    # if yearly, keep all
    remove_old(dropbox_folder, backup_schedule)
    ####################################



####################################
if __name__ == '__main__':
    main()
