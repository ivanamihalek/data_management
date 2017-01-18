#!/usr/bin/python

import os
from  sys import argv
import subprocess
from  data_mgmt_utils_py.generic_utils import *
from  data_mgmt_utils_py.dropbox_utils import *

####################################
DROPBOX_TOKEN = os.environ['DROPBOX_TOKEN']
dbx = dropbox.Dropbox(DROPBOX_TOKEN)

###############################
def main():

    backup_schedule = "daily"
    if len(sys.argv) > 1:
        if sys.argv[1] == "monthly": backup_schedule ="monthly"
        elif sys.argv[1] == "annual": backup_schedule ="annual"
    print backup_schedule

    sql_dump_location = "/tmp/blimps_dump.sql"
    dropbox_folder    = "/blimps_backup"

    # dump mysql using local credentials to /tmp/blimps_dump.sql
    cmd = ["mysqldump", "--login-path=cookiemonster", "blimps_development"]
    errlog = sql_dump_location+".stderr"
    try:
        exit_code = subprocess.call(cmd, stdout = open(sql_dump_location, "w"), stderr= open(errlog,"w"))
    except subprocess.CalledProcessError as e:
        print "got error from mysql:"
        print e.output
        exit(1)
    except OSError:
        print cmd[0], "not found, or something like that (OSError)"
        exit(1)
    if not exit_code == 0: #I don't understand why is subprocess.call not intercepting this ....
        print os.popen("cat "+errlog).read()
        exit(1)
    print "going to upload"
    #  upload current version to dropbox
    dbx_path = dropbox_folder+ "/" + backup_schedule
    upload (dbx, sql_dump_location, dbx_path)
    # if chronjob is daily remove from Dropbox everyting older than 3 days
    # if monthly, remove older than 6 monthc
    # if yearly, keep all
    ####################################



####################################
if __name__ == '__main__':
    main()
