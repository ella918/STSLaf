from __future__ import print_function 
import sys
import cv2 as cv
from random import randint 
import numpy as np 
from flirpy.camera.lepton import Lepton

trackerTypes = ['BOOSTING', 'MIL', 'KCF', 'TLD', 'MEDIANFLOW', 'GOTURN', 'MOSSE', 'CSRT']

def createTrackerByName(trackerType):
	#create a tracker based on tracker name
	if trackerType == trackerTypes[0]:
		tracker = cv.TrackerBoosting+create()
	elif trackerType == trackerTypes[1]:
		tracker = cv.TrackerMIL_create()
	elif trackerType == trackerTypes[2]:
		tracker = cv.TrackerKCF_create()
	elif trackerType == trackerTypes[3]:
		tracker = cv.TrackerTLD_create()
	elif trackerType == trackerTypes[4]:
		tracker = cv.TrackerMedianFlow_create()
	elif trackerType == trackerTypes[5]:
		tracker = cv.TrackerGOTURN_create()
	elif trackerType == trackerTypes[6]:
		tracker = cv.TrackerMOSSE_create()
	elif trackerType == trackerTypes[7]:
		tracker = cv.TrackerCSRT_create()
	else:
		tracker = None
		print('Incorrect tracker name')
	return tracker
	
with Lepton() as camera:
	camera.setup_video()	
	
	bboxes = []
	colors = []
	FirstRunTest = True
	while True:
		img = camera.grab().astype(np.float32)
		T, threshold = cv.threshold(img, 30000, 50000, cv.THRESH_BINARY)
		img2 = 255*(img - img.min())/(img.max()-img.min())
		imgu = img2.astype(np.uint8)
		
		frame = imgu
		bbox = cv.selectROI('MultiTracker', frame)
		bboxes.append(bbox)
		colors.append((randint(0,255), randint(0,255), randint(0,255)))
		print('Press q to quit selecting boxes and start tracking')
		print('Press any other key to select next object')
		k = cv.waitKey(0) & 0xFF
		if (k==113):
			break
		print('Slected bounding boxes{}'.format(bboxes))
	
		trackerType = 'CSRT'
		multiTracker = cv.MultiTracker_create()
	
		for bbox in bboxes:
			multiTracker.add(createTrackerByName(trackerType), frame, bbox)
	
		success, boxes = multiTracker.update(frame)
	
		for i, newbox in enumerate(boxes):
			p1 = (int(newbox[0]), int(newbox[1]))
			p2 = (int(newbox[0] + newbox[2]), int(newbox[1] + newbox[3]))
			cv.rectangle(frame, p1, p2, colors[i], 2, 1)
	
		cv.imshow('Multitracker', frame)
		if cv.waitKey(1) == 27:
				break
	camera.release()	
	cv.destroyAllWindows()
