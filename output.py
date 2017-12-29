#!/usr/bin/python

import time, httplib, urllib, os, glob, socket#, gmaileralert
from datetime import datetime

import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)

# OUT pins:
# 25: szary (relay 1)
# 24: zolty (relay 2)
# --------  (relay 3)
# --------  (relay 4)
# setup GPIO pins:
GPIO.setup(25,GPIO.OUT, initial=1)
GPIO.setup(24,GPIO.OUT, initial=1)

# XXX we setup pins already in "input.py". We should have one script to setup/read/store values.

# state 0 - relay led ON
# state 1 - relay led OFF

#sleep(2)

GPIO.output(25, 1) 
#sleep(2)
GPIO.output(24, 1)
