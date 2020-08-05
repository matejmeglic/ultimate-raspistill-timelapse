#!/usr/bin/env python3

import datetime
from datetime import timedelta
from suntime import Sun, SunTimeException

latitude = 51.21
longitude = 21.01

sun = Sun(latitude, longitude)

# Get today's sunrise and sunset in UTC
today_sr = sun.get_sunrise_time()
today_ss = sun.get_sunset_time()
print('Today at Warsaw the sun raised at {} and get down at {} UTC'.
      format(today_sr.strftime('%H:%M'), today_ss.strftime('%H:%M')))

abd_sr = sun.get_local_sunrise_time()
abd_ss = sun.get_local_sunset_time()
print('the sun at Warsaw raised at {} and get down at {}.'.
      format(abd_sr.strftime('%H:%M'), abd_ss.strftime('%H:%M')))

abd_sr1 = sun.get_local_sunrise_time()+datetime.timedelta(minutes=0)
abd_ss1 = sun.get_local_sunset_time()+datetime.timedelta(minutes=0)
print('the sun at Warsaw raised at {} and get down at {}.'.
      format(abd_sr1.strftime('%H:%M'), abd_ss1.strftime('%H:%M')))