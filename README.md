 It is known that original raspistill shell timelapse feature cannot save images with filenames set as date or datetime,therefore, new script was developed in pyhon to overcome these obstacles. If set correctly (cronjob), this script can boot itself up after power is provided and start capture images in given interval (anything from 0-24 will do, but it can't run overnight in current state).   Capture can be perpetual as folder generate separately every day at midnight system time. After capturing session is finished (author aimed at 14h/d capture), post-capture processes take place, such as 1) automatic creation of timelapse video, 2) automatic upload to youtube, 3) automatic resizing of the images, 4) automatic move of folder from systemSD to externalHDD and 5) log extraction. Author originally intender to use this camera live on a dynamically built website (React+GitHub+Netlify) so this code sends every n-th image to the github repo and is uploaded with another accompanying script. For serious usage, rebuilding the code to another data storage provider is advised. Git upload can be turned off in the config. Define the location where you wish to save files (initPath in config) If you run a local web server on Apache you could set this to /var/www/ to make them accessible via web browser or use my idea of feeding last image to github repo

Building blocks (prerequisites):
https://bitbucket.org/fotosyn/fotosynlabs/src/9819edca892700e459b828517bba82b0984c82e4/RaspiLapseCam/raspiLapseCam.py?at=master <--original repo
https://github.com/tokland/youtube-upload  <-- prerequisite for yt upload
https://www.raspberrypi.org/documentation/usage/camera/raspicam/raspistill.md <-- raspistill documentation
https://www.raspberrypi.org/documentation/raspbian/applications/camera.md <-- raspistill documentation mode
https://youtu.be/5OFnqLuYZy8?t=660 <-- fstab hdd configuration
Python 3.x, pip3 for python, other pip and apt-get installations needed (like checksumdir)

When setting up the environment for this script, please refer to prereq repos stated above for troubleshooting (GH issues are key)

Attached are three scripts:
1) git_upload.py - uploads file every X seconds, could be reworked to keep multiple files online at once
2) raspishot.sh - is intended to fully customize your camera manual settings to get best results (auto wb was brown [not-correct] in my case)
3) ultimate_timelapse.py - actual timelapse script

Run script with: sudo python /your/file/location/ultimate_timelapse.py

to schedule run at system startup run console nano crontab -e (set time interval within the code)
@reboot /usr/bin/python /home/git_upload.py
@reboot /usr/bin/python /home/pi/ultimate_timelapse.py