#!/bin/bash

DATE=$(date +"%Y-%m-%d_%H%M%S")

raspistill -w 3280 -h 2464 -o  /home/pi/camera/raspistill_shot/$DATE.jpg -sh 100 -q 100 -v -hf -vf -ev -4 -awb off -awbg 1.6,1.7 -mm average

