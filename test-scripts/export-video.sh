9#!/bin/bash

ffmpeg -framerate 30 -pattern_type glob -i '/home/pi/camera/20200529_1626/*.jpg' -vf scale=1920:-1 -qscale 0 /home/pi/original.mp4
                