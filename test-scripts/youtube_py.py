#!/usr/bin/env python3

import re
import os
import os.path
import time
import RPi.GPIO as GPIO
import logging
import datetime
import subprocess
import shutil
from os import path
from checksumdir import dirhash


fileName = "cgii_1080_0"
youtubeClientSecretsPath = "/home/pi/cs.json"
youtubePlaylistTitle = "timelapse"
folderToSave = "/home/pi/Videos"
tlVideoExportPath = "/export"


os.system("youtube-upload --title=" + str(fileName) + " --client-secrets="+ youtubeClientSecretsPath +" --playlist='"+youtubePlaylistTitle+"' --embeddable=True "+ str(folderToSave) + str(tlVideoExportPath) + "/" + str(fileName) +".mp4")
                