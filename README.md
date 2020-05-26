* Control software for using the Arducam Pan-Tilt-Zoom module with the RaspiMJPEG module.
* See: https://www.arducam.com/product/arducam-ptz-pan-tilt-zoom-camera-raspberry-pi/

* The vendor supplied software is set up to work locally only with the picamera interface.
* This software adapts and expands that software to work with the RaspiMJPEG software module instead
so that it will work in the RPi_Cam_Web_Interface web-based interface.

## PTZ_control.py
* Main program to control the Arducam Pan Tilt Zoom focusing and IR module with RPi_Web_Cam_Interface
* Run this at boot (e.g. from /etc/rc.local) with "python PTX_control.py &"

## PTZ_RaspiMJPEG_Autofocus.py
* Support autofocusing with the Arducam PTZ module used with RPi_Cam_Web_Interface.

## www/html/userbuttons
* Define control buttons for the RPi_Web_Cam_Interface

## www/html/macros/*.sh
* Macro shell scripts to send commands to PTZ_control.py

-------
## Arducam Hardware Connection
![Alt text](https://github.com/ArduCAM/PTZ-Camera-Controller/blob/master/data/HardwareConnection.png)
## Focuser.py
* zoom-lens basic control component.

## AutoFocus.py
* Provide two autofocus methods are available, depending on Focuser.py, opencv, picamera
* Use the `sudo apt-get install python-opencv` command to install opencv.

## AutoFocusExample.py
* Example of using autofocus, depending on AutoFocus.py

## FocuserExample.py
* zoom-lens controller.

## Download the source code 
```bash
git clone https://github.com/ArduCAM/PTZ-Camera-Controller.git
```
## Run the FocuserExample.py
```bash
  cd PTZ-Camera-Controller/pyCode
  python FocuserExample.py
```

![Alt text](https://github.com/ArduCAM/PTZ-Camera-Controller/blob/master/data/Arducam%20Controller.png)

### Refer to this link to get more information about the PTZ-Camera-Controller
```bash
http://www.arducam.com/docs/cameras-for-raspberry-pi/ptz-camera/
```
