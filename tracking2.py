import cv2
import numpy as np
from flirpy.camera.lepton import Lepton 
import trackerclass
from trackerclass import Tracker

with Lepton() as camera:
	camera.setup_video()
	def select_roi(image):
		image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
		roi_points = []
		def mouse_callback(event, x, y, flags, param):
			if event == cv2.EVENT_LBUTTONDOWN:
				roi_points.append((x, y))
				cv2.circle(image, (x, y), 5, (0, 255, 0), -1)
				cv2.imshow("Select ROI", image)
		cv2.imshow("Select ROI", image)
		cv2.setMouseCallback("Select ROI", mouse_callback)
		cv2.waitKey(0)
		cv2.destroyAllWindows()
		image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
	
		if len(roi_points) > 2:
			roi_points = np.array(roi_points)
			mask = np.zeros_like(image)
			cv2.fillPoly(mask, [roi_points], (255, 255, 255))
			return mask
		else:
			mask = np.ones_like(image)
			return mask
			
	def detect_objects(frame):
		bbox = []
		contours, hier = cv2.findContours(frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
		for c in contours:
			# Check if the contour area is larger than a threshold.
			if cv2.contourArea(c) > 90:
				# Get the bounding rectangle coordinates.
				[x, y, w, h] = cv2.boundingRect(c)
				bbox.append([x,y,w,h])
		return bbox

	def draw_bbox(frame):
		bbox = []
		contours, hier = cv2.findContours(frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
		for c in contours:
			mask = np.zeros_like(frame)
			contourSize = cv2.contourArea(c)
			# Check if the contour area is larger than a threshold.
			if cv2.contourArea(c) > 90:
				cv2.fillPoly(mask,[c],1)
				# draw rectangle coordinates.
				cv2.boundingRect(c)
		simpleblobcolor = cv2.cvtColor(frame, cv2.COLOR_GRAY2RGB)
		return simpleblobcolor


	blobs = []
	FirstRunTest = True
	
	while(True):
		img = camera.grab().astype(np.float32)
		T, threshold = cv2.threshold(img, 3000, 5000, cv2.THRESH_BINARY)
		img2 = 255*(img - img.min())/(img.max()-img.min())
		imgu = img2.astype(np.uint8)
		
		if FirstRunTest is True and imgu is not None:
			masku = select_roi(imgu)
			mask = masku.astype(np.float32)
			FirstRunTest = False
		if FirstRunTest is False:
			masked = cv2.bitwise_and(threshold, mask)
		masked2 = masked.astype(np.uint8)
		detections = detect_objects(masked2)
		simpleblob = draw_bbox(masked2)
		
		
		cv2.imshow('Blobs Tracked', simpleblob)

    # Wait for the user to press a key (110ms delay).
		k = cv2.waitKey(110)

    # If the user presses the Escape key (key code 27), exit the loop.
		if k == 27:
			break
    
