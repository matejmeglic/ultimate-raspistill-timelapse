#!/usr/bin/env python3

# settings (change to your preference)
# storage settings (file name is defined later in the code)
HDD_PATH = "/backup" # path is used for storing directly to HDD. use sudo nano /etc/fstab to define mounting point for your HDD, then change path
# capture settings
CAPTURE_SUN_TIME = False # 1 for running capture session based on sunrise and sunset times gathered from www; if this is set to 1, captureTimeframe doesn't work
CAPTURE_SUN_TIME_LATITUDE = 46.062935
CAPTURE_SUN_TIME_LONGITUDE = 14.519045
CAPTURE_SUN_TIME_SUNRISE_OFFSET = 0
CAPTURE_SUN_TIME_SUNSET_OFFSET = 0 
CAPTURE_SUN_TIME_NIGHTLY = False
# set capture as [start-h,start-m,end-h,end-m, day-rollover] = without leading zero's (does not support rolling over midnight)
CAPTURE_TIMEFRAME = [
    [16,0,20,0], 
    [5,5,8,48],
    [21,0,3,0]
    ]
DELAY_BETWEEN_IMAGES = 30 # Wait x+5 seconds before next capture (+5.5 sec goes because raspistill workflow for focusing, taking and saving a shot takes 5-5.5sec)
# IMG settings
IMG_WIDTH = 3280 # Max = 3280
IMG_HEIGTH = 2464 # Max = 2464
IMG_PARAMETERS = "-sh 100 -q 100 -v -vf -hf -ev -4 -awb off -awbg 1.6,1.7 -mm average -n" #raspistill image capture parameters
EXPORT_MOVIE_SETTINGS = [ # [fps, parameters, export_folder, video_suffix (yyyy-mm-dd hardcoded), logging_name, youtube_credentials, youtube_playlist, upload_to_youtube_yes/no]
    [30, "-vf scale=1920:1442 -qscale 0", "export/exportFullHD", "FullHD", "/home/pi/cs.json", "timelapse", False],
    [30, "-qscale 0", "export/4k", "4k", "/home/pi/cs.json", "timelapse", True]
    ]
# post-capture automation switches
CREATE_MOVIE = True # create timelapse movie
UPLOAD_TO_YOUTUBE = True # uploads timelapse movie to youtube
COMPRESSION = True # compresses all files in initPath
LOG_EXPORT = False # exports logs to git + backup HDD
# git upload configs
UPLOAD_TO_WEB = True # git upload - this switch controls uploading every x-th image to separate folder alongside with alltime image creation
WEB_UPLOAD_COUNTER_ROLL = 9 # how often a compressed picture is duplicated in github www repo (and in alltime folder)
WEB_UPLOAD_IMG_WIDTH = 1920 # Max = 3280 width and height of www repo image (smaller to decrease page loading time and file transfer)
WEB_UPLOAD_IMG_HEIGTH = 1442 # Max = 2464
WEB_UPLOAD_PATH_LOG = "/home/pi/tl_cam/public/logs" # logs in github repo
WEB_UPLOAD_PATH_IMG = "/home/pi/tl_cam/public/img" # last image in github repo
INIT_ALLTIME = True # extra copy of all images that were sent to the web (compressed)
ALLTIME_PATH = "www_alltime" # subfolder to store full-res pictures that were sent to www repo


# WARNING - SD path only (no HDD scenario) - keep False at all costs, potential loss of data
DELETE_PICTURES = False # WARNING! This is for SD without storing images to HDD. If True, deletes images after capture and post-processing is completed (will not delete movies and alltime if they will be placed in a separate subfolder)
DELETE_ALL = False # WARNING! This will delete ALL created content (pictures, movies, alltime)