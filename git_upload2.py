#  #!/usr/bin/env python

#  git_upload.py - uploads file every X seconds, could be reworked to work with multiple files at once

#  Run script with: sudo python /your/file/location/git_upload.py

#  to schedule run at system startup run console nano crontab -e (set time interval within the code)
#  @reboot /usr/bin/python /home/git_upload.py

import os
import os.path
import shutil
import time
import datetime
from os import listdir, path
from os.path import isfile, join



   
    
initPath = "/home/pi/ultimate-raspistill-timelapse" # set your repository path

# git upload on img change
os.system("git add -A")
print("IMG - add")
os.system("git commit -m 'upload")
print("IMG - commit")
os.system("git push -u origin master")
print("IMG - Git push - file updated successfully!")
