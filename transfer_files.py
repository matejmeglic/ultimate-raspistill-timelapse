#  #!/usr/bin/env python

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

from distutils.dir_util import copy_tree

tempDisk = "/TimelapseTemp"
toDirectory = "/home/pi/AAA"
#path, dirs, files = next(os.walk(tempDisk))
#file_count = len(files)

def get_size(start_path = tempDisk):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            # skip if it is symbolic link
            if not os.path.islink(fp):
                total_size += os.path.getsize(fp)
        
    return total_size

def delete_contents(start_path = tempDisk):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            os.remove(os.path.join(tempDisk,f))

folderSizeMB = round(get_size()/1024/1024,0)
counter = 0


while folderSizeMB < 240 :
    shutil.copyfile("/home/pi/2020-04-25_17-08-02.jpg", tempDisk+"/"+str(counter)+".jpg")
    folderSizeMB = round(get_size()/1024/1024,0)
    counter += 1
    print(counter, folderSizeMB)
    
    



copy_tree(tempDisk, toDirectory)


delete_contents()