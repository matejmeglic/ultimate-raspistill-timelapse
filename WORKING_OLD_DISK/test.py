#!/usr/bin/env python

import os
import time
import RPi.GPIO as GPIO
import logging
import datetime
import subprocess
import os.path
import re
from os import path

import shutil
from checksumdir import dirhash

folderToSave = "/home/pi/camera/20200504_1340"
initFolderName = "20200504_1341"
backupHDDPath = "/backup/"
folderLoopInt = 1

if path.isdir(str(folderToSave)) is False : 
    print("Source folder doesn't exist - cannot copy to HDD!")
else :
    if path.isdir(str(backupHDDPath)+str(initFolderName)) is False :
        shutil.move(str(folderToSave), str(backupHDDPath)+str(initFolderName))
        #logging.debug("Files successfully moved to: "+str(backupHDDPath)+str(initFolderName))
        print("Files moved to backup HDD")
    else :
        print("Same named file exists on both locations - check")
        hashSource = dirhash(str(folderToSave), 'md5')
        hashHDD = dirhash(str(backupHDDPath)+str(initFolderName),'md5')
        print("Source hash: "+hashSource)
        print("Source hash: "+hashHDD)
        if hashSource == hashHDD :
            print("Files already exist on HDD - copy process stopped.")
        else :
            while path.isdir(str(backupHDDPath)+str(initFolderName)+"_"+str(folderLoopInt)) :
                print("File "+str(backupHDDPath)+str(initFolderName)+"_"+str(folderLoopInt)+" exists, try again.")
                folderLoopInt+=1
            else :
                shutil.move(str(folderToSave), str(backupHDDPath)+str(initFolderName)+"_"+str(folderLoopInt))
                folderLoopInt = 1
                print("Files exist on HDD but hash didn't match - check HDD - potentially duplicated content.")
        





