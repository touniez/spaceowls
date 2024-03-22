# run "python -m pip install mediapipe" first
# download model: wget -q https://storage.googleapis.com/mediapipe-models/gesture_recognizer/gesture_recognizer/float16/1/gesture_recognizer.task

# STEP 1: Import the necessary modules.
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

import cv2
import numpy as np
from picamera2 import Picamera2

# STEP 2: Create an GestureRecognizer object.
base_options = python.BaseOptions(model_asset_path='/home/pi/Downloads/gesture_recognizer.task')
options = vision.GestureRecognizerOptions(base_options=base_options,
                                          running_mode=vision.RunningMode.IMAGE,
                                          num_hands=2,
                                          min_hand_detection_confidence=0.4,
                                          min_hand_presence_confidence=0.4,
                                          min_tracking_confidence=0.4)
# options = vision.GestureRecognizerOptions(base_options=base_options)
recognizer = vision.GestureRecognizer.create_from_options(options)

picam2 = Picamera2()
x_dim = 2304
y_dim = 1296

DESIRED_HEIGHT = 224
DESIRED_WIDTH = 224

picam2.configure(picam2.create_preview_configuration(main={"format": 'XRGB8888', "size": (x_dim, y_dim)}))
# picam2.configure(picam2.create_preview_configuration(main={"format": 'XRGB8888', "size": (DESIRED_WIDTH, DESIRED_HEIGHT)}))

picam2.start()
disp_width = int(2304 / 4)
disp_height = int(1296 / 4)


while True:
    # STEP 3: Load the input image.
    original_img = picam2.capture_array()
    img_display = cv2.resize(original_img, (disp_width, disp_height))
    resized_img = cv2.resize(original_img, (DESIRED_WIDTH, DESIRED_HEIGHT))
    rgb_image = cv2.cvtColor(resized_img, cv2.COLOR_BGR2RGB)
    image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_image)

    # STEP 4: Recognize gestures in the input image.
    recognition_result = recognizer.recognize(image)

    # STEP 5: Process the result. In this case, visualize it.
    for i, gesture in enumerate(recognition_result.gestures):
        # Get the top gesture from the recognition result
        print("Top Gesture Result: ", gesture[0].category_name)

    cv2.imshow('Gesture detector', img_display)
    cv2.waitKey(1)
