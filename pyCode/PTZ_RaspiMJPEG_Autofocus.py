'''
    PTZ_RaspiMJPEG_Autofocus.py
    Adapted for use with RaspiMJPEG instead of picamera
    by Rick Hollinbeck
'''
'''
    Arducam programable zoom-lens autofocus component.

    Copyright (c) 2019-4 Arducam <http://www.arducam.com>.

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all
    copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
    EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
    MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
    IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
    DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
    OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
    OR OTHER DEALINGS IN THE SOFTWARE.
'''

import sys
import time
from Focuser import Focuser

try:
    import cv2 #sudo apt-get install python-opencv
    import numpy as np
except:
    print("PTZ_RaspiMJPEG_Autofocus(): import failed")
    sys.exit(0)

class PTZ_RaspiMJPEG_Autofocus:

    img_filename = "/dev/shm/mjpeg/cam.jpg"
    MAX_FOCUS_VALUE = 19500
    MJPEG_DELAY = 0.35 # Wait for RASPIMJPEG to update the image file
    value_buffer = []
    focuser = None
    debug = False
    last_RaspiMJPEG_image_time = 0

    def __init__(self,focuser):
        self.focuser = focuser
	self.last_RaspiMJPEG_image_time = 0

    def get_RaspiMJPEG_image(self):
	s = self.img_filename
#        if self.debug: print("get_RaspiMJPEG_image: %s" %(s))
        if self.debug: print("get_RaspiMJPEG_image()")
	if self.last_RaspiMJPEG_image_time > 0:
		dt = time.time() - self.last_RaspiMJPEG_image_time
		if dt < self.MJPEG_DELAY:
		        if self.debug: print("sleep: %lf"%(self.MJPEG_DELAY - dt))
		        # Wait a little bit to make sure raspimjpeg
	        	# has written a new image file.
			time.sleep(self.MJPEG_DELAY - dt)
	else:
	        # Wait a little bit to make sure raspimjpeg
        	# has written a new image file.
		time.sleep(self.MJPEG_DELAY)
        image = cv2.imread(s)
	self.last_RaspiMJPEG_image_time = time.time()
        width = image.shape[1]
        height = image.shape[0]
	#Look at the middle part of the image for focusing
        image = image[(height / 4):((height / 4) * 3),(width / 4):((width / 4) * 3)]
	return image

    def filter(self,value):
        max_len = 3
        self.value_buffer.append(value)
        if len(self.value_buffer) == max_len:
            sort_list = sorted(self.value_buffer)
   	    if self.debug:
		if len(self.value_buffer) == 1:
			print("filter() value_buffer(1): %lf" %(self.value_buffer[0]))
			print("filter() sort_list(1): %lf" %(sort_list[0]))
		elif len(self.value_buffer) == 2:
			print("filter() value_buffer(2): %lf,%lf" %(self.value_buffer[0],self.value_buffer[1]))
			print("filter() sort_list(2): %lf,%lf" %(sort_list[0],sort_list[1]))
		elif len(self.value_buffer) == 3:
			print("filter() value_buffer(3): %lf,%lf,%lf" %(self.value_buffer[0],self.value_buffer[1],self.value_buffer[2]))
			print("filter() sort_list(3): %lf,%lf,%lf" %(sort_list[0],sort_list[1],sort_list[2]))
            self.value_buffer.pop(0)
            return sort_list[max_len / 2]
        return value

    def sobel(self,img):
        img_gray = cv2.cvtColor(img,cv2.COLOR_RGB2GRAY)
        img_sobel = cv2.Sobel(img_gray,cv2.CV_16U,1,1)
        return cv2.mean(img_sobel)[0]

    def laplacian(self,img):
        img_gray = cv2.cvtColor(img,cv2.COLOR_RGB2GRAY)
        img_sobel = cv2.Laplacian(img_gray,cv2.CV_16U)
        return cv2.mean(img_sobel)[0]

    def laplacian2(self,img):
        img_gray = cv2.cvtColor(img,cv2.COLOR_RGB2GRAY) 
        img_sobel = cv2.Laplacian(img_gray,cv2.CV_64F).var()
#        return img_sobel
        return cv2.mean(img_sobel)[0]

    def calculation(self):
	image = self.get_RaspiMJPEG_image()
        #return self.laplacian(image)
        #return self.sobel(image)
#	if self.debug: print("calculation(): laplacian2")
        return self.laplacian2(image)

    def start_RaspiMJPEG_Autofocus(self):
	#Get focus range for the zoom.
        self.MAX_FOCUS_VALUE = self.focuser.end_point[int(self.focuser.get(Focuser.OPT_ZOOM)/1000)]
        starting_point = self.focuser.starting_point[int(self.focuser.get(Focuser.OPT_ZOOM)/1000)]
	focus = starting_point
        best_focus = focus
        max_value = 0.0
        last_value = -1
        dec_count = 0
#        step = 50
        step = (self.MAX_FOCUS_VALUE - starting_point) / 50
	if step <= 0: step = 1
	threshold = 1.0
	max_dec_count = 1
#	max_dec_count = 0
        focal_distance = best_focus
        if self.debug: print("\nstart_RaspiMJPEG_Autofocus() from %d to %d step %d" %(starting_point,self.MAX_FOCUS_VALUE,step))
	try:
		self.last_RaspiMJPEG_image_time = 0
		while focus < self.MAX_FOCUS_VALUE:
		        if self.debug: print("--> try focus %d" %(focus))
		        self.focuser.set(Focuser.OPT_FOCUS,focus)
		        #Take image and calculate image clarity
        		val = self.calculation()
		        if self.debug: print("calculation() = %lf" %(val))
			#Get median of last 3 values
#        		val = self.filter(val)
#		        if self.debug: print("filter() = %lf" %(val))
			#Find the maximum image clarity
			if val > max_value:
        	        	best_focus = focus
        	        	max_value = val
		        #If the image clarity starts to decrease
        	    	if last_value - val > threshold :
        	        	dec_count += 1
        	       		if self.debug: print("clarity decrease(%d): last_value = %lf,current_value = %lf"%(dec_count,last_value,val))
        	 	elif last_value - val != 0:
        	       		dec_count = 0
			#Check if image clarity is reduced by max_dec_count consecutive frames
		        if dec_count > max_dec_count:
		                if self.debug: print("getting blurry, so exiting loop (threshold=%d)" %(threshold))
		                break
        	        last_value = val
			focus = focus + step

        except Exception as e:
                e0 = sys.exc_info()[0]
                e1 = sys.exc_info()[1]
                print "Exception: "+str(e0)+" - "+str(e1)

	#Position at start value first
        self.focuser.set(Focuser.OPT_FOCUS,starting_point)
        while self.focuser.isBusy():
		time.sleep(.1)
#	time.sleep(5)
        if self.debug: print("start_RaspiMJPEG_Autofocus(): return best_focus=%d,max_value(clarity)=%lf" %(best_focus,max_value))
	#Position to the best focus value we found before returning
        self.focuser.set(Focuser.OPT_FOCUS,best_focus)
        while self.focuser.isBusy():
		time.sleep(.1)
#	time.sleep(5)
        return best_focus,max_value

    def focusing(self,step,threshold,max_dec_count):
        self.value_buffer = []
        max_index = self.focuser.get(Focuser.OPT_FOCUS)
	if self.debug: print("focusing(): max_index=%d" % (max_index))
        max_value = 0.0
        last_value = -1
        dec_count = 0
        # step = 200
        focal_distance = max_index
#        self.focuser.set(Focuser.OPT_FOCUS,focal_distance)
        while True:
            #Adjust focus
            self.focuser.set(Focuser.OPT_FOCUS,focal_distance)
            #Take image and calculate image clarity
            val = self.calculation()
            if self.debug: print("calculation() = %d" %(val))
            # print "calculation value:",val
            val = self.filter(val) # get average of last 3 values
            if self.debug: print("filter value = %d, focal_distance = %d"%(val,focal_distance))

            #Find the maximum image clarity
            if val > max_value:
                max_index = focal_distance
                max_value = val

            #If the image clarity starts to decrease
            if last_value - val > threshold :
                if self.debug: print("clarity decrease(%d): last_value = %lf,current_value = %lf"%(dec_count,last_value,val))
                dec_count += 1
            elif last_value - val != 0:
                dec_count = 0
            #Image clarity is reduced by six consecutive frames
            if dec_count > max_dec_count:
                if self.debug: print("blurry, so exiting loop (%d)"%(max_dec_count))
                break
            last_value = val

            #Increase the focal distance
            focal_distance = self.focuser.get(Focuser.OPT_FOCUS)
            focal_distance += step
            if focal_distance > self.MAX_FOCUS_VALUE:
                if self.debug: print("Hit maximum focus value (%d) at focal_distance=%d, so exiting loop"%(self.MAX_FOCUS_VALUE,focal_distance))
                break

	if self.debug:
            print("focusing(): return max_index(focus)=%d,max_value(clarity)=%d" % (max_index,max_value))
        return max_index,max_value

    def CoarseAdjustment(self,st_point,ed_point):
	focus_step = 100
        images = []
        index_list = []
        eval_list = []
        time_list = []
	if self.debug: print("CoarseAdjustment(st_point=%d,ed_point=%d)" % (st_point,ed_point))
#        while self.focuser.isBusy():
#		time.sleep(.1)
	if self.debug: print(" self.focuser.set(Focuser.OPT_FOCUS,%d)"%(st_point))
        self.focuser.set(Focuser.OPT_FOCUS,st_point)
#        rawCapture = PiRGBArray(self.camera) 
#        self.camera.capture(rawCapture,format="bgr", use_video_port=True)
#	if self.debug:
#            print(" t = time.time()")
	t = time.time()
#	if self.debug:
#            print(" time_list.append(%.3f)" % t)
       	time_list.append(t)
#	print "appended"
#	except:
#		print "except!!!"
#		e0,e1,e2 = sys.exc_info()
#		print e0+" - "+e1+" - "+e2
#	print "appended2"
	s = "/dev/shm/mjpeg/cam.jpg"
	if self.debug: print(" Ready to read img_filename=%s" % s)

	# Wait a little bit to make sure raspimjpeg
	# has written a new image file.
	time.sleep(self.MJPEG_DELAY)

#       image = rawCapture.array
	if self.debug: print(" image = cv2.imread(\"%s\")"%(s))
	try:
#		image = cv2.imread(IMG_FILENAME, cv2.IMREAD_COLOR)
	    image = cv2.imread(s)
	except:
	    e = sys.exc_info()[0]
	    print ("ERROR READING FIRST IMAGE: %s"%(str(e)))
	    raise

        images.append(image)
#        rawCapture.truncate(0)

	# Gather a set of images while focusing to the max focus value

        # self.focuser.setFocusNoWait(self.focuser.end_point[int(self.focuser.getZoom()/1000)])
#        self.focuser.set(Focuser.OPT_FOCUS,ed_point,0)
#        while self.focuser.isBusy():
#            self.camera.capture(rawCapture,format="bgr", use_video_port=True)
        focus = self.focuser.get(Focuser.OPT_FOCUS) + focus_step
	while focus <= ed_point:
	    self.focuser.set(Focuser.OPT_FOCUS,focus)
	    while self.focuser.isBusy():
		pass

            time_list.append(time.time())
#            image = rawCapture.array
	    # Wait a little bit to make sure raspimjpeg
	    # has written a new image file.
	    time.sleep(self.MJPEG_DELAY)
#	    image = cv2.imread(IMG_FILENAME, cv2.IMREAD_COLOR)
	    if self.debug:
                print(" coarse focusing read image %d" % len(images))
            image = cv2.imread(s)
            images.append(image)
#            rawCapture.truncate(0)
            focus = self.focuser.get(Focuser.OPT_FOCUS) + focus_step

        total_time = time_list[len(time_list) - 1] - time_list[0]
        index_list = np.arange(len(images))
        last_time = time_list[0]
        if self.debug:
            print("total images = %d"%(len(images)))
            print("total time = %.3f"%(total_time))
        for i in range(len(images)):
            image = images.pop(0)
            width = image.shape[1]
            height = image.shape[0]
            image = image[(height / 4):((height / 4) * 3),(width / 4):((width / 4) * 3)]
            result = self.laplacian2(image)
	    if self.debug: print("CoarseAdjustment laplacian2 %d=%.3f"%(i,result))
            eval_list.append(result)
        return eval_list,index_list,time_list

    def startFocus(self):
        begin = time.time()
        self.focuser.reset(Focuser.OPT_FOCUS)
        self.MAX_FOCUS_VALUE = self.focuser.end_point[int(self.focuser.get(Focuser.OPT_ZOOM)/1000)]
        self.focuser.set(Focuser.OPT_FOCUS,self.focuser.starting_point[int(self.focuser.get(Focuser.OPT_ZOOM)/1000)])
        if self.debug: print("startFocus: init time = %lf"%(time.time() - begin))
        begin = time.time()
        max_index,max_value = self.focusing(300,1,1)
        # focuser.setFocus(0)
        self.focuser.set(Focuser.OPT_FOCUS,max_index - 300 * (2) - 30)
        # Careful adjustment
        max_index,max_value = self.focusing(50,1,4)
        self.focuser.set(Focuser.OPT_FOCUS,max_index - 30)
        if self.debug: print("focusing time = %lf"%(time.time() - begin))
        return max_index,max_value

    def startFocus2(self):
        begin = time.time()
        self.focuser.reset(Focuser.OPT_FOCUS)
        self.MAX_FOCUS_VALUE = self.focuser.end_point[int(self.focuser.get(Focuser.OPT_ZOOM)/1000)]
        starting_point = self.focuser.starting_point[int(self.focuser.get(Focuser.OPT_ZOOM)/1000)]
        if self.debug: print("startFocus2 init reset time = %lf"%(time.time() - begin))
        begin = time.time()
        if self.debug: print("startFocus2 CoarseAdjustment = focus from %d to %d"%(starting_point,self.MAX_FOCUS_VALUE))
        eval_list,index_list,time_list = self.CoarseAdjustment(starting_point,self.MAX_FOCUS_VALUE)
        max_index = np.argmax(eval_list)
        total_time = time_list[len(time_list) - 1] - time_list[0]
        max_time = time_list[max_index - 1] - time_list[0]
        self.focuser.set(Focuser.OPT_FOCUS,int(((max_time - 0.0)/total_time)*(self.MAX_FOCUS_VALUE - starting_point)) + starting_point)
        if self.debug: print("startFocus2 max_index=%d total_time=%lf max_time=%lf"%(max_index,total_time,max_time))
        # Careful adjustment
        if self.debug: print("startFocus2 fine focusing(50,1,4)")
        max_index,max_value = self.focusing(50,1,4)
        if self.debug: print("startFocus2 finished: max_index(focus)=%d max_value(clarity)=%lf"%(max_index,max_value))
        self.focuser.set(Focuser.OPT_FOCUS,max_index - 30)
        if self.debug: print("startFocus2 focusing time = %lf"%(time.time() - begin))
        return max_index,max_value

    def auxiliaryFocusing(self):
        begin = time.time()
        self.focuser.reset(Focuser.OPT_FOCUS)
        self.MAX_FOCUS_VALUE = self.focuser.end_point[int(self.focuser.get(Focuser.OPT_ZOOM)/1000)]
        starting_point = self.focuser.starting_point[int(self.focuser.get(Focuser.OPT_ZOOM)/1000)]
        if self.debug: print("auxiliaryFocusing init time = %lf"%(time.time() - begin))
        begin = time.time()
        eval_list,index_list,time_list = self.CoarseAdjustment(starting_point,self.MAX_FOCUS_VALUE)
        max_index = np.argmax(eval_list)
        total_time = time_list[len(time_list) - 1] - time_list[0]
        max_time = time_list[max_index] - time_list[0]
        self.focuser.set(Focuser.OPT_FOCUS,int(((max_time - 0.0)/total_time)*(self.MAX_FOCUS_VALUE - starting_point)) + starting_point)
        if self.debug: print("focusing time = %lf"%(time.time() - begin))
        return max_index

pass
