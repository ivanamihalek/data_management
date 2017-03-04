#!/usr/bin/python


import dropbox, os
DROPBOX_TOKEN = os.environ['DROPBOX_TOKEN']

dbx = dropbox.Dropbox(DROPBOX_TOKEN)

try:
    metadata, res = dbx.files_download(path='/some_nonexistent_crap')
except dropbox.exceptions.ApiError as err:
    print "Download failure:", err
    print "Not sure what that means, so I'll exit."
