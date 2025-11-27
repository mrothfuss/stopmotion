#!/usr/bin/python
 
import RPi.GPIO as GPIO
import datetime

# nvlc v4l2:///dev/video0
 
# GPIO 18
def btn_white(channel):
	if GPIO.input(channel) == GPIO.LOW:
		print("White ▼  at " + str(datetime.datetime.now()))
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
 
    message = input('\nPress Enter to exit.\n')
 
finally:
    GPIO.cleanup()
 
print("Goodbye!")
