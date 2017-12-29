#!/usr/bin/python

import time, httplib, urllib, os, glob, socket#, gmaileralert
from datetime import datetime

import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)

# setup GPIO pins:
GPIO.setup(27,GPIO.IN)
# OUT pins:
# 27:       (input for "podajnik")  IN
# 25: szary (relay 1)               OUT 
# 24: zolty (relay 2)               OUT
# --------  (relay 3)
# --------  (relay 4)
# setup GPIO pins:
GPIO.setup(25,GPIO.OUT, initial=1)
GPIO.setup(24,GPIO.OUT, initial=1)

script_dir = os.path.dirname(os.path.abspath(__file__))

# Node Exporter directory for storing results:
node_exporter_path = "/var/lib/node_exporter/textfile_collector"

# read ThingSpeak API key:
with open(script_dir + "/ThingSpeak.key") as f:
  api_key = f.readline()

""" 
This script gathers data and:
- streams data to ThingSpeak via sendToThingSpeak()  (https://www.thingspeak.com)
- stores in node_exporter_path for node_exporter via storeForNodeExporter()
"""

def sendToThingSpeak(input):
    params = urllib.urlencode(input)
    headers = {"Content-type": "application/x-www-form-urlencoded","Accept": "text/plain"}
    conn = httplib.HTTPConnection("api.thingspeak.com:80")
    conn.request("POST", "/update", params, headers)
    #print params
    response = conn.getresponse()
    # Uncomment the print statement to check connection to TS
    #  print response.status, response.reason
    data = response.read()
    conn.close()

def storeForNodeExporter(input):
    fn="input"
    with open(node_exporter_path+"/"+fn+".data", "w") as f:
        for sensor, data in sorted(input.items()):
            f.write(str(sensor)+" "+str(data))
            f.write("\n")
        f.close()
    # now, atomic operation: rename file:
    os.rename(node_exporter_path+"/"+fn+".data", node_exporter_path+"/"+fn+".prom");

#def log_state(input):
#    with open("log_gpio_state.txt", "a") as f: 
#        f.write(str(datetime.now()))
#        for sensor, val in sorted(input.items()):
#            f.write("\t")
#            f.write(str(val))
#        f.write("\n")

if __name__ == "__main__":
    # dictionary for each sensor and device location
    w1= { 'field5': 27 }
    # field1: internal : cpu_temp
    # field2: ce525 : temp. CWU
    # field3: e11ff : temp. mieszacza
    # field4: 867ff : temp. kotla
    # field5: gpio27 : status podajnika (on/off)
    sum = 0
    fails = 0
    
    print "starting INPUT state readings on: " + str(datetime.now())
    while True:
        try:
            dict = { }

            # add Things Speak special API key pair
            dict['key'] = api_key

            for fieldName, gpioPIN in w1.iteritems():
                state = not GPIO.input(gpioPIN)
                #print state

                # we count nr of seconds input was in changed state, then we send it as a value after state get back to normal (HIGH).
                # WARNING:  PAUSE + SUM < 15s. If state changes more often, thingspeak will discard those values.
                if state:
                  sum += 1
                  # reset fails if we got data again and sum them to data
                  if fails > 0:
                    print "adding fails: %d" % fails
                    sum += fails
                    fails = 0
                elif sum > 0 and fails < 2:
                  fails += 1
                elif sum > 0:
                  #dict[fieldName] = sum
                  dict[fieldName] = 1
                  print "Sending value of %d\n" % sum
                  storeForNodeExporter({'podajnik': 1})
                  sendToThingSpeak(dict)
                  sum = 0
                  fails = 0
                  time.sleep(10)

            storeForNodeExporter({"podajnik": 0})
            #sleep for 16 seconds (api limit of 15 secs)
            time.sleep(1)

        except socket.gaierror, e:
            print "%s There was a socket.gaierror: %s" % (e, str(datetime.now()))
            time.sleep(15)
        except socket.error, e:
            print "%s There was a socket.error: %s" % (e, str(datetime.now()))
            time.sleep(15)
        except (SystemExit):
            raise

