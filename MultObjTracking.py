import numpy as np 
import cv2
from tracker import Tracker
import time
import imageio
from flirpy.camera.lepton import Lepton 

def FLIRFunc():
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
				 boundaries = ((0,0), (0,120), (160, 120), (160, 0))
				 boundaries = np.array(boundaries)
				 mask = np.zeros_like(image)
				 cv2.fillPoly(mask, [boundaries], (255, 255, 255))#if enter is pressed and nothing has been pressed then the mask is the frame 
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
		
		def circleBlobs(c, frame): #draw circles at blob on image
			if len(c) > 0: #if there are blob
				for i in range(len(c)): #for each blob
			 	   cv2.circle(frame, (c[i][0], c[i][1]), 10, (255, 0, 0), 2) #draw circle at center of blob
				simpleblob = frame
			else:
				simpleblob = frame
			return simpleblob 
		prev_position = []
		FirstRunTest = True
		tracker = Tracker(20, 10, 5) #distance thresh, max frame skipped, max trace length
		while(True):
			frame = createimage(512,512) #blank image to put labeled blobs 
			img = camera.grab().astype(np.float32) #get image from FLIR
			T, threshold = cv2.threshold(img, 30400, 50000, cv2.THRESH_BINARY) #threshold the temp 
			img2 = 255*(img - img.min())/(img.max()-img.min()) 
			imgu = img2.astype(np.uint8)
		
			if FirstRunTest is True and imgu is not None: #if there is an image and its the first time through the loop
				masku = select_roi(imgu) 
				mask = masku.astype(np.float32)
				FirstRunTest = False
			if FirstRunTest is False and masku is not None:
				masked = cv2.bitwise_and(threshold, mask) #merge threshold and mask once created by select_roi

			masked2 = masked.astype(np.uint8)
			centers = detect_objects(masked2)
			masked3 = cv2.cvtColor(masked2, cv2.COLOR_GRAY2RGB)
			masked3 = circleBlobs(centers, masked3)
		
			track_colors = [(0, 255, 0), (0, 0, 255), (255, 255, 0), (127, 127, 255), (255, 0, 255), (255, 127, 255), (127, 0, 255), (127, 0, 127),(127, 10, 255), (0,255, 127)] #got rid of red so that can tell when crashes

		
			thresh = 2 #how much can the blob move for it to not think its a crash
		
			i = len(centers) # number of blobs
		
			if i > 0: #if there are any blobs 
				tracker.update(centers) #update the tracker with the blob locations 
			
				for j in range(len(tracker.tracks)): #len(tracker.tracks) is the number of blobs
					#print(tracker.tracks[j].trace) #example: deque([array([[68.92307692, 52.76923077]])], maxlen=20) 
					if (len(tracker.tracks[j].trace) > 1): 
						x = int(tracker.tracks[j].trace[-1][0,0]) #idea: rename these to x1 and y1
						y = int(tracker.tracks[j].trace[-1][0,1])
						tl = (x-10,y-10) #starting coordinates of rectangle 
						br = (x+10,y+10) #ending coordinates of rectangle
						cv2.rectangle(frame,tl,br,track_colors[j],1) #draw rectangle 
						cv2.putText(frame,str(tracker.tracks[j].trackId), (x-10,y-20),0, 0.5, track_colors[j],2) #label with which blob number
						if len(prev_position) < len(tracker.tracks):
							prev_position.append(None)
						if prev_position[j] is not None:
							if abs(prev_position[j][0]-x) < thresh and abs(prev_position[j][1] - y) < thresh:
								print(f'Bike {tracker.tracks[j].trackId} has crashed')
							else:
								print(f'Bike {tracker.tracks[j].trackId} is chilling')
						prev_position[j] = (x, y)
						
						for k in range(len(tracker.tracks[j].trace)):
							x2 = int(tracker.tracks[j].trace[k][0,0]) #idea compare to the x and y above and if they are the same its a crash?
							y2 = int(tracker.tracks[j].trace[k][0,1])
							cv2.circle(frame,(x2,y2), 3, track_colors[j],-1)
						cv2.circle(frame,(x2,y2), 6, track_colors[j],-1)
					for n in range(i):
						cv2.circle(frame, (centers[n][0], centers[n][1]), 6, (0,0,0),-1)
			cv2.imshow('image',frame)
			cv2.imshow("blobed", masked3)

    
    # Wait for the user to press a key (110ms delay).
			k = cv2.waitKey(110)

    # If the user presses the Escape key (key code 27), exit the loop.
			if k == 27:
				return

  
