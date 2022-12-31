#!/bin/bash

xrandr --output HDMI-1 --mode 1920x1080

python3 /home/pi/rpi-picture-frame/main.py >> log.txt