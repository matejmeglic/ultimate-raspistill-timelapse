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

logCounter = 0

# indefinite loop  
while True:
   
    # IMG upload
    initPath = "/home/pi/tl_cam/public/img/" # set your repository path
    if path.isdir(initPath) is False :
        os.mkdir(initPath)
    onlyFiles = [f for f in listdir(initPath) if isfile(join(initPath, f))]

    if len(onlyFiles)>1 :
        # filter files to the most recent one (Based on date in the file name)
        while len(onlyFiles)>1 :         
            if onlyFiles[0] > onlyFiles[1] :
                os.system("rm "+initPath+onlyFiles[1])
                onlyFiles.remove(onlyFiles[1])
            else :
                os.system("rm "+initPath+onlyFiles[0])
                onlyFiles.remove(onlyFiles[0])
        # git upload on img change
        os.system("git add "+str(initPath))
        print("IMG - add")
        os.system("git commit -m 'upload "+onlyFiles[0]+"'")
        print("IMG - commit")
        os.system("git push -u origin master")
        print("IMG - Git push - file "+onlyFiles[0]+" updated successfully!")
    else :
        print("IMG - No changes - "+ str(len(onlyFiles)) +" image in the IMG folder!")
    
    # LOG upload
    initPathLogs = "/home/pi/tl_cam/public/logs/" # set your repository path
    if path.isdir(initPathLogs) is False :
        os.mkdir(initPathLogs)
    onlyFilesLogs = [f for f in listdir(initPathLogs) if isfile(join(initPathLogs, f))]

    # git upload on log change
    if len(onlyFilesLogs)>logCounter :
        os.system("git add "+initPathLogs)
        print("LOGS - add")
        os.system("git commit -m 'upload logs'")
        print("LOGS - commit")
        os.system("git push -u origin master")
        print("LOGS - Git push - logs updated successfully!")    
        logCounter = len(onlyFilesLogs)
    else :
        print("LOGS - No changes - "+ str(len(onlyFilesLogs)) +" logs in the LOG folder!")

    # set check interval
    time.sleep(10)