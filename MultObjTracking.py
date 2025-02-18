import numpy as np 
import cv2
from tracker import Tracker
import time
import imageio
from flirpy.camera.lepton import Lepton 

with Lepton() as camera:
	camera.setup_video() #use Lepton camera
	def select_roi(image): #roi function NEED TO ADD THAT IF ENTER IS PRESSED YOU DON'T HAVE TO PICK ROI
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
			mask = image #if enter is pressed and nothing has been pressed then the mask is the frame 
			return mask #return the mask 
			
	def createimage(w,h):
		size = (w,h,1)
		img = np.ones((w,h,3),np.uint8)*255
		return img
			
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
				circles.append([x, y]) #add coords to the circle coordinate list
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
	tracker = Tracker(10, 5, 5)
	while(True):
		frame = createimage(512,512)
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

		masked2 = masked.astype(np.uint8)
		centers = detect_objects(masked2)
		masked3 = cv2.cvtColor(masked2, cv2.COLOR_GRAY2RGB)
		masked3 = circleBlobs(centers, masked3)
		
		track_colors = [(0, 255, 0), (0, 0, 255), (255, 255, 0), (127, 127, 255), (255, 0, 255), (255, 127, 255), (127, 0, 255), (127, 0, 127),(127, 10, 255), (0,255, 127)] #got rid of red so that can tell when crashes
		
		
		i = len(centers)
		if i > 0:
		#	for n in range(i):
				#print(centers[n])
			tracker.update(centers)
			
			for j in range(len(tracker.tracks)): #len(tracker.tracks) is the number of blobs
				#print(tracker.tracks[j].trace) #example: deque([array([[68.92307692, 52.76923077]])], maxlen=20) 
				if (len(tracker.tracks[j].trace) > 1): 
					x = int(tracker.tracks[j].trace[-1][0,0]) #idea: rename these to x1 and y1
					y = int(tracker.tracks[j].trace[-1][0,1])
					tl = (x-10,y-10)
					br = (x+10,y+10)
					cv2.rectangle(frame,tl,br,track_colors[j],1)
					cv2.putText(frame,str(tracker.tracks[j].trackId), (x-10,y-20),0, 0.5, track_colors[j],2)
					for k in range(len(tracker.tracks[j].trace)):
						x = int(tracker.tracks[j].trace[k][0,0]) #idea compare to the x and y above and if they are the same its a crash?
						y = int(tracker.tracks[j].trace[k][0,1])
						cv2.circle(frame,(x,y), 3, track_colors[j],-1)
					cv2.circle(frame,(x,y), 6, track_colors[j],-1)
				for n in range(i):
					cv2.circle(frame, (centers[n][0], centers[n][1]), 6, (0,0,0),-1)
		cv2.imshow('image',frame)
		cv2.imshow("blobed", masked3)

    
    # Wait for the user to press a key (110ms delay).
		k = cv2.waitKey(110)

    # If the user presses the Escape key (key code 27), exit the loop.
		if k == 27:
			break

  
