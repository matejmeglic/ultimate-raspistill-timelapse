#!/bin/bash

ffmpeg -framerate 30 -pattern_type glob -i '/backup/20200508_0000/*.jpg' -qscale 0 /backup/20200508/export/4k0.mp4