#!/usr/bin/env python3

# Import section
import re
import glob
import os
import os.path
from os.path import isfile, join
from os import listdir, path
import time
import datetime
from datetime import date, timedelta
from suntime import Sun, SunTimeException
import subprocess
import shutil
from checksumdir import dirhash
import logging
import logging.handlers
# import other files
import configparser
import user_settings

# redis queue for git upload
# from rq import Queue
# from redis import Redis
# redis_conn = Redis()
# q = Queue(connection=redis_conn) 

# load errors document
errors = configparser.ConfigParser()
errors.read('exception_errors.ini')

# set script variables
class Config:
    init_delay_idle = False # sleep if true (save energy)
    init_create_movie = False
    init_upload_to_youtube = False
    init_compression = False
    init_log_export = False
    init_set_folders = False # create folders on 1st capture run
    initial_path = "" # SD/HDD path
    initial_folder_name = "" # capture folder name
    folder_to_save = "" # full path for saving images
    web_counter = 0 # counter for git upload
    delay_idle = 10 # timeout during idle, non-capture periods

# function declarations

# check if folder exists and fo not, create
def create_folder( path_to_check ):
    if not path.isdir(path_to_check):
        try:
            os.makedirs(path_to_check)
        except:
            Exception(errors['errors']['ERROR_PATH_NOT_CREATED'].format(path_to_check))

# concatenate two integers into hhmm for scenario assignment    
def concat_2_int(int1, int2):
    if int1 > 23 or int2 > 59:
        Exception(errors['errors']['ERROR_CHECK_CAPTURE_TIME'])
    hour_minute = "{0:0=4d}".format(int(str("{0:0=2d}".format(int1))+str("{0:0=2d}".format(int2))))
    return hour_minute

# calculating total size function (function called twice)
def get_size(start_path = str(Config.folder_to_save)):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path): # do not remove dirnames even if code editor returns error (to-do improvement to fix this)
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if not os.path.islink(fp):
                total_size += os.path.getsize(fp)
    return total_size
       
# main image capture & post processing function
def capture(capture_scenario):
    Config.init_delay_idle = False # ongoing capture, don't sleep
    # 1st time create folder structure
    if not Config.init_set_folders:
        # set folder name generated based on capture scenario
        if capture_scenario == "capture": 
            Config.initial_folder_name = "{}_{}-{}".format(d.strftime("%Y%m%d"), concat_timeframe_start, concat_timeframe_end) 
        elif capture_scenario == "capture-overnight": 
            next_day = d+datetime.timedelta(days=1)
            Config.initial_folder_name = "{}_{}-{}_{}".format(d.strftime("%Y%m%d"), concat_timeframe_start, next_day.strftime("%Y%m%d"), concat_timeframe_end) 
        elif capture_scenario == "suntime": 
            Config.initial_folder_name = "{}_{}-{}".format(d.strftime("%Y%m%d"), sunrise.strftime('%H%M'), sunset.strftime('%H%M')) 
        elif capture_scenario == "suntime-overnight": 
            next_day = d+datetime.timedelta(days=1)
            Config.initial_folder_name = "{}_{}-{}_{}".format(d.strftime("%Y%m%d"), sunset.strftime('%H%M'), next_day.strftime("%Y%m%d"), sunrise.strftime('%H%M')) 
        else:
            Exception(errors['errors']['ERROR_INVALID_SCENARIO'])

        # create folder
        Config.inital_path = user_settings.HDD_PATH     
        Config.folder_to_save = os.path.join(Config.inital_path, Config.initial_folder_name)
        create_folder(Config.folder_to_save)

        # trigger for creating folder structure on capture start
        Config.init_set_folders = True


    # define current time for img name
    img_name = d.strftime("%Y%m%d_%H-%M-%S")

    # Capture the image using raspistill
    print("photo taken at {}".format(img_name))
    os.system("raspistill -w {} -h {} -o {}.jpg {}".format(user_settings.IMG_WIDTH, user_settings.IMG_HEIGTH, os.path.join(Config.folder_to_save, img_name), user_settings.IMG_PARAMETERS))

    # place picture to rq queue for git upload
    if user_settings.UPLOAD_TO_WEB:
        Config.web_counter = Config.web_counter +1
        if Config.web_counter == user_settings.WEB_UPLOAD_COUNTER_ROLL:
            # ffmpeg creates virtual copy in github repo
            create_folder(user_settings.WEB_UPLOAD_PATH_IMG)
            os.system("ffmpeg -i {}.jpg -vf scale={}:{} {}.jpg -y".format(os.path.join(Config.folder_to_save, img_name), user_settings.IMG_WIDTH, user_settings.IMG_HEIGTH, os.path.join(user_settings.WEB_UPLOAD_PATH_IMG, img_name)))
            Config.web_counter = 0
            # ffmpeg creates virtual (full-res) copy in /www_alltime folder (so you have easy access to all published photos)
            if user_settings.INIT_ALLTIME:
                alltime = os.path.join(Config.folder_to_save, user_settings.ALLTIME_PATH)
                create_folder(alltime)
                os.system("ffmpeg -i {}.jpg -vf scale={}:{} {}.jpg -y".format(os.path.join(Config.folder_to_save, img_name), user_settings.IMG_WIDTH, user_settings.IMG_HEIGTH, os.path.join(alltime, img_name)))           
            

    # Wait x+5 seconds before next capture (+5.5 sec goes because raspistill workflow for focusing, taking and saving a shot takes 5-5.5sec)
    time.sleep(user_settings.DELAY_BETWEEN_IMAGES)       

# initialize post-capture processes to only run after 1st timelapse section is completed
def post_capture():
    if user_settings.CREATE_MOVIE:
        Config.init_create_movie = True
    if user_settings.UPLOAD_TO_YOUTUBE:
        Config.init_upload_to_youtube = True
    if user_settings.COMPRESSION:
        Config.init_compression = True
        if user_settings.DELETE_PICTURES: # don't compress in case SD-card scenario enabled
            Config.init_compression = False
    if user_settings.LOG_EXPORT:
        Config.init_log_export = True

    if Config.init_create_movie:
        for movie in user_settings.EXPORT_MOVIE_SETTINGS: # create a movie for every array entry
            export_path = os.path.join(Config.folder_to_save, movie[2])
            create_folder(export_path)
            movie_title = Config.initial_folder_name+"_"+movie[3]
            os.system("ffmpeg -framerate {} -pattern_type glob -i '{}/*.jpg' {} {}.mp4".format(movie[0], Config.folder_to_save, movie[1], os.path.join(export_path, movie_title)))
        Config.init_create_movie = False
        
    if Config.init_upload_to_youtube:
        for movie in user_settings.EXPORT_MOVIE_SETTINGS:
            if movie[6]:                                            # upload, if movie is selected as uploadable
                movie_title = Config.initial_folder_name+"_"+movie[3]
                export_path = os.path.join(Config.folder_to_save, movie[2])
                os.system("/usr/local/bin/youtube-upload --title={} --client-secrets={} --playlist='{}' --embeddable=True {}.mp4".format(movie_title, movie[4], movie[5], os.path.join(export_path, movie_title)))
        Config.init_upload_to_youtube = False

    if Config.init_compression: # compress all photos
        photos = os.listdir(Config.folder_to_save)
        for photo in photos:
            photo_path = os.path.join(Config.folder_to_save,photo)
            os.system('ffmpeg -i {} -vf scale={}:{} {} -y'.format(photo_path, user_settings.IMG_WIDTH, user_settings.IMG_HEIGTH, photo_path))
        Config.init_compression = False

    if Config.init_log_export:
        print("Log was exported :)")
        Config.init_log_export = False

    # reset paths    
    Config.initial_path = ""
    Config.initial_folder_name = ""
    Config.folder_to_save = ""
   
    # SD scenario - DELETE SOURCE FILES
    if user_settings.DELETE_PICTURES:
        for filename in os.listdir(Config.folder_to_save):
            file_path = os.path.join(Config.folder_to_save, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))

    # SD scenario - DELETE ALL
    if user_settings.DELETE_ALL:
        shutil.rmtree(Config.folder_to_save)


while True:
    
    if Config.init_delay_idle: # if none of capture scenarios are active, sleep 1min
        if Config.init_set_folders: # after first iteration without active capture scenario, run post_capture actions
            post_capture() # run post-capture actions
            Config.init_set_folders = False
            Config.web_counter = 0
        print("Idling {}".format(Config.delay_idle))   
        time.sleep(Config.delay_idle)

    d = datetime.datetime.now() # Capture current time
    concat_d = concat_2_int(d.hour, d.minute) # concat time
    Config.init_delay_idle = True # if there are no capture slots, sleep a wee (to save energy)

    # set correct capture scenario
    if user_settings.CAPTURE_SUN_TIME: # SUN_TIME has priority
        sun = Sun(user_settings.CAPTURE_SUN_TIME_LATITUDE, user_settings.CAPTURE_SUN_TIME_LONGITUDE)
        sunrise = sun.get_local_sunrise_time()+datetime.timedelta(minutes=user_settings.CAPTURE_SUN_TIME_SUNRISE_OFFSET)
        sunset = sun.get_local_sunset_time()+datetime.timedelta(minutes=user_settings.CAPTURE_SUN_TIME_SUNSET_OFFSET)

        if not user_settings.CAPTURE_SUN_TIME_NIGHTLY: # sunrise-sunset
            if concat_d >= sunrise.strftime('%H%M'): 
                if concat_d <= sunset.strftime('%H%M'):
                    capture("suntime")
        else:                                          # sunset-sunrise
            if concat_d >= sunset.strftime('%H%M'): 
                capture("suntime-overnight") 
            elif concat_d <= sunrise.strftime('%H%M'):
                capture("suntime-overnight") 
    else:
        for timeframe in user_settings.CAPTURE_TIMEFRAME: # is SUN_TIME is turned off, check CAPTURE_TIMEFRAME array
            concat_timeframe_start = concat_2_int(timeframe[0], timeframe[1])
            concat_timeframe_end = concat_2_int(timeframe[2], timeframe[3])

            if concat_timeframe_start < concat_timeframe_end: # daily capture [00-2359]
                if concat_d >= concat_timeframe_start: 
                    if concat_d <= concat_timeframe_end:
                        capture("capture")
            else:                                             # nightly capture [rolling over midnight]
                if concat_d >= concat_timeframe_start:  # until midnight
                    capture("capture-overnight")
                if concat_d <= concat_timeframe_end:    # after midnight
                    capture("capture-overnight")
