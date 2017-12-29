#!/usr/bin/python

import time, httplib, urllib, os, glob, socket#, gmaileralert
from datetime import datetime
import re

script_dir = os.path.dirname(os.path.abspath(__file__))

# Node Exporter directory for storing results:
node_exporter_path = "/var/lib/node_exporter/textfile_collector"

# read ThingSpeak API key:
with open(script_dir + "/ThingSpeak.key") as f:
  api_key = f.readline()

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

""" 
This script gathers data and:
- streams data to ThingSpeak via sendToThingSpeak()  (https://www.thingspeak.com)
- stores in node_exporter_path for node_exporter via storeForNodeExporter()
"""

def calibrate(k,v):
    # kalibracja mieszacza: #3.5
    if '28-0316467e11ff' in k:
      v += 0.5
    # kalibracja temp kotla: #7
    elif '28-041651d867ff' in k:
      v += -4
    # kalibracja temp CWU: #5
    elif '28-0000087ce525' in k:
      v += -1
    # CWU na powrocie #0
    elif '28-041651311dff' in k:
      v += 0
    return v

def readsensor(input):
    raw = open(input, "r").read()
    temperature = float(raw.split("t=")[-1])/1000
    return round(calibrate(input,temperature), 1)

def sendToThingSpeak(input):
    params = urllib.urlencode(input)
    headers = {"Content-type": "application/x-www-form-urlencoded","Accept": "text/plain"}
    conn = httplib.HTTPConnection("api.thingspeak.com:80")
    conn.request("POST", "/update", params, headers)
    print params
    response = conn.getresponse()
    # Uncomment the print statement to check connection to TS
    #  print response.status, response.reason
    data = response.read()
    conn.close()


def storeForNodeExporter(input):
    with open(node_exporter_path+"/ds18b20.data", "w") as f: 
        #f.write(str(datetime.now()))
        for sensor, temperature in sorted(input.items()):
            f.write(str(sensor)+" "+str(temperature))
            f.write("\n")
        f.close()
    # now, atomic operation: rename file:
    os.rename(node_exporter_path+"/ds18b20.data", node_exporter_path+"/ds18b20.prom");

if __name__ == "__main__":
    # dictionary for each sensor and device location
    w1= { 'field2': '/sys/bus/w1/devices/28-0000087ce525/w1_slave',
          'field3': '/sys/bus/w1/devices/28-0316467e11ff/w1_slave',
          'field4': '/sys/bus/w1/devices/28-041651d867ff/w1_slave',
          'field5': '/sys/bus/w1/devices/28-041651311dff/w1_slave'}
    w2= {'field2': 'temp_cwu',
         'field3': 'temp_mieszacza',
         'field4': 'temp_kotla',
         'field5': 'temp_cyrkulacji'}
    # field1: internal : cpu_temp
    # field2: ce525 : temp. CWU
    # field3: e11ff : temp. mieszacza
    # field4: 867ff : temp. kotla
    
    print "starting temperature readings on: " + str(datetime.now())
    while True:
        try:
            dict = { }
            dict2 = { }
            for key, value in w1.iteritems():
                dict[key] = readsensor(value)
                dict2[w2[key]] = dict[key]
           
            # Log the data to a file
            storeForNodeExporter(dict2)

            # add Things Speak special API key pair
            dict['key'] = api_key
            
            #sendToThingSpeak(dict) # send the data to Things Speak
            
            #sleep (api limit of 15 secs)
            time.sleep(60)

        except socket.gaierror, e:
            print "%s There was a socket.gaierror: %s" % (e, str(datetime.now()))
            time.sleep(15)
        except socket.error, e:
            print "%s There was a socket.error: %s" % (e, str(datetime.now()))
            time.sleep(15)
        except (SystemExit):
            raise

