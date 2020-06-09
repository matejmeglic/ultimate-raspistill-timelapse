#!/usr/bin/env python3

from ultimate_timelapse_a import (initYear, initMonth, initDate, initHour, initMins)

# config (change to your preference)
# capture settings
captureTimeframe = [
    [4,0,12,12], # set capture as [h,m,hh,mm] = without leading zero's
    [12,15,23,00]
]
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
exportMovieSettings = [
    [30, "-vf scale=1080:810 -qscale 0","export","".join(str(initYear) + str(initMonth) + str(initDate)),"FullHD","/home/pi/cs.json","timelapse",0],
    [30, "-qscale 0","export","".join(str(initYear) + str(initMonth) + str(initDate)+"_4k"),"4k","/home/pi/cs.json","timelapse",1]
]
backupHDDPath = "/home/pi/backupaa" # use sudo nano /etc/fstab to define mounting point for your HDD
# git upload configs
uploadToWeb = True # this switch controls uploading every x-th image to separate folder alongside with alltime image creation
wCounterRoll = 9 # how often a compressed picture is duplicated in github www repo (and in alltime folder)
imgWidthWeb = 1920 # Max = 3280 width and height of www repo image (smaller to decrease page loading time and file transfer)
imgHeightWeb = 1442 # Max = 2464
alltimePath = "www_alltime" # subfolder to store full-res pictures that were sent to www repo
pathLogsW = "/home/pi/ku_tl_cam/public/logs" # logs in github repo
pathImgW = "/home/pi/ku_tl_cam/public/img" # last image in github repo




