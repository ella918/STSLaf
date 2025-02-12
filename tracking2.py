import cv2
import numpy as np
from flirpy.camera.lepton import Lepton 
import KalmanFilter
from KalmanFilter import KalmanFilter

with Lepton() as camera:
	camera.setup_video() #use Lepton camera
	def select_roi(image): #roi function
		image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB) #change image to color so that the dots show up 
		roi_points = [] #empty array of points
		def mouse_callback(event, x, y, flags, param): #defining mouse function
			if event == cv2.EVENT_LBUTTONDOWN: #if clicked add circle where clicked and show image
				roi_points.append((x, y))
				cv2.circle(image, (x, y), 5, (0, 255, 0), -1)
				cv2.imshow("Select ROI", image)
		cv2.imshow("Select ROI", image) #show image without circles
		cv2.setMouseCallback("Select ROI", mouse_callback) #do clicks and make circles
		cv2.waitKey(0) #close window when esc pressed
		cv2.destroyAllWindows()
		image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY) #convert back to gray image
	
		if len(roi_points) > 2: #if more than 2 roi points
			roi_points = np.array(roi_points) #create array of roi points
			mask = np.zeros_like(image) #create mask of zeros same size as image
			cv2.fillPoly(mask, [roi_points], (255, 255, 255)) #fill mask outside of roi points
			return mask #return the mask
		else:
			mask = np.ones_like(image) #create mask of ones the same as the image
			return mask #return the mask 
			
	def detect_objects(frame): #detecting objects function
		circles = [] #empty list of box coordinates 
		contours, hier = cv2.findContours(frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) #find contours in given frame 
		for c in contours: #go through each contour
			mask = np.zeros_like(frame)
			# Check if the contour area is larger than a threshold.
			if cv2.contourArea(c) > 90: #if contour is big enough 
				# Get the bounding circle coordinates.
				cv2.fillPoly(mask, [c], 1)
				M = cv2.moments(mask)
				x = int(M["m10"] / M["m00"])
				y = int(M["m01"] / M["m00"]) 
				circles.append((x, y)) #add coords to the circle coordinate list
		circles = np.array(circles)
		return circles #return list of coordinates 
		
	def circleBlobs(c, frame):
		if len(c) > 0:
			for i in range(len(c)):
			    cv2.circle(frame, (c[i][0], c[i][1]), 10, (255, 0, 0), 2)
			simpleblob = frame
		else:
			simpleblob = frame
		return simpleblob

	FirstRunTest = True
	KF = KalmanFilter(0.1, 1, 1, 1, 0.1, 0.1)
	
	while(True):
		
		img = camera.grab().astype(np.float32)
		T, threshold = cv2.threshold(img, 30050, 50000, cv2.THRESH_BINARY)
		img2 = 255*(img - img.min())/(img.max()-img.min())
		imgu = img2.astype(np.uint8)
		
		if FirstRunTest is True and imgu is not None:
			masku = select_roi(imgu)
			mask = masku.astype(np.float32)
			FirstRunTest = False
		if FirstRunTest is False:
			masked = cv2.bitwise_and(threshold, mask)
		#cv2.imshow('mask', masked)
		masked2 = masked.astype(np.uint8)
		circles = detect_objects(masked2)
		masked3 = cv2.cvtColor(masked2, cv2.COLOR_GRAY2RGB)
		masked3 = circleBlobs(circles, masked3)
		if len(circles) > 0:
			for i in range(len(circles)):
				(x, y) = KF.predict() #predict where it is going
				cv2.rectangle(masked3, (int(x-15), int(y-15), (int(x + 15)), int(y+15)), (255, 0, 0, 2)) # draw rectangle at predicted pos
				(x1, y1) = KF.update(circles[i]) #update NEED TO FIX WHAT THIS IS OUTPUTTING I THINK THE FUNCTION HAS AN ERROR SOMEWHERE BC CIRCLES[I] LOOKS RIGHT 
				cv2.rectangle(masked3, (int(x1 - 15), int(y1 - 15)), (int(x1 + 15), int(y1 + 15)), (0, 0, 255), 2) #draw rectangle at estimated pos
				cv2.putText(masked3, "Estimated Position", (int(x1 + 15), int(y1 + 10)), 0, 0.5, (0, 0, 255), 2)
				cv2.putText(masked3, "Predicted Position", (int(x + 15), int(y)), 0, 0.5, (255, 0, 0), 2)
			
		blobcopy = cv2.resize(masked3, (1000,600))
		blobcopy2 = cv2.flip(blobcopy, 0)
		cv2.imshow('Blobs Tracked', blobcopy2)

    # Wait for the user to press a key (110ms delay).
		k = cv2.waitKey(110)

    # If the user presses the Escape key (key code 27), exit the loop.
		if k == 27:
			break
    
