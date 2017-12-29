#!/bin/bash

NAME=input

if [ -z "`screen -ls | grep $NAME`" ]; then
  /usr/bin/screen -d -m -S $NAME /usr/bin/python /home/kuba/scripts/$NAME\.py
else
  echo "script $NAME already started on screen. Skipping." > /dev/null
fi
