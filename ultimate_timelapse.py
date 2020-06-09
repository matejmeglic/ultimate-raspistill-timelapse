#!/usr/bin/env python3

#  raspiLapseCam.py
#  Created by James Moore on 28/07/2013.
#  Modified by James Moore on 13/11/2013.
#  Copyright (c) 2013 Fotosyn. All rights reserved.

#  ultimate_timelapse.py based on raspiLapseCam.py
#  Modified by Matej Meglic 05/05/2020.
#  Modification Copiright (c) 2020 Matej Meglic s.p. All rights reserved.
#
#  Raspberry Pi is a trademark of the Raspberry Pi Foundation.

#  Redistribution and use in source and binary forms, with or without
#  modification, are permitted provided that the following conditions are met:

#  1. Redistributions of source code must retain the above copyright notice, this
#  list of conditions and the following disclaimer.
#  2. Redistributions in binary form must reproduce the above copyright notice,
#  this list of conditions and the following disclaimer in the documentation
#  and/or other materials provided with the distribution.>

#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
#  ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
#  WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
#  DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
#  ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
#  (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
#  LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
#  ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
#  (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
#  SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

#  The views and conclusions contained in the software and documentation are those
#  of the authors and should not be interpreted as representing official policies,
#  either expressed or implied, of the FreeBSD Project.

#  This script (2013) was originally set up to runs a Python Script which, at specified intervals invokes a capture
#  command to the Raspberry Pi camera, and stores those files locally in a dynamically named folder.
#  Original script can be found at http://fotosyn.com/blog/simple-timelapse-camera-using-raspberry-pi-and-a-coffee-tin

#  Extension (2020): It is known that original raspistill shell timelapse feature cannot save images with filenames
#  set as date or datetime,therefore, new script was developed in pyhon to overcome these obstacles.
#  If set correctly (cronjob), this script can boot itself up after power is provided and start
#  capture images in given interval (anything from 0-24 will do, but it can't run overnight in current state).
#  Capture can be perpetual as folder generate separately every day at midnight system time.
#  After capturing session is finished (author aimed at 14h/d capture), post-capture processes take place,
#  such as 1) automatic creation of timelapse video, 2) automatic upload to youtube, 3) automatic resizing of the
#  images, 4) automatic move of folder from systemSD to externalHDD and 5) log extraction.
#  Author originally intender to use this camera live on a dynamically built website (React+GitHub+Netlify) so this
#  code sends every n-th image to the github repo and is uploaded with another accompanying script. For serious usage,
#  rebuilding the code to another data storage provider is advised. Git upload can be turned off in the config.
#  Define the location where you wish to save files (initPath in config)
#  If you run a local web server on Apache you could set this to /var/www/ to make them
#  accessible via web browser or use my idea of feeding last image to github repo

#  Building blocks (prerequisites):
#  https://bitbucket.org/fotosyn/fotosynlabs/src/9819edca892700e459b828517bba82b0984c82e4/RaspiLapseCam/raspiLapseCam.py?at=master <--original repo
#  https://github.com/tokland/youtube-upload  <-- prerequisite for yt upload
#  https://www.raspberrypi.org/documentation/usage/camera/raspicam/raspistill.md <-- raspistill documentation
#  https://www.raspberrypi.org/documentation/raspbian/applications/camera.md <-- raspistill documentation mode
#  https://youtu.be/5OFnqLuYZy8?t=660 <-- fstab hdd configuration
#  Python 3.x, pip3 for python, other pip and apt-get installations needed (like checksumdir)

#  When setting up the environment for this script, please refer to prereq repos stated above for troubleshooting (GH issues are key)

#  Attached are three scripts:
#  1) git_upload.py - uploads file every X seconds, could be reworked to keep multiple files online at once
#  2) raspishot.sh - is intended to fully customize your camera manual settings to get best results (auto wb was brown [not-correct] in my case)
#  3) ultimate_timelapse.py - actual timelapse script

#  Run script with: sudo python /your/file/location/ultimate_timelapse.py

#  to schedule run at system startup run console nano crontab -e (set time interval within the code)
#  @reboot sleep 60 && eval `ssh-agent -s` && ssh-add ~/.ssh/id_rsa && ssh-add -l && cd /home/pi/ultimate-raspistill-timelapse && sudo -u pi python /home/pi/ultimate-raspistill-timelapse/git_upload.py > /home/pi/git-notes.txt 2>&1
#  @reboot /usr/bin/python /home/pi/ultimate_timelapse.py

# Import section
import re
import os
import os.path
import time
import logging
import datetime
import subprocess
import glob
import os.path
from os import path
import time
import datetime
import subprocess
import shutil
from checksumdir import dirhash
import logging
import logging.handlers

# Grab the current datetime which will be used to generate dynamic folder names
d = datetime.datetime.now()
initYear = "%04d" % (d.year)
initMonth = "%02d" % (d.month)
initDate = "%02d" % (d.day)
initHour = "%02d" % (d.hour)
initMins = "%02d" % (d.minute)

# config (change to your preference)
# capture settings
captureHourStart = 0 # start of the capture
captureHourEnd = 50 # finish the capture
delayBetweenImages = 25 # Wait x+5 seconds before next capture (+5.5 sec goes because raspistill workflow for focusing, taking and saving a shot takes 5-5.5sec)
# IMG settings
imgWidth = 3280 # Max = 3280
imgHeight = 2464 # Max = 2464
imgParameters = "-sh 100 -q 100 -v -vf -hf -ev -4 -awb off -awbg 1.6,1.7 -mm average -n" #raspistill parameters, configure
# post-capture automation switches
createMovie = False # settings for different processes to run after timelapse is completed
uploadToYoutube = False
compression = False
backupToHDD = True
logExport = True
# storage settings (file name is defined later in the code)
initPath = "/home/pi/camera/" # init path for folder generation
initFolderName= str(initYear) + str(initMonth) + str(initDate) +"_"+ str(initHour) + str(initMins) # folder name generated, file name is generated later as it needs to be generated per image taken
# automation configs
tlVideoExportPath = "export" # subfolder to store full-res timelapse !! caution, do not use closing / as ffmpeg building timelapse video will not work
exportFileName = str(initYear) + str(initMonth) + str(initDate) # additional logic for avoiding duplication in the code
exportFileName4k = str(initYear) + str(initMonth) + str(initDate)+"_4k"
backupHDDPath = "/home/pi/backupaa" # use sudo nano /etc/fstab to define mounting point for your HDD
# youtube configs
youtubeClientSecretsPath = "/home/pi/cs.json" # yt client secrets file path
youtubePlaylistTitle = "timelapse" # yt playlist name (playlist has to be created manually in youtube ahead of capture)
# git upload configs
uploadToWeb = True # this switch controls uploading every x-th image to separate folder alongside with alltime image creation
wCounterRoll = 5 # how often a compressed picture is duplicated in github www repo (and in alltime folder)
imgWidthWeb = 1920 # Max = 3280 width and height of www repo image (smaller to decrease page loading time and file transfer)
imgHeightWeb = 1442 # Max = 2464
alltimePath = "www_alltime" # subfolder to store full-res pictures that were sent to www repo
pathLogsW = "/home/pi/ku_tl_cam/public/logs" # logs in github repo
pathImgW = "/home/pi/ku_tl_cam/public/img" # last image in github repo

# DON'T CHANGE: inits for different processes to run after timelapse is completed
dateToday = datetime.date.today() # for running timelapse for multiple days (auto generating folders and log separation)
dateIsYesterday = datetime.date.today()
wCounter = 0
createMovieInit = 0
uploadToYoutubeInit = 0
compressionInit = 0
backupToHDDInit = 0
logExportInit = 0
delayPostprocess = 1 # timeout between post-capture actions
folderToSave =  os.path.join(initPath, initFolderName)


# calculating total size function (function called twice)
def get_size(start_path = str(folderToSave)):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path): # do not remove dirnames even if code editor returns error (to-do improvement to fix this)
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if not os.path.islink(fp):
                total_size += os.path.getsize(fp)

    return total_size

# create inital folder structure 
if path.isdir(str(initPath)) is False :
    os.mkdir(str(initPath))
if path.isdir(str(folderToSave)) is False :
    os.mkdir(str(folderToSave))

# Set up a system log file to store activities for any checks.
systemLogPath = str(initPath) + "SystemLog.log"
systemLog = logging.getLogger('Timelapse logging')
systemLog.setLevel(logging.DEBUG)
systemLog.addHandler(logging.handlers.RotatingFileHandler(systemLogPath))
systemLog.handlers[0].doRollover()

logStart = d.strftime("%y%m%d_%H%M%S")
systemLog.debug(" Ultimate RaspiLapse -- Started Log for " + str(folderToSave))
systemLog.debug(str(logStart))
systemLog.debug(" Logging session started at: "+ str(logStart))


# Run a WHILE Loop of infinitely
# This is where magic happens
while True:

    d = datetime.datetime.now()
    # this will reset folder and put a special tag in system log
    dateToday = datetime.date.today()
    if dateToday == dateIsYesterday:

# change if you want program to end on certain hour h-format (without leading zeroes).
# Hack: if you want indefinite loop type if d.hour < 99, but capture will not be separated
# into multiple folders plus post-capture automations will never run (for unlimited capture or capture when power-on I would refer to the original script)
# or modify config section captureHourStart and captureHourEnd if you want to run it between time range
# current settings doesn't allow 24-h or over-midnight timelapse capture (folder generation, system log etc.)

        captureElement = d.minute # for faster debug results you may change this to "minute"
        if captureElement >= captureHourStart and captureElement < captureHourEnd :

            # Capture the CURRENT time (not start time as set above) to insert into each capture image filename
            hour = "%02d" % (d.hour)
            mins = "%02d" % (d.minute)
            second = "%02d" % (d.second)
            # define file name
            fileName = str(initYear) + "-" + str(initMonth) + "-" + str(initDate) + "_" + str(hour) + "-" + str(mins) + "-" + str(second)

            print (" ====================================== Saving file at " + hour + ":" + mins + ":" + second)

            # if one doesn't want to upload to web, counter will be reset to never reach else part below
            if uploadToWeb == False :
                wCounter = 0

            # Capture the image using raspistill.
            if wCounter < wCounterRoll : # change wCounterRoll to 9 - every 10th image will have special action (duplicated to alltime folder and github repo)
                os.system("raspistill -w " + str(imgWidth) + " -h " + str(imgHeight) + " -o " + os.path.join(folderToSave,fileName)+".jpg "+ str(imgParameters))
                systemLog.debug(' Full-res image saved: ' + os.path.join(folderToSave,fileName) )
                wCounter += 1
                print("GIT Upload Counter: "+str(wCounter)+" / "+str(wCounterRoll))
            else :
                # same process as above (taking normal picture)
                os.system("raspistill -w " + str(imgWidth) + " -h " + str(imgHeight) + " -o " + os.path.join(folderToSave,fileName)+".jpg " + str(imgParameters))
                systemLog.debug(' Full-res image saved: ' + os.path.join(folderToSave,fileName) )
                # create webpage image_shot every 10-th image to /img (webpage will refresh image every 5min; calculate as wCount max number in if statement
                # x timeout between the picture x time to capture the picture as raspistill takes about 5.5 sec to take each picture)
                if path.isdir(pathImgW) is False :
                    os.mkdir(pathImgW)
                    systemLog.debug(' Folder created: '+str(pathImgW))
                # ffmpeg creates virtual copy in github repo
                os.system("ffmpeg -i "+os.path.join(folderToSave,fileName)+".jpg -vf scale="+str(imgWidthWeb)+":"+ str(imgHeightWeb)+" " + os.path.join(pathImgW,fileName)+".jpg -y")
                systemLog.debug(" Compressed image saved to www: "+os.path.join(pathImgW,fileName)+".jpg (UPDATED)" )
                # ffmpeg creates virtual (full-res) copy in /www_alltime folder (so you have easy access to all published photos)
                if path.isdir(os.path.join(folderToSave,alltimePath)) is False :
                    os.mkdir(os.path.join(folderToSave,alltimePath))
                    systemLog.debug(' Folder created: ' + os.path.join(folderToSave,alltimePath))
                os.system("ffmpeg -i "+os.path.join(folderToSave,fileName)+".jpg -vf scale="+str(imgWidth)+":"+ str(imgHeight) +" "+os.path.join(folderToSave,alltimePath,fileName)+".jpg -y")
                systemLog.debug(' Compressed image saved: ' + os.path.join(folderToSave,fileName))
                wCounter = 1
                print("GIT Upload Counter: "+str(wCounter)+" / "+str(wCounterRoll)+" Image queued for upload.")

        # Wait x+5 seconds before next capture (+5.5 sec goes because raspistill workflow for focusing, taking and saving a shot takes 5-5.5sec)
            time.sleep(delayBetweenImages)

        # initialize post-capture processes to only run after 1st timelapse section is completed
            if createMovie == True :
                createMovieInit = 1
            if uploadToYoutube == True :
                uploadToYoutubeInit = 1
            if compression == True :
                compressionInit = 1
            if backupToHDD == True :
                backupToHDDInit = 1
            if logExport == True :
                logExportInit = 1

        else:
            # after the working hours set above expire, program will proceed with additional actions (post-capture processes)
            # ffmpeg will create 1080p timelapse and store it in /export folder for youtube upload
            if createMovieInit == 1 :
                print (" ====================================== Sleeping ("+str(delayPostprocess)+")")
                time.sleep(delayPostprocess)
                print (" ====================================== Exporting .JPGs to FullHD timelapse")
                if path.isdir(os.path.join(folderToSave,tlVideoExportPath)) is False :
                    os.mkdir(os.path.join(folderToSave,tlVideoExportPath))
                    systemLog.debug(' FullHD Timelapse Folder created: ' + os.path.join(folderToSave,tlVideoExportPath))
                os.system("ffmpeg -framerate 30 -pattern_type glob -i '"+ os.path.join(folderToSave,"/*.jpg")+"' -vf scale=1080:810 -qscale 0 " + os.path.join(folderToSave,tlVideoExportPath,exportFileName,".mp4"))
                systemLog.debug(' FullHD Timelapse created: ' + os.path.join(folderToSave,tlVideoExportPath,exportFileName) )
                os.system("ffmpeg -framerate 30 -pattern_type glob -i '"+ os.path.join(folderToSave,"/*.jpg")+"' -qscale 0 " + os.path.join(folderToSave,tlVideoExportPath,exportFileName4k,".mp4"))
                systemLog.debug(' 4k Timelapse created: ' + os.path.join(folderToSave,tlVideoExportPath,exportFileName4k) )
                createMovieInit = 0
            # after timelapse video is finished, it will be uploaded to youtube automatically
            if uploadToYoutubeInit == 1 :
                print (" ====================================== Sleeping ("+str(delayPostprocess)+")")
                time.sleep(delayPostprocess)
                print (" ====================================== Uploading video to Youtube.com")
                os.system("/usr/local/bin/youtube-upload --title=" + str(fileName) + " --client-secrets="+ youtubeClientSecretsPath +" --playlist='"+youtubePlaylistTitle+"' --embeddable=True "+ os.path.join(folderToSave,tlVideoExportPath,exportFileName,".mp4"))
                systemLog.debug(' Video auto uploaded to youtube: ' + os.path.join(folderToSave,tlVideoExportPath,fileName) )
                uploadToYoutubeInit = 0

            # after upload is finish, all captured images will be resized automatically + logging folder total size of captured images
            if compressionInit == 1:
                print (" ====================================== Sleeping ("+str(delayPostprocess)+")")
                time.sleep(delayPostprocess)
                print (" ====================================== Compress all full-res files")
# function was here
                # logging part of resizing before compression (total size)
                path, dirs, files = next(os.walk(str(folderToSave)))
                fileCount = len(files)
                print(str(fileCount))
                systemLog.debug(' '+str(fileCount)+' photos recorded during the session. ')
                folderSizeGB = round(get_size()/1024/1024/1024,3)
                folderSizeMB = round(get_size()/1024/1024,1)
                print(str(folderSizeGB)+" GB / "+str(folderSizeMB)+" MB")
                systemLog.debug(' Total size before compression: ' +  str(folderSizeGB) + " GB / "+  str(folderSizeMB) + " MB")
                # compress each photo in the folder
                photos = os.listdir(str(folderToSave))
                for photo in photos:
                    os.system('ffmpeg -i '+str(folderToSave)+'/'+photo+' -vf scale=3280:2464 '+str(folderToSave)+'/'+photo+' -y')
                # logging total size after compress
                path, dirs, files = next(os.walk(str(folderToSave)))
                fileCount = len(files)
                print(str(fileCount))
                systemLog.debug(' '+str(fileCount)+' photos after compression.  ')
                folderSizeGB = round(get_size()/1024/1024/1024,3)
                folderSizeMB = round(get_size()/1024/1024,1)
                print(str(folderSizeGB)+" GB / "+str(folderSizeMB)+" MB")
                systemLog.debug(' Total size after compression: ' +  str(folderSizeGB) + " GB / "+  str(folderSizeMB) + " MB")
                compressionInit = 0

            if backupToHDDInit == 1 :
                print (" ====================================== Sleeping ("+str(delayPostprocess)+")")
                time.sleep(delayPostprocess)
                print (" ====================================== Moving files from SD-card to HDD backup")
                # move files from SDcard to backup HDD
                folderLoopInt = 1
                from os import path
                if path.isdir(folderToSave) is False :
                    print("Source folder doesn't exist - cannot copy to HDD!")
                else :
                    if path.isdir(os.path.join(backupHDDPath,initFolderName)) is False :
                        shutil.move(str(folderToSave),os.path.join(backupHDDPath,initFolderName))
                        systemLog.debug(" Files successfully moved to: "+os.path.join(backupHDDPath,initFolderName))
                        print("Files moved to backup HDD")
                    else :
                        print("Same named file exists on both locations - check")
                        systemLog.debug(" Same named file exists on both locations - performing md5 hash check")
                        hashSource = dirhash(str(folderToSave), 'md5')
                        hashHDD = dirhash(os.path.join(backupHDDPath,initFolderName),'md5')
                        print("Source hash: "+hashSource)
                        print("Source hash: "+hashHDD)
                        if hashSource == hashHDD :
                            print("Files already exist on HDD - move process stopped.")
                            systemLog.debug(" CHECK - md5 hash check is the same - content already copied to: "+os.path.join(backupHDDPath,initFolderName)+". Move wasn't performed.")
                        else :
                            while path.isdir(os.path.join(backupHDDPath,initFolderName)+"_"+str(folderLoopInt)) :
                                print("File "+os.path.join(backupHDDPath,initFolderName)+"_"+str(folderLoopInt)+" exists, try again.")
                                folderLoopInt+=1
                            else :
                                shutil.move(str(folderToSave), os.path.join(backupHDDPath,initFolderName)+"_"+str(folderLoopInt))
                                folderLoopInt = 1
                                print("Files exist on HDD but hash didn't match - check HDD - potentially duplicated content.")
                                systemLog.debug(" CHECK - possible duplication: files moved to: "+os.path.join(backupHDDPath,initFolderName)+"_"+str(folderLoopInt))
                systemLog.debug(' Logging session ended at: '+ str(d))
                logEnd = d.strftime("%y%m%d_%H%M%S")
                backupToHDDInit = 0

            if logExportInit == 1 :
                print (" ====================================== Sleeping ("+str(delayPostprocess)+")")
                time.sleep(delayPostprocess)
                print (" ====================================== Exporting logs from system log")
                # session log is extracted from system log
                from os import path #reset path (path was changed for counting total size)
                if path.isdir(pathLogsW) is False :
                    os.mkdir(pathLogsW)
                file = str(logStart)+"-"+str(logEnd)+"_export.txt"
                export_file = os.path.join(pathLogsW,file)
                export_file_backup = os.path.join(backupHDDPath,initFolderName,file)
                regex = logStart
                # read from system log
                with open(str(systemLogPath), "r") as file:
                    match_list = []
                    signal1 = 0
                    for line in file:
                        if signal1 == 0 :
                            for match in re.finditer(regex, line, re.S):
                                match_text = match.group()
                                if match_text == match.group():
                                    signal1 =1
                        else :
                            match_list.append(line)

                    file.close()
                    print("Logs cached.")
                    # write session log to github repo folder
                    with open(export_file, "w+") as file:
                        file.write("EXPORTED DATA: "+str(logStart)+"-"+str(logEnd)+"\n")

                        for item in range(0, len(match_list)):
                            file.write(str(match_list[item]))
                    file.close()
                    print("Logs exported to github repo.")
                    # write session log to backup HDD folder
                    with open(export_file_backup, "w+") as file:
                        file.write("EXPORTED DATA: "+str(logStart)+"-"+str(logEnd)+"\n")

                        for item in range(0, len(match_list)):
                            file.write(str(match_list[item]))
                    file.close()
                    print("Logs exported to backup HDD.")
                logExportInit = 0

                # remove system log
                os.remove(systemLogPath)
                print("SYSTEM LOG DELETED.")


                

    else:
# this part is used when script is run overnight (date change) and enforce saving images to different folder every day
# do not change

# reinit day
        from os import path
        d = datetime.datetime.now()
        dateToday = datetime.date.today()
        dateIsYesterday = datetime.date.today()
        initYear = "%04d" % (d.year)
        initMonth = "%02d" % (d.month)
        initDate = "%02d" % (d.day)
        initHour = "%02d" % (d.hour)
        initMins = "%02d" % (d.minute)
        initFolderName= str(initYear) + str(initMonth) + str(initDate) +"_"+ str(initHour) + str(initMins)
        exportFileName = str(initYear) + str(initMonth) + str(initDate)
        wCounter = 0

# reinit folder
        folderToSave = os.path.join(initPath,initFolderName)   
        
        if path.isdir(str(initPath)) is False :
            os.mkdir(str(initPath))
        if path.isdir(str(folderToSave)) is False :
            os.mkdir(str(folderToSave))

# reinit logging (same file)
        systemLog.handlers[0].doRollover()

        logStart = d.strftime("%y%m%d_%H%M%S")
        systemLog.debug(" Ultimate RaspiLapse -- Started Log for " + str(folderToSave))
        systemLog.debug(str(logStart))
        systemLog.debug(" Logging session started at: "+ str(logStart))
        