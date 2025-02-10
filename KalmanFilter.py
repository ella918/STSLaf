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
      if event == cv.EVENT_LBUTTONDOWN:
        roi_points.append((x,y))
        cv2.cirvle(image, (x,y), 5, (0,255,0), -1)
        cv2.imshow("Select ROI", image)
      cv2.imshow("Select ROI", image)
      cv2.setMouseCallback("Select ROI", mouse_callback)
      cv2.waitKey(0)
      cv2.destroyAllWindows()
      image = cv2.cvtColor(image, cv.COLOR_RGB2GRAY)
      if len(roi_points) > 2:
        roi_points = np.array(roi_points)
        mask = np.zeros_like(image)
        cv2.fillPoly(mask, [roi_points], (255, 255, 255))
        return mask
      else:
        mask = np.ones_like(image)
        return mask
	
  # Create the KNN background subtractor.
  bg_subtractor = cv2.createBackgroundSubtractorKNN()

  # Set the history length for the background subtractor.
  history_length = 20
  bg_subtractor.setHistory(history_length)

  # Create kernel for erode and dilate operations.
  erode_kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
  dilate_kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 7))

  # Create an empty list to store the tracked blobs.
  blobs = []

  # Counter to keep track of the number of history frames populated.
  num_history_frames_populated = 0
	
  FirstRunTest = True

  # Start processing each frame of the video.
  while True:
    # Read the current frame from the video.
    img = camera.grab().astype(np.float32)
    T, threshold = cv2.threshold(img, 3000, 5000, cv2.THRESH_BINARY)
    img2 = 255*(img - img.min())/(img.max()-img.min())
    imgu = img2.astype(np.uint8)
    frame = imgu
##    if FirstRunTest is True and imgu is not None:
 #     masku = select_roi(imgu)
 #     mask = masku.astype(np.float32)
 #     FirstRunTest = False
 #   if FirstRunTest is False:
 #     masked = cv2.bitwise_and(threshold, mask)
  #  frame = masked.astype(np.uint8)

    # Apply the KNN background subtractor to get the foreground mask.
   # fg_mask = bg_subtractor.apply(frame)

    # Let the background subtractor build up a history before further processing.
    if num_history_frames_populated < history_length:
        num_history_frames_populated += 1
        continue

    # Create the thresholded image using the foreground mask.
    #_, thresh = cv2.threshold(fg_mask, 127, 255, cv2.THRESH_BINARY)

    # Perform erosion and dilation to improve the thresholded image.
   # cv2.erode(thresh, erode_kernel, thresh, iterations=2)
   # cv2.dilate(thresh, dilate_kernel, thresh, iterations=2)

    # Find contours in the thresholded image.
    contours, hier = cv2.findContours(frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Convert the frame to HSV color space for tracking.
    hsv_frame_color = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
    hsv_frame = cv2.cvtColor(hsv_frame_color, cv2.COLOR_BGR2HSV)

    # Draw red rectangles around large contours.
    # If there are no blobs being tracked yet, create new trackers.
    should_initialize_blobs = len(blobs) == 0
    id = 0
    for c in contours:
        # Check if the contour area is larger than a threshold.
        if cv2.contourArea(c) > 90:
            # Get the bounding rectangle coordinates.
            (x, y, w, h) = cv2.boundingRect(c)
            
            
            # Draw a rectangle around the contour.
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 1)
            
            # If no senators are being tracked yet, create a new tracker for each contour.
            if should_initialize_blobs:
                print(frame.shape)
                blobs.append(Tracker(id, hsv_frame, (x, y, w, h)))
        id += 1

    # Update the tracking of each senator.
    for blob in blobs:
        print(blob)
        blob.update(frame, hsv_frame)

    # Display the frame with senators being tracked.
    cv2.imshow('Blobs Tracked', frame)

    # Wait for the user to press a key (110ms delay).
    k = cv2.waitKey(110)

    # If the user presses the Escape key (key code 27), exit the loop.
    if k == 27:
        break
