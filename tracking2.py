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
			# Check if the contour area is larger than a threshold.
			if cv2.contourArea(c) > 90: #if contour is big enough 
				# Get the bounding circle coordinates.
				(x,y), radius = cv2.minEnclosingCircle(c) #find bounding circle coords and save 
				circles.append((x,y))) #add coords to the circle coordinate list
		if len(circles) > 0: #if there are any blobs
			circles = np.array(circles) #create an array out of the list
		return circles #return list of coordinates 



	FirstRunTest = True
	KF = KalmanFilter(0.1, 1, 1, 1, 0.1, 0.1)
	
	while(True):
		
		img = camera.grab().astype(np.float32)
		T, threshold = cv2.threshold(img, 30000, 50000, cv2.THRESH_BINARY)
		img2 = 255*(img - img.min())/(img.max()-img.min())
		imgu = img2.astype(np.uint8)
		
		if FirstRunTest is True and imgu is not None:
			masku = select_roi(imgu)
			mask = masku.astype(np.float32)
			FirstRunTest = False
		if FirstRunTest is False:
			masked = cv2.bitwise_and(threshold, mask)
		cv2.imshow('mask', masked)
		masked2 = masked.astype(np.uint8)
		detections = detect_objects(masked2)
		if len(detections) > 0:
			cv2.circle(masked2, (int(circles[0][0]), int(circles[0][0])), 10, (0,191,255), 2) #draw circle around blob
			(x, y) = KF.predict() #predict where it is going
			cv2.rectangle(masked2, (int(x-15), int(y-15), (int(x + 15)), int(y+15)), (255, 0, 0, 2)) # draw rectangle at predicted pos
			(x1, y1) = KF.update(circles[0]) #update
			cv2.rectangle(masked2, (int(x1 - 15), int(y1 - 15)), (int(x1 + 15), int(y1 + 15)), (0, 0, 255), 2) #draw rectangle at estimated pos
			cv2.putText(frame, "Estimated Position", (int(x1 + 15), int(y1 + 10)), 0, 0.5, (0, 0, 255), 2)
			cv2.putText(frame, "Predicted Position", (int(x + 15), int(y)), 0, 0.5, (255, 0, 0), 2)
			cv2.putText(frame, "Measured Position", (int(centers[0][0] + 15), int(centers[0][1] - 15)), 0, 0.5, (0,191,255), 2)
			


		
		#cv2.imshow('Blobs Tracked', masked2)

    # Wait for the user to press a key (110ms delay).
		k = cv2.waitKey(110)

    # If the user presses the Escape key (key code 27), exit the loop.
		if k == 27:
			break
    
