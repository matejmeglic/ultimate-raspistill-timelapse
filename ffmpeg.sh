#!/bin/bash

ffmpeg -framerate 30 -pattern_type glob -i '/backup/20200505_0000_2/*.jpg' -qscale 0 /home/pi/Videos/final10.mp4
