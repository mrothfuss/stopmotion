#!/usr/bin/python
 
import RPi.GPIO as GPIO
import datetime

import os
import time
import glob
import sys
import shutil
import subprocess

from threading import Thread
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
	PLAYBACK = 3

program_state = STATE.PENDING
live_process = False
sfx_process = False
overlay_thread = False

def play_sfx(path):
	global sfx_process

	if(sfx_process):
		sfx_process.kill()
		sfx_process = False

	sfx_process = subprocess.Popen(["aplay", path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL)

def find_vlc_capture():
	snapshot_dir = os.path.expanduser("~")
	prefix = "vlcsnap-"
	ext = ".png"
	sleep_duration = 0.05

	pattern = os.path.join(snapshot_dir, f"{prefix}*{ext}")
	slept=0
	while slept<5:
		files = glob.glob(pattern)

		if files:
			latest_file = max(files, key=os.path.getmtime)
			return latest_file
		time.sleep(sleep_duration)
		slept = slept + sleep_duration
	return ""

def update_overlay_thread():
	global live_process
	global project_frame

	if not live_process:
		return
	
	if project_frame == 0:
		return
	
	while True:
		draw_frame = project_frame

		last_img="%s/frame_%05d.png" % (project_dir, draw_frame)
		overlay_img="%s/overlay.png" % (project_dir)
		subprocess.run(["magick", last_img, "-gravity", "Center" , "-crop", "1440x806+0+0", "+repage", overlay_img])
		
		if project_frame == draw_frame:
			if live_process:
				live_process.stdin.write(b"logo_update\n")
				live_process.stdin.flush()
			return


def update_overlay():
	global overlay_thread

	if overlay_thread:
		if overlay_thread.is_alive():
			return
		overlay_thread.join()
	
	overlay_thread = Thread(target = update_overlay_thread)
	overlay_thread.start()

def capture_frame():
	global live_process
	global project_frame

	if not live_process:
		return

	play_sfx("./assets/camera-shutter.wav")
	live_process.stdin.write(b"snapshot\n")
	live_process.stdin.flush()
	last_img = find_vlc_capture()

	if last_img == "":
		return

	project_frame = project_frame + 1
	new_img="%s/frame_%05d.png" % (project_dir, project_frame)
	shutil.move(last_img, new_img)
	update_overlay()

def start_live_stream():
	global project_frame
	global live_process

	print("START STREAM")
	overlay_img="%s/overlay.png" % (project_dir)
	shutil.copy("./assets/blank-overlay.png", overlay_img)
	subprocess.run(["v4l2-ctl", "--set-ctrl", "auto_exposure=1,focus_automatic_continuous=0"])
	live_process = subprocess.Popen(["cvlc", "-I", "luaintf", "--lua-intf", "stopmotion", "--sub-filter", "logo", "--logo-file", overlay_img, \
		"--logo-opacity", "127", "--logo-position", "0", "v4l2:///dev/video0", \
		"--video-filter=transform", "--transform-type=180"], \
		stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, stdin=subprocess.PIPE)
	update_overlay()
	subprocess.run(["v4l2-ctl", "--set-ctrl", "focus_absolute=240,saturation=80,brightness=30,contrast=64,zoom_absolute=4"])

	return

def stop_live_stream():
	global live_process

	if(live_process):
		live_process.kill()
		live_process = False

def restart_live_stream():
	stop_live_stream()
	start_live_stream()

def compile_frames():
	framerate=12
	frame_template="%s/frame_%%05d.png" % (project_dir)
	preview_mp4 = "%s/video.mp4" % (project_dir)
	subprocess.run(["ffmpeg", "-y", "-framerate", str(framerate), "-i", frame_template, "-c:v", "h264_v4l2m2m", "-b:v", "2M", preview_mp4])

def play_video():
	preview_mp4 = "%s/video.mp4" % (project_dir)
	live_process = subprocess.Popen(["cvlc", "--play-and-exit", "-I", "luaintf", "--lua-intf", "stopmotion",  \
		preview_mp4, "--video-filter=transform", "--transform-type=180"], \
		stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, stdin=subprocess.PIPE)
	live_process.wait()

def change_state(next_state):
	global program_state

	if(program_state == STATE.PENDING):
		if(next_state == STATE.LIVE):
			program_state = STATE.LIVE
			start_live_stream()
	if(program_state == STATE.LIVE):
		if(next_state == STATE.CAPTURE):
			capture_frame()
		if(next_state == STATE.PENDING):
			stop_live_stream()
			program_state = STATE.PENDING
		if(next_state == STATE.PLAYBACK):
			compile_frames()
			stop_live_stream()
			program_state = STATE.PLAYBACK
			play_video()
			program_state = STATE.LIVE
			start_live_stream()

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
		change_state(STATE.PLAYBACK)
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
	vlc_lua_intf_dir = os.path.expanduser("~/.local/share/vlc/lua/intf")
	shutil.copy("./vlc/stopmotion.lua", vlc_lua_intf_dir)
	os.makedirs(vlc_lua_intf_dir, exist_ok=True)
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
