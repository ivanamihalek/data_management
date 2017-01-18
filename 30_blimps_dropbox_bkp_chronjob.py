#!/usr/bin/python

import os
from  sys import argv
from  data_mgmt_utils_py.dropbox_utils import *
import subprocess
import time

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
def main():

    backup_schedule = "daily"
    if len(sys.argv) > 1:
        if sys.argv[1] == "monthly": backup_schedule ="monthly"
        elif sys.argv[1] == "annual": backup_schedule ="annual"
    print backup_schedule

    sql_dump_location = "/tmp/blimps_production.sql"
    dropbox_folder    = "/blimps_backup"


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
    upload (dbx, compressed_db, dbx_path)
    # if chronjob is daily remove from Dropbox everyting older than 3 days
    # if monthly, remove older than 6 monthc
    # if yearly, keep all
    ####################################



####################################
if __name__ == '__main__':
    main()
