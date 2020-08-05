#!/usr/bin/env python3

import os
from oauth2client import file 

EXPORT_MOVIE_SETTINGS = [ # [fps, parameters, export_folder, video_suffix (yyyy-mm-dd hardcoded), logging_name, youtube_credentials, youtube_playlist, upload_to_youtube_yes/no]
    [30, "-vf scale=1920:1442 -qscale 0", "export/exportFullHD", "FullHD", "/home/pi/cs.json", "timelapse", False],
    [30, "-qscale 0", "export/4k", "4k", "/home/pi/cs.json", "timelapse", True]
    ]

for movie in EXPORT_MOVIE_SETTINGS:
            if movie[6]:                                          
                movie_title = "20200805_1505-1548_"+movie[3]
                export_path = os.path.join("/backup/20200805_1505-1548", movie[2])
                os.system("/usr/local/bin/youtube-upload --title={} --client-secrets={} --playlist='{}' --embeddable=True {}.mp4".format(movie_title, movie[4], movie[5], os.path.join(export_path, movie_title)))