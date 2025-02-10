import cv2
import numpy as np

class Tracker():
    """
    This class represents a tracker object that uses OpenCV and Kalman Filters.
    """

    def __init__(self, id, hsv_frame, track_window):
        """
        Initializes the Tracker object.

        Args:
            id (int): Identifier for the tracker.
            hsv_frame (numpy.ndarray): HSV frame.
            track_window (tuple): Tuple containing the initial position of the tracked object (x, y, width, height).
        """

        self.id = id

        self.track_window = track_window
        self.term_crit = (cv2.TERM_CRITERIA_COUNT | cv2.TERM_CRITERIA_EPS, 10, 1)

        # Initialize the histogram.
        x, y, w, h = track_window
        roi = hsv_frame[y:y+h, x:x+w]
        roi_hist = cv2.calcHist([roi], [0], None, [15],[0, 256])
        self.roi_hist = cv2.normalize(roi_hist, roi_hist, 0, 255, cv2.NORM_MINMAX)

        # Create a Kalman filter object with 4 state variables and 2 measurement variables.
        self.kalman = cv2.KalmanFilter(4, 2)
        
        # Set the measurement matrix of the Kalman filter.
        # It defines how the state variables are mapped to the measurement variables.
        # In this case, the measurement matrix is a 2x4 matrix that maps the x and y position measurements to the state variables.
        self.kalman.measurementMatrix = np.array(
            [[1, 0, 0, 0],
             [0, 1, 0, 0]], np.float32)

        # Set the transition matrix of the Kalman filter.
        # It defines how the state variables evolve over time.
        # In this case, the transition matrix is a 4x4 matrix that represents a simple linear motion model.
        self.kalman.transitionMatrix = np.array(
            [[1, 0, 1, 0],
             [0, 1, 0, 1],
             [0, 0, 1, 0],
             [0, 0, 0, 1]], np.float32)
             
#pedict function?
        # Set the process noise covariance matrix of the Kalman filter.
        # It represents the uncertainty in the process model and affects how the Kalman filter predicts the next state.
        # In this case, the process noise covariance matrix is a diagonal matrix scaled by 0.03.
        self.kalman.processNoiseCov = np.array(
            [[1, 0, 0, 0],
             [0, 1, 0, 0],
             [0, 0, 1, 0],
             [0, 0, 0, 1]], np.float32) * 0.03

        cx = x+w/2
        cy = y+h/2

        # Set the initial predicted state of the Kalman filter.
        # It is a 4x1 column vector that represents the initial estimate of the tracked object's state.
        # The first two elements are the predicted x and y positions, initialized to the center of the tracked window.
        self.kalman.statePre = np.array([[cx], [cy], [0], [0]], np.float32)
        
        # Set the corrected state of the Kalman filter.
        # It is a 4x1 column vector that represents the current estimated state of the tracked object.
        # Initially, it is set to the same value as the predicted state.
        self.kalman.statePost = np.array([[cx], [cy], [0], [0]], np.float32)
