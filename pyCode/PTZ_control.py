#!/usr/bin/env python

# RPICam control program to control the Arducam PTZ camera.

# This processes commands sent through the FIFO pipe
#  from the website buttons.
# Commands include panning, tilting, focus, zoom, IR cut filter ON/OFF,
#  servo sleep and servo wake.

# By RickH

#import smbus
import time
import os
import errno
import threading
import sys

import RPi.GPIO as GPIO
#GPIO number for controlling the pantilt servo power. (GPIO17=Pin 11)
RELAY_GPIO = 17

#enable_autofocus = False
enable_autofocus = True

from Focuser import Focuser

try:
	from PTZ_RaspiMJPEG_Autofocus import PTZ_RaspiMJPEG_Autofocus

except Exception as e:
	e0 = sys.exc_info()[0]
	e1 = sys.exc_info()[1]
	print "Exception: "+str(e0)+" - "+str(e1)
	print "PTZ_control: import failed"
	sys.exit(0)

sleepTimer = 0
sleepTime = 10
asleep = False

# Set up a table of focus values for different zoom settings.
# This table is interpolated in focus_to_zoom() to approximate auto-focus while zooming.

def focus_to_zoom(zoom):

	zoom_settings = [
		15000, 14000, 13000, 12000, 11000, 10000, 9000,
		8000, 7000, 6000, 5000, 4000, 3000, 2000,
		1600,
		0
	    ]
	focus_settings = [
	        1870, 1988, 2182, 2405, 2880, 3552, 4300,
	        5096, 6560, 8112, 10068, 12548, 15180, 19080,
	        20000,
		0
	    ]

	i = 0
#	print "focus_to_zoom("+str(zoom)+")"
	while zoom < zoom_settings[i]:
#		print "i="+str(i)+",zoom_settings[i]="+str(zoom_settings[i])
		i += 1
	if zoom_settings[i] == 0: # out of range
		focus = 10000
		return focus
	ratio = 1.0 * (zoom - zoom_settings[i]) / (zoom_settings[i-1] - zoom_settings[i])
	focus = int(focus_settings[i] - ratio * (focus_settings[i] - focus_settings[i-1]))
#	print "zoom="+str(zoom)+",ratio="+str(ratio)+",focus=="+str(focus)
	return focus

def is_asleep():
        global asleep
#       print "is_asleep: " + str(asleep)
        return asleep

def servosleep():
        global asleep
        global sleepTimer
	global RELAY_GPIO
        sleepTimer = 0
#       print "servosleep()"
        GPIO.output(RELAY_GPIO, GPIO.LOW) # out
        asleep = True
#        fannotate = open('/dev/shm/mjpeg/user_annotate.txt', 'w')
#        fannotate.write('ASLEEP\n')
#        fannotate.close()

def servowake():
        global asleep
        global sleepTimer
	global RELAY_GPIO
        sleepTimer = 0
#       print "servowake()"
        GPIO.output(RELAY_GPIO, GPIO.HIGH) # on
        asleep = False
#        fannotate = open('/dev/shm/mjpeg/user_annotate.txt', 'w')
#        fannotate.write('AWAKE\n')
#        fannotate.close()

def scale(x, in_min, in_max, out_min, out_max):
	return (x - in_min)*(out_max - out_min)/(in_max - in_min) + out_min

def timer_thread(event):
        global sleepTimer
        global sleepTime
        while not event.is_set():
#               print "timer"
#	        fannotate = open('/dev/shm/mjpeg/user_annotate.txt', 'w')
#        	fannotate.write('timer:%3d' % sleepTimer)
#        	fannotate.close()
                if sleepTimer >= sleepTime:
                        if not is_asleep(): servosleep()
                        sleepTimer = 0
                elif not is_asleep(): sleepTimer = sleepTimer + 1
                time.sleep(1)
        print "timer_thread() done."

def annotate(focuser):
        fannotate = open('/dev/shm/mjpeg/user_annotate.txt', 'w')
        fannotate.write('F:%3.0f/Z:%3.0f' %(focuser.get(Focuser.OPT_FOCUS),focuser.get(Focuser.OPT_ZOOM)))
        fannotate.close()

def main():

	global sleepTimer
	global RELAY_GPIO

        focuser = Focuser(1)

#        focuser.reset(Focuser.OPT_FOCUS)
#        focuser.reset(Focuser.OPT_ZOOM)
	focuser.set(Focuser.OPT_ZOOM,4000)
#	focuser.set(Focuser.OPT_FOCUS,12300)
	focuser.set(Focuser.OPT_FOCUS,focus_to_zoom(4000))

        auto_focus = PTZ_RaspiMJPEG_Autofocus(focuser)
#	auto_focus.debug = True

	GPIO.setmode(GPIO.BCM) # GPIO Numbers instead of board numbers
	GPIO.setup(RELAY_GPIO, GPIO.OUT) # GPIO Assign mode

#	time.sleep(5)
	annotate(focuser)

	while True:

        	time.sleep(.1)  # delay a little for each loop

#		print "opening FIFO_pipan"
		pipein = open("/var/www/html/FIFO_pipan", 'r')
        	# Look for a command sent on the website's pipe
		line = pipein.readline()
		pipein.close()
		try:
	        	while line <> '':
	                	#debugging
	                	#print line

				line_array = line.split(' ')
				line = ''

				if line_array[0] == "servo":
					sleepTimer = 0
					if (is_asleep()):
						servowake()
						time.sleep(.2)
	#				print "servo set pantilt"
					pan_setting = scale(int(line_array[1]), 50, 250, 0xb4, 0)
					tilt_setting = scale(int(line_array[2]), 80, 220, 0, 0xb4)
					if focuser.get(Focuser.OPT_MOTOR_Y) != tilt_setting:
	                                	focuser.set(Focuser.OPT_MOTOR_Y, tilt_setting)
					if focuser.get(Focuser.OPT_MOTOR_X) != pan_setting:
		                                focuser.set(Focuser.OPT_MOTOR_X, pan_setting)
				elif line_array[0] == "focusplus":
	#				print "focus="+str(focuser.get(Focuser.OPT_FOCUS))+"+"+str(int(line_array[1]))
					focuser.set(Focuser.OPT_FOCUS,focuser.get(Focuser.OPT_FOCUS) + int(line_array[1]))
					annotate(focuser)
				elif line_array[0] == "focusminus":
	#				print "focus="+str(focuser.get(Focuser.OPT_FOCUS))+"-"+str(int(line_array[1]))
					focuser.set(Focuser.OPT_FOCUS,focuser.get(Focuser.OPT_FOCUS) - int(line_array[1]))
					annotate(focuser)
				elif line_array[0] == "autofocus":
					if enable_autofocus:
					        fannotate = open('/dev/shm/mjpeg/user_annotate.txt', 'w')
				        	fannotate.write('AUTOFOCUSING...\n')
					        fannotate.close()
					        best_focus,max_value = auto_focus.start_RaspiMJPEG_Autofocus()
	# focus has been set already:		focuser.set(Focuser.OPT_FOCUS,best_focus)
						#print "max_index="+str(max_index)+",max_value="+str(max_value)
					else:
						focuser.set(Focuser.OPT_FOCUS,focus_to_zoom(focuser.get(Focuser.OPT_ZOOM)))
					annotate(focuser)
				elif line_array[0] == "focuszoom":
					focuser.set(Focuser.OPT_FOCUS,focus_to_zoom(focuser.get(Focuser.OPT_ZOOM)))
					annotate(focuser)
				elif line_array[0] == "zoomto":
	#				print "zoomto="+str(int(line_array[1])
					zoom = int(line_array[1])
					if zoom < 2000: zoom = 2000
					if zoom > 15000: zoom = 15000
					focuser.set(Focuser.OPT_ZOOM,zoom)
					while focuser.isBusy(): pass
					#Force an autofocus next.
					line = "autofocus 0 0"
					annotate(focuser)
				elif line_array[0] == "zoomplus":
	#				print "zoomplus="+str(focuser.get(Focuser.OPT_ZOOM))+"+"+str(int(line_array[1]))
					zoom = focuser.get(Focuser.OPT_ZOOM) + int(line_array[1])
					if zoom > 15000: zoom = 15000
					focuser.set(Focuser.OPT_ZOOM,zoom)
					zoom = focuser.get(Focuser.OPT_ZOOM)
					focuser.set(Focuser.OPT_FOCUS,focus_to_zoom(zoom))
					annotate(focuser)
				elif line_array[0] == "zoomminus":
	#				print "zoomminus="+str(focuser.get(Focuser.OPT_ZOOM))+"-"+str(int(line_array[1]))
					zoom = focuser.get(Focuser.OPT_ZOOM) - int(line_array[1])
					if zoom < 2000: zoom = 2000
					focuser.set(Focuser.OPT_ZOOM,zoom)
					zoom = focuser.get(Focuser.OPT_ZOOM)
					focuser.set(Focuser.OPT_FOCUS,focus_to_zoom(zoom))
					annotate(focuser)
				elif line_array[0] == "ircutfilter":
	# 				print "IR="+str(int(line_array[1]))
	#			        focuser.set(Focuser.OPT_IRCUT,int(line_array[1]))
					# Toggle the Infrared cut filter
					if focuser.get(Focuser.OPT_IRCUT) == 1:
					        focuser.set(Focuser.OPT_IRCUT,0)
					else:
					        focuser.set(Focuser.OPT_IRCUT,1)
				elif line_array[0] == "servosleep":
					servosleep()
				elif line_array[0] == "servowake":
					servowake()

		except Exception as e:
			e0 = sys.exc_info()[0]
			e1 = sys.exc_info()[1]
			print "Exception: "+str(e0)+" - "+str(e1)

if __name__ == '__main__':
	try:
		event = threading.Event()
		timerThread = threading.Thread(target=timer_thread, args = (event,))
		timerThread.start()
		main()
		print "main() done."
	except KeyboardInterrupt:
		print "Ctrl-c pressed!"
	except Exception as e:
		e0 = sys.exc_info()[0]
		e1 = sys.exc_info()[1]
		print "Exception: "+str(e0)+" - "+str(e1)
	finally:
		print "finally..."
		event.set()
		time.sleep(2)	# let timer thread exit.
		sys.exit(1)
