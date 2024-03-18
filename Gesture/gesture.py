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
base_options = python.BaseOptions(model_asset_path='gesture_recognizer.task')
options = vision.GestureRecognizerOptions(base_options=base_options)
recognizer = vision.GestureRecognizer.create_from_options(options)

picam2 = Picamera2()
x_dim = 2304
y_dim = 1296
picam2.configure(picam2.create_preview_configuration(main={"format": 'XRGB8888', "size": (x_dim, y_dim)}))

picam2.start()
disp_width = int(2304 / 4)
disp_height = int(1296 / 4)

while True:
    # STEP 3: Load the input image.
    original_img = picam2.capture_array()
    img_display = cv2.resize(original_img, (disp_width, disp_height))
    image = mp.Image(image_format=mp.ImageFormat.SRGB, data=original_img)

    # STEP 4: Recognize gestures in the input image.
    recognition_result = recognizer.recognize(image)

    # STEP 5: Process the result. In this case, visualize it.
    top_gesture = recognition_result.gestures[0][0]
    print(top_gesture)

    cv2.imshow('Gesture detector', img_display)
    cv2.waitKey(1)
