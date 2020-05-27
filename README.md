Control software for using the Arducam Pan-Tilt-Zoom module with the RaspiMJPEG module.

See: https://www.arducam.com/product/arducam-ptz-pan-tilt-zoom-camera-raspberry-pi/

The vendor supplied software is set up to work locally only with the picamera interface.

This software adapts and expands that software to work with the RaspiMJPEG software module instead
so that it will work in the RPi-Cam-Web-Interface web-based camera control application.

See: https://github.com/silvanmelchior/RPi_Cam_Web_Interface

## PTZ_control.py
* Main program to control the Arducam Pan Tilt Zoom focusing and IR module with RPi-Cam-Web-Interface
* Run this in the background at boot as root (e.g. from /etc/rc.local) with "python PTZ_control.py &"

## PTZ_RaspiMJPEG_Autofocus.py
* Class that supports autofocusing the Arducam PTZ camera to be used with RPi-Cam-Web-Interface.

## www/html/userbuttons
* Defines control buttons for the RPi_Web_Cam_Interface web UI.

## www/html/macros/*.sh
* Macro shell scripts to send piped commands to PTZ_control.py

-------
## Arducam Hardware Connection
![Alt text](https://github.com/ArduCAM/PTZ-Camera-Controller/blob/master/data/HardwareConnection.png)

## Focuser.py
* zoom-lens basic control component.

### Refer to this link to get more information about the PTZ-Camera-Controller
```bash
http://www.arducam.com/docs/cameras-for-raspberry-pi/ptz-camera/
```
