# Ultimate Raspistill timelapse 
## Fully automated Raspberry Pi Camera datetime automated timelapse that works 
- v0.1 - 20200505 stable version. bugs can be found, but after rudimentary testing (2d), main workflow works as expected on RPI4. 
Everyone is encouraged to do PR and contribute.

## Thank you section
Special thanks go to James Moore, Fotosy who created initial python script that I relied heavily when creating this extended version, to Arnau Sanchez for sharing automatic youtube uploader and to Marko Trebizan for being a mentor one can dream of.

## Description
This script was created because it is known that original raspistill shell timelapse feature cannot save images with filenames set as date or datetime (yyyy-mm-dd), only as a sequence (image%02d) therefore, new script was developed in pyhon to overcome these obstacles plus automate workflows so that it can be used as a standalone timelapse camera. 
 
If set correctly (cronjob), this script can boot itself up after power is provided and start capture images in given interval (anything from 0-24 will do, but it can't run overnight in current state). Capture can be perpetual as folder generate separately every day at midnight system time. After capturing session is finished (author aimed at 14h/d capture), post-capture processes take place, such as 1) automatic creation of timelapse video, 2) automatic upload to youtube, 3) automatic resizing of the images, 4) automatic move of folder from systemSD to externalHDD and 5) log extraction. Author originally intender to use this camera live on a dynamically built website (React+GitHub+Netlify) so this code sends every n-th image to the github repo and is uploaded with another accompanying script. For serious usage, rebuilding the code to another data storage provider is advised. Git upload can be turned off in the config. Define the location where you wish to save files (initPath in config) If you run a local web server on Apache you could set this to /var/www/ to make them accessible via web browser or use my idea of feeding last image to github repo

## Building blocks (prerequisites)
- https://bitbucket.org/fotosyn/fotosynlabs/src/9819edca892700e459b828517bba82b0984c82e4/RaspiLapseCam/raspiLapseCam.py?at=master <--original repo
- https://github.com/tokland/youtube-upload  <-- prerequisite for yt upload
- https://www.raspberrypi.org/documentation/usage/camera/raspicam/raspistill.md <-- raspistill documentation
- https://www.raspberrypi.org/documentation/raspbian/applications/camera.md <-- raspistill documentation mode
- https://youtu.be/5OFnqLuYZy8?t=660 <-- fstab hdd configuration
- Python 3.x, pip3 for python, other pip and apt-get installations needed (like checksumdir, also make sure that Python3 is actually run after it's installed)
- Probably a lot of trouble shooting and other dependencies that I forgot about during development. If I will create another one, I will try to document this section more.

When setting up the environment for this script, please refer to prereq repos stated above for troubleshooting (GH issues are key)

## Contents
Attached are four scripts:
1) **ffmpeg.sh** - *TEST TOOL: *creates a timelapse video (specify source and destination), useful for testing video quality (bitrate) [settings between 0-best and 51-worst]
2) **git_upload.py** - *GIT CRON UPLOADER:* uploads file every X seconds, could be reworked to keep multiple files online at once - **require SSH connection to your GH repo**
3) **raspishot.sh** - *TEST TOOL:* is intended to fully customize your camera manual settings to get best results (auto wb was brown [not-correct] in my case)
4) **ultimate_timelapse.py** - actual timelapse script

## Running scripts
Run script with: **sudo python /your/file/location/ultimate_timelapse.py**

### Preffered way - set up a cronjob
to schedule run at system startup run console nano **crontab -e **(set time interval within the code)
**@reboot /usr/bin/python /home/git_upload.py
@reboot /usr/bin/python /home/pi/ultimate_timelapse.py**



### Installation from the get-go (pi3 + pi camera) #fordummies :D
#### Set up Pi
0. Get Pi up and running

a. download Raspbian desktop image + extract ZIP file
b. download balenaEtcher
c. burn image on SD card
d. set up PI 
    - location and language,
    - user pi password,
    - wifi,
    - download updates (might take a while),
    - keyboard layout, 
    - Pi Start button (open menu) - Preferences - R Pi Configuration - interfaces tab -  enable camera, VNC, SSH
    - set up VNC (for remote access and debugging, find yt tutorial like https://www.youtube.com/watch?v=XjpquXPf24s, make sure to check VNC server boots on start)
    - terminal - sudo raspi-config - enable running it without HDMI cable attached (had problems where I was not able to access remote desktop on RPI4)
    - reboot

#### Set up prerequisites for timelapse script
1. As you assure that Pi works as intended, shut it down and connect the camera (read instructions on static electricity, don't forget to take SD card out if you are using RPI housing, peel protective layer off). 
2. Download files from this git repo (terminal - GIT CLONE REPOSITORY_LINK)
3. terminal - chmod +x /home/pi/ultimate-raspistill-timelapse/raspishot.sh      <-- this will make .sh script executable
4. Use raspishot.sh to take photos and set up camera settings if needed (refer to the documentation, use text editor to modify output folder of the script) 
HURA - first captured photos should be in the folder
5. terminal - sudo apt update
6. terminal - sudo apt upgrade (might take a while)
7. terminal - sudo apt-get install xscreensaver (after that turn screen saver of in Raspi-menu - Preferences - Screensaver)
7. terminal - sudo reboot
8. terminal - pip install checksumdir
9. terminal - sudo apt install ffmpeg
If you disable all the post-capture actions 
    - set all post-capture actions to **False** in the config section, 
    - recheck all folder paths in config, 
    - now a rudimentary timelapse should work 
    - try with terminal - cd FOLDER - python ultimate_timelapse.py - interrupt process with CTRL+C (note that you can change captureElement from hours to minutes in the code)
    - at this moment, you can also turn createVideo and compression post-capture functionality on as it should work

#### Set up post-capture (autonomous) functionalities
Follow https://github.com/tokland/youtube-upload
- sudo pip install --upgrade google-api-python-client oauth2client progressbar2
- wget https://github.com/tokland/youtube-upload/archive/master.zip
- unzip master.zip
- cd youtube-upload-master
- sudo python setup.py install
Set up OAuth file
- log into google console (make sure you log in with account that has linked (is owner of) youtube channel - if you are having problems, that is the likely cause for them)
- select project - new project - enter name of your project - click Create project
- select newly created project
- APIs & Services - click Enable APIs and Services - find all Youtube related APIs and enable them (I believe you only need Data API v3 [20200528])
- Click Create credentials 
    - youtube api
    - other non-ui
    - public data
    - you get the key (restrict it if you want, I use it offline)
- configure consent screen
    - external user type
    - submit information for verification
- Create credentials
    - OAuth cliend ID
    - Application type: desktop app



- OAuth client ID
- Configure consent screen
    - User type : External
    - enter data and click Save
- Click Create credentials - OAuth client ID - Application type: Desktop app (or other) - name: youtube-upload - Create
- download .json file (far right in OAuth 2.0 Client IDs)
- modify path to .json file, title and path to video in youtube-upload.sh
- terminal - chmod +x youtube-upload.sh (to make it executable)
- terminal - ./youtube-upload.sh (run script)
    - script will ask you to open link in a browser for validation
    - click on correct email profile --> then click on correct YOUTUBE ACCOUNT
    - Advanced
    - go to youtube uploading ...
    - Allow youtube to manage videos and account
    - Allow
    - Paste given code back to the terminal and press enter
    - if everything was done correctly, you should be able to upload videos - if you are getting 401, there is a problem with Authorization with your youtube channel or smth, refer to tokland GitHub issues and google for solving that part




todo:
- check logs
- check all folders from config and make them if they don't exist prior to recording (try multilevel checks)
- config for gitupload
- config for 4k and fullHd upload
- config hour/minute move to config
- git cron