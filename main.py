#!/usr/bin/python
 
import RPi.GPIO as GPIO
import datetime

import os
import time
import glob
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
live_process = False

def find_vlc_capture():
	snapshot_dir = os.path.expanduser("~")
	prefix = "vlcsnap-"
	ext = ".png"

	pattern = os.path.join(snapshot_dir, f"{prefix}*{ext}")
	i=1
	while i<5:
		files = glob.glob(pattern)

		if files:
			latest_file = max(files, key=os.path.getmtime)
			return latest_file
		time.sleep(1)
		i = i + 1
	return ""

def update_overlay():
	global project_frame

	last_img="%s/frame_%05d.png" % (project_dir, project_frame)
	overlay_img="%s/overlay.png" % (project_dir)
	#subprocess.run(["magick", last_img, "-gravity", "Center" , "-crop", "1440x806+0+0", "-rotate", "180", "+repage", overlay_img])
	subprocess.run(["magick", last_img, "-gravity", "Center" , "-crop", "1440x806+0+0", "+repage", overlay_img])
	print("Created new overlay from %s" % last_img)

def capture_frame():
	global live_process
	global project_frame

	if not live_process:
		return

	live_process.stdin.write(b"snapshot\n")
	live_process.stdin.flush()
	last_img = find_vlc_capture()

	if last_img == "":
		return

	project_frame = project_frame + 1
	new_img="%s/frame_%05d.png" % (project_dir, project_frame)
	print("MOVE %s to %s" % (last_img, new_img))
	shutil.move(last_img, new_img)
	update_overlay()
	live_process.stdin.write(b"next\n")
	live_process.stdin.flush()

def start_live_stream():
	global project_frame
	global live_process

	print("START STREAM")
	update_overlay()
	overlay_img="%s/overlay.png" % (project_dir)
	live_process = subprocess.Popen(["cvlc", "--extraintf", "rc", "--sub-filter", "logo", "--logo-file", overlay_img, \
		"--logo-opacity", "127", "--logo-position", "0", "v4l2:///dev/video0", \
		"--video-filter=transform", "--transform-type=180"], \
		stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, stdin=subprocess.PIPE)
	#cvlc --extraintf rc --sub-filter logo --logo-file overlay.png --logo-opacity 50 --logo-x 80 --logo-y 45 v4l2:///dev/video0
	# + snapshot

	# nvlc --sub-filter logo --logo-file overlay.png --logo-opacity 50 --logo-x 80 --logo-y 45 v4l2:///dev/video0 --video-filter=transform --transform-type=180

	return

def stop_live_stream():
	global live_process

	if(live_process):
		live_process.kill()
		live_process = False

def restart_live_stream():
	stop_live_stream()
	start_live_stream()

def change_state(next_state):
	global program_state

	if(program_state == STATE.PENDING):
		if(next_state == STATE.LIVE):
			program_state = STATE.LIVE
			start_live_stream()
	if(program_state == STATE.LIVE):
		if(next_state == STATE.CAPTURE):
			capture_frame()
			#restart_live_stream()
		if(next_state == STATE.PENDING):
			stop_live_stream()
			program_state = STATE.PENDING

def restore_project_frame():
	global project_frame

	i=1
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
		change_state(STATE.CAPTURE)
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

	change_state(STATE.PENDING)
 
finally:
    GPIO.cleanup()
 
print("Goodbye!")
