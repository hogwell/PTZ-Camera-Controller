## Hardware Conncetion
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

### Refering the link to get more information about the PTZ-Camera-Controller
```bash
http://www.arducam.com/docs/cameras-for-raspberry-pi/ptz-camera/
```
-------
Added support for using the Pan-Tilt_Zoom module with the RaspiMJPEG module.

## PTZ_RaspiMJPEG_Autofocus.py
* Support autofocusing with the Arducam PTZ module used with RPi_Cam_Web_Interface.

