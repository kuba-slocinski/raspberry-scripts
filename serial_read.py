#!/usr/bin/env python2
import serial

with serial.Serial('/dev/ttyUSB0', 9600) as ser:
    while True:
        line = ser.readline()
        print(line.strip())
