#!/usr/bin/env python3

# Import section
import re
import os
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
from datetime import date, timedelta
from checksumdir import dirhash
import logging
import logging.handlers
from suntime import Sun, SunTimeException
import configparser
import user_settings

errors = configparser.ConfigParser()
errors.read('exception_errors.ini')

class Config:
    init_delay_idle = False # sleep if true (save energy)
    init_create_movie = False
    init_upload_to_youtube = False
    init_compression = False
    init_backup_to_HDD = False
    init_log_export = False
    init_set_folders = False # create folders on 1st capture run
    process_on_SD = True # default, only false when saving directly to HDD
    initial_folder_name = "" # capture folder name
    folder_to_save = "" # save images to [either temp or SD/HDD]
    initial_path = "" # SD/HDD path
    end_destination_path = "" # SD/HDD path in case USE_RAM is on
    RAM_counter = 0 # counter for temporary storage
    web_counter = 0 # counter for git upload
    delay_postprocess = 1 # timeout between post-capture actions
    delay_idle = 10 # timeout during idle, non-capture periods

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

        # store final photos to SD or HDD
        if user_settings.STORAGE_TYPE == "SD":
            Config.inital_path = user_settings.SD_PATH
        elif user_settings.STORAGE_TYPE == "HDD":
            Config.inital_path = user_settings.HDD_PATH
            Config.process_on_SD = False
        else:
            raise errors['errors']['ERROR_STORAGE_TYPE']
        Config.folder_to_save = os.path.join(Config.inital_path, Config.initial_folder_name)
        create_folder(Config.folder_to_save)

        # if user uses temporary storage, modify save path
        if user_settings.USE_RAM:
            Config.end_destination_path = Config.folder_to_save # remembers original initial path for export from temporary disk
            Config.folder_to_save = os.path.join(user_settings.TEMP_PATH,"FULLRES")                
            create_folder(Config.folder_to_save)

        # trigger for creating folder structure on capture start
        Config.init_set_folders = True


    # define current time for img name
    img_name = d.strftime("%Y%m%d_%H-%M-%S")

    # Capture the image using raspistill
    print("photo taken at {}".format(img_name))
    #os.system("raspistill -w {} -h {} -o {}.jpg {}".format(user_settings.IMG_WIDTH, user_settings.IMG_HEIGTH, os.path.join(Config.folder_to_save, img_name), user_settings.IMG_PARAMETERS))

    # Wait x+5 seconds before next capture (+5.5 sec goes because raspistill workflow for focusing, taking and saving a shot takes 5-5.5sec)
    if user_settings.USE_RAM:
        Config.RAM_counter +=1 
    print("Sleep "+str(Config.RAM_counter))
    time.sleep(user_settings.DELAY_BETWEEN_IMAGES)       


while True:
    # if none of capture scenarios work, sleep 1min
    if Config.init_delay_idle: 
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
