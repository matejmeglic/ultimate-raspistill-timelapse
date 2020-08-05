#!/usr/bin/env python3

from rq import Queue
from redis import Redis
import time
import os
import shutil
from os.path import isfile, join

folderToSave = "/TimelapseTemp"

def get_size(start_path):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path): # do not remove dirnames even if code editor returns error (to-do improvement to fix this)
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if not os.path.islink(fp):
                total_size += os.path.getsize(fp)

    return total_size


redis_conn = Redis()
q = Queue(connection=redis_conn)


#job = q.enqueue(count_words_at_url, 'http://gremovmongolijo.com')



#print(round(get_size(folderToSave)/1024/1024,1))

total, used, free = shutil.disk_usage(folderToSave)

print("Total: %d MiB" % (total // 1024 // 1024))
print("Used: %d MiB" % (used // 1024 // 1024))
print("Free: %d MiB" % (free // 1024 // 1024))

result = round(used / total,1)

print("Used: {} %".format(result))

arr = os.listdir(folderToSave)
print(arr)
print(len(arr))


#shutil.rmtree(os.path.join(folderToSave,"asdf"))

folder = folderToSave
for filename in os.listdir(folder):
    file_path = os.path.join(folder, filename)
    try:
        if os.path.isfile(file_path) or os.path.islink(file_path):
            os.unlink(file_path)
    except Exception as e:
        print('Failed to delete %s. Reason: %s' % (file_path, e))

arr = os.listdir(folderToSave)
print(arr)
print(len(arr))