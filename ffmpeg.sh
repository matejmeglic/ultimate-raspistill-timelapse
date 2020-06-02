#!/bin/bash

ffmpeg -framerate 30 -pattern_type glob -i '/home/pi/camera/20200529_1052/*.jpg' -c:v libx264 -vf "fps=30,format=yuv420p" -qscale 0 /home/pi/final10.mp4
