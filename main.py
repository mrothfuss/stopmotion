#!/usr/bin/python
 
import RPi.GPIO as GPIO
import datetime

import os
import sys
import shutil
import subprocess

from enum import Enum

# nvlc v4l2:///dev/video0

# Configuration
capture_dir="./recordings"
project_dir="%s/current" % capture_dir
project_frame=0

class STATE(Enum):
	PENDING = 0
	LIVE = 1
	CAPTURE = 2

program_state = STATE.PENDING

def capture_frame():
	global project_frame

	project_frame = project_frame + 1
	last_img="%s/last_001.png" % project_dir
	subprocess.run(["ffmpeg", "-f", "v4l2", "-i", "/dev/video0", "-frames:v", "1", "%s/last_%%03d.png" % project_dir])
	new_img="%s/frame_%05d.png" % (project_dir, project_frame)
	shutil.move(last_img, new_img)

def start_live_stream():
	return

def stop_live_stream():
	return

def change_state(next_state):
	global program_state

	if(program_state == STATE.PENDING):
		if(next_state == STATE.LIVE):
			program_state = STATE.LIVE
			start_live_stream()
	if(program_state == STATE.LIVE):
		if(next_state == STATE.CAPTURE):
			stop_live_stream()
			program_state = STATE.CAPTURE
			capture_frame()
			program_state = STATE.LIVE
			start_live_stream()
			


def restore_project_frame():
	global project_frame

	i=0
	while i<1000000:
		test_img="%s/frame_%05d.png" % (project_dir, i)
		if os.path.exists(test_img):
			project_frame = i
		else:
			return
		i = i + 1
	print("Could not determine frame index")
	sys.exit(1)
	


# GPIO 18
def btn_white(channel):
	if GPIO.input(channel) == GPIO.LOW:
		print("White ▼  at " + str(datetime.datetime.now()))
		capture_frame()
	else:
		print("White  ▲ at " + str(datetime.datetime.now()))
# GPIO 17
def btn_yellow(channel):
	if GPIO.input(channel) == GPIO.LOW:
		print("Yellow ▼  at " + str(datetime.datetime.now()))
	else:
		print("Yellow  ▲ at " + str(datetime.datetime.now()))
# GPIO 23
def btn_green(channel):
	if GPIO.input(channel) == GPIO.LOW:
		print("Green ▼  at " + str(datetime.datetime.now()))
	else:
		print("Green  ▲ at " + str(datetime.datetime.now()))
# GPIO 24
def btn_red(channel):
	if GPIO.input(channel) == GPIO.LOW:
		print("Red ▼  at " + str(datetime.datetime.now()))
	else:
		print("Red  ▲ at " + str(datetime.datetime.now()))
# GPIO 12
def btn_blue(channel):
	if GPIO.input(channel) == GPIO.LOW:
		print("Blue ▼  at " + str(datetime.datetime.now()))
	else:
		print("Blue  ▲ at " + str(datetime.datetime.now()))
# GPIO 16
def btn_black(channel):
	if GPIO.input(channel) == GPIO.LOW:
		print("Black ▼  at " + str(datetime.datetime.now()))
	else:
		print("Black  ▲ at " + str(datetime.datetime.now()))


try:
	os.makedirs(capture_dir, exist_ok=True)
	os.makedirs(project_dir, exist_ok=True)
	restore_project_frame()

	GPIO.setmode(GPIO.BCM)
	GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_UP)
	GPIO.add_event_detect(18, GPIO.BOTH, callback=btn_white, bouncetime=50)
	GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP)
	GPIO.add_event_detect(17, GPIO.BOTH, callback=btn_yellow, bouncetime=50)
	GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_UP)
	GPIO.add_event_detect(23, GPIO.BOTH, callback=btn_green, bouncetime=50)
	GPIO.setup(24, GPIO.IN, pull_up_down=GPIO.PUD_UP)
	GPIO.add_event_detect(24, GPIO.BOTH, callback=btn_red, bouncetime=50)
	GPIO.setup(12, GPIO.IN, pull_up_down=GPIO.PUD_UP)
	GPIO.add_event_detect(12, GPIO.BOTH, callback=btn_blue, bouncetime=50)
	GPIO.setup(16, GPIO.IN, pull_up_down=GPIO.PUD_UP)
	GPIO.add_event_detect(16, GPIO.BOTH, callback=btn_black, bouncetime=50)

	change_state(STATE.LIVE)

	message = input('\nPress Enter to exit.\n')
 
finally:
    GPIO.cleanup()
 
print("Goodbye!")
