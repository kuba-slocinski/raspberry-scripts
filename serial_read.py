#!/usr/bin/env python2
import serial,os

# todo:
# - set nice to higher
# - 
node_exporter_file = '/var/lib/node_exporter/textfile_collector/serial.prom'

# define summary vars
# co_temp_set
# co_temp_actual
# co_feeder_state
co_feeder_sum_secs = 0
reads = 0
# co_blower_speed
# co_secs_to_feed

# read old values from node_exporter file if exists:
with open(node_exporter_file, 'r') as f:
  d = {}
  for line in f:
    (key, val) = line.split()
    d[key] = val
  if 'co_feeder_sum_secs' in d.keys():
    co_feeder_sum_secs = int(d['co_feeder_sum_secs'])

# store data for NodeExporter
def dump_data(data):
  with open(node_exporter_file+'.tmp', 'w') as f:
    f.writelines(["co_temp_set %s\n" % data[2],
    "co_temp_actual %s\n" % data[3],
    "co_secs_to_feed %s\n" % data[7],
    "co_feeder_sum_secs %s\n" % co_feeder_sum_secs])
  os.rename(node_exporter_file+'.tmp', node_exporter_file)
  f.close

#def reset_feeder_sum():
#  # sth
#  print()

with serial.Serial('/dev/ttyUSB0', 9600) as ser:
    while True:
        line = ser.readline()
        reads += 1
        # line exmaple:
        # 14: 47; 53; 53; 56;  2;  1; 20;    0;  144; 1280;  210; 27;255; 27; 26; 1236
        data = line.strip().split(';')
        print(line.strip())
        # copy vars:
        co_temp_set = data[2]
        co_temp_actual = data[3]
        co_feeder_state = data[5]
        co_blower_speed = data[6]
        co_secs_to_feed = data[7]

        co_feeder_sum_secs += int(co_feeder_state)
        print(data[2]+' '+data[3]+' '+data[5]+' '+data[6]+' '+data[7])

        # dump data each 60s:
        if reads == 60:
          print("storing data..")
          dump_data(data)
          reads = 0
