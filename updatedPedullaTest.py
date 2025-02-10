import cv2 as cv
import numpy as np 
from flirpy.camera.lepton import Lepton

with Lepton() as camera:
	camera.setup_video()
	
	def select_roi(image):
		image = cv.cvtColor(image, cv.COLOR_GRAY2RGB)
		roi_points = []
		def mouse_callback(event, x, y, flags, param):
			if event == cv.EVENT_LBUTTONDOWN:
				roi_points.append((x, y))
				cv.circle(image, (x, y), 5, (0, 255, 0), -1)
				cv.imshow("Select ROI", image)
		cv.imshow("Select ROI", image)
		cv.setMouseCallback("Select ROI", mouse_callback)
		cv.waitKey(0)
		cv.destroyAllWindows()
		image = cv.cvtColor(image, cv.COLOR_RGB2GRAY)
		if len(roi_points) > 2:
			roi_points = np.array(roi_points)
			mask = np.zeros_like(image)
			cv.fillPoly(mask, [roi_points], (255, 255, 255))
			return mask
		else:
			mask = np.ones_like(image)
			return mask	
			
	def SimpleBlob(frame):
		contours, hierarchy = cv.findContours(frame, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
		cx_all = []
		cx_old = []
		cy_all = []
		cy_old = []
		blob_velo = []
		blobthresh = 90
		for contour in contours:
			mask = np.zeros_like(frame)
			contourSize = cv.contourArea(contour)
			if contourSize > blobthresh:
				cv.fillPoly(mask,[contour],1)
				M = cv.moments(mask)
				cX = int(M["m10"] / M["m00"])
				cx_all.append(cX)
				cY = int(M["m01"] / M["m00"])
				cy_all.append(cY)
				if len(cx_all)!=len(cx_old):
					cx_old = cx_all
					cy_old = cy_all
				else:
					blob_velo = sqrt((cx_all-cx_old)^2+(cy_all-cy_old)^2)
					threshold = 7
					result = blob_velo[blob_velo < threshold] 
					if len(result)>=1:
						B=0
						R=255
					else:
						R=0
						B=255
					cx_old = cx_all
					cy_old = cy_all
				
		
			    
		simpleblobcolor = cv.cvtColor(frame, cv.COLOR_GRAY2RGB)
		if len(cx_all) > 0:
			for i in range(len(cx_all)):
			    cv.circle(simpleblobcolor, (cx_all[i], cy_all[i]), 10, (B, 0, R), 2)
			simpleblob = simpleblobcolor
		else:
			simpleblob = frame
		return simpleblob
	
	FirstRunTest = True
	while True:
		
		img = camera.grab().astype(np.float32)
		T, threshold = cv.threshold(img, 30000, 50000, cv.THRESH_BINARY)
		img2 = 255*(img - img.min())/(img.max()-img.min())
		imgu = img2.astype(np.uint8)
		
		if FirstRunTest is True and imgu is not None:
			masku = select_roi(imgu)
			mask = masku.astype(np.float32)
			FirstRunTest = False
		if FirstRunTest is False:
			masked = cv.bitwise_and(threshold, mask)
		
		cv.imshow('mask', masked)
		masked2 = masked.astype(np.uint8)
		blobed = SimpleBlob(masked2)
		blobcopy = cv.resize(blobed, (1000,600))
		#blobcopy2 = cv.flip(blobcopy, 1)
		blobcopy2 = cv.flip(blobcopy, 0)
		cv.imshow('blob', blobcopy2)
		
		
		if cv.waitKey(1) == 27:
			break
	camera.release()	
	cv.destroyAllWindows()