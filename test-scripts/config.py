#!/usr/bin/env python3


# config (change to your preference)
# caching settings
USE_RAM = True # store photos to RAM (temporary storage) to prolong SD-card life (decrease number of writes to medium)
STORAGE_TYPE = "SD" # set "SD" or "HDD"
TRANSFER_TO_DISK = 35 # calculate after how many iterations script should move photos from RAM to SD/HDD (calculate RAM storage / ~5MB/file x 0.8 = transferToDisk) <-- 0.8 = factor that takes into consideration that some photos will be taken during the process of file transfer from RAM to SD/HDD
# storage settings (file name is defined later in the code)
TEMP_PATH = "/TimelapseTemp" # RAM path, created with sudo nano etc/fstab
SD_PATH = "/home/pi/camera"
HDD_PATH = "/backup" # path is used for storing directly to HDD and for backup to HDD. use sudo nano /etc/fstab to define mounting point for your HDD, then change path
ALLTIME_PATH = "www_alltime" # subfolder to store full-res pictures that were sent to www repo
# capture settings
CAPTURE_SUN_TIME = True # 1 for running capture session based on sunrise and sunset times gathered from www; if this is set to 1, captureTimeframe doesn't work
CAPTURE_SUN_TIME_OFFSET = [0,0] # offset to when SunTime capture should start/end in min
CAPTURE_TIMEFRAME = [
    [4,3,19,37], # set capture as [start-h,start-m,end-h,end-m] = without leading zero's
    [19,39,19,43]
]
DELAY_BETWEEN_IMAGES = 5 # Wait x+5 seconds before next capture (+5.5 sec goes because raspistill workflow for focusing, taking and saving a shot takes 5-5.5sec)
# IMG settings
IMG_WIDTH = 3280 # Max = 3280
IMG_HEIGTH = 2464 # Max = 2464
IMG_PARAMETERS = "-sh 100 -q 100 -v -vf -hf -ev -4 -awb off -awbg 1.6,1.7 -mm average -n" #raspistill image capture parameters
# post-capture automation switches
CREATE_MOVICE = False # create timelapse movie
UPLOAD_TO_YOUTUBE = False # uploads timelapse movie to youtube
COMPRESSION = False # compresses all files in initPath
BACKUP_TO_HDD = False # backups all initPath's contents to HDD
LOG_EXPORT = False # exports logs to git + backup HDD
UPLOAD_TO_WEB = False # git upload - this switch controls uploading every x-th image to separate folder alongside with alltime image creation
# automation configs
EXPORT_MOVIE_SETTINGS = [ # [fps, parameters, export_folder, video_suffix (yyyy-mm-dd hardcoded), logging_name, youtube_credentials, youtube_playlist, upload_to_youtube_yes/no]
    [30, "-vf scale=1080:810 -qscale 0","export","","FullHD","/home/pi/cs.json","timelapse",0],
    [30, "-qscale 0","export","_4k","4k","/home/pi/cs.json","timelapse",1]
]

# git upload configs
WEB_UPLOAD_COUNTER_ROLL = 9 # how often a compressed picture is duplicated in github www repo (and in alltime folder)
WEB_UPLOAD_IMG_WIDTH = 1920 # Max = 3280 width and height of www repo image (smaller to decrease page loading time and file transfer)
WEB_UPLOAD_IMG_HEIGTH = 1442 # Max = 2464
WEB_UPLOAD_PATH_LOG = "/home/pi/ku_tl_cam/public/logs" # logs in github repo
WEB_UPLOAD_PATH_IMG = "/home/pi/ku_tl_cam/public/img" # last image in github repo




