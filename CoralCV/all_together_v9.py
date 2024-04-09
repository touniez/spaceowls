# run "python -m pip install mediapipe" first
# download model: wget -q https://storage.googleapis.com/mediapipe-models/gesture_recognizer/gesture_recognizer/float16/1/gesture_recognizer.task

# STEP 1: Import the necessary modules.
import serial
import time

from PIL import Image

# Gesture Imports
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# Vision Imports
from pycoral.adapters import common
from pycoral.adapters import detect
from pycoral.utils.dataset import read_label_file
from tflite_runtime.interpreter import load_delegate
from tflite_runtime.interpreter import Interpreter

import cv2
from picamera2 import Picamera2

# Initialize serial for arduino interface
ser = serial.Serial('/dev/ttyACM0', 115200, timeout=1)
ser.reset_input_buffer()

# Initialize Gesture Recognition objects
base_options = python.BaseOptions(model_asset_path='/home/pi/gesture_recognizer.task')
options = vision.GestureRecognizerOptions(base_options=base_options,
                                          running_mode=vision.RunningMode.IMAGE,
                                          num_hands=2,
                                          min_hand_detection_confidence=0.4,
                                          min_hand_presence_confidence=0.4,
                                          min_tracking_confidence=0.4)
recognizer = vision.GestureRecognizer.create_from_options(options)
gesture_frames = 0

# Initialize CV Recognition objects
labels = read_label_file("/home/pi/spaceowls/Models/retrain-2000-headbody-labels.txt")
interpreter = Interpreter("/home/pi/spaceowls/Models/retrain-2000-headbody_edgetpu.tflite",
                          experimental_delegates=[load_delegate('libedgetpu.so.1.0')])
interpreter.allocate_tensors()
input_details = interpreter.get_input_details()
height = input_details[0]['shape'][1]
width = input_details[0]['shape'][2]

# Set display frame dimensions
d_width = int(2304 / 4)
d_height = int(1296 / 4)

# Start Picam
picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(main={"format": 'XRGB8888', "size": (2304, 1296)}))
picam2.start()
prev_bodies = ""
prev_0_bodies = 0
prev_heads = ""
prev_0_heads = 0

while True:
    heads = ""
    bodies = ""
    # Capture image then resize for display and for input
    original_img = picam2.capture_array()
    disp_img = cv2.resize(original_img, (d_width, d_height))
    resized_img = cv2.resize(original_img, (width, height))

    # Change image format to Image object then resize for model
    pil_img = Image.fromarray(cv2.cvtColor(resized_img, cv2.COLOR_BGR2RGB))
    _, scale = common.set_resized_input(
        interpreter, pil_img.size, lambda size: pil_img.resize(size, Image.ANTIALIAS))

    # Invoke interpreter then get the detected objects
    interpreter.invoke()
    objs = detect.get_objects(interpreter, score_threshold=0.3, image_scale=scale)

    # Invoke gesture detector every 10 frames
    if gesture_frames == 10:
        resized_gesture = cv2.resize(original_img, (224, 224))
        rgb_gesture = cv2.cvtColor(resized_gesture, cv2.COLOR_BGR2RGB)
        gesture_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_gesture)
        recognition_result = recognizer.recognize(gesture_image)
        for i, gesture in enumerate(recognition_result.gestures):
            print("Top Gesture Result: ", gesture[0].category_name)
            if gesture[0].category_name == 'Open_Palm':
                ser.write(bytes("@\r\n", 'utf-8'))
                time.sleep(10)
            if gesture[0].category_name == "Closed_Fist":
                ser.write(bytes("$\r\n", 'utf-8'))
                time.sleep(10)
            if gesture[0].category_name == "Thumb_Up":
                ser.write(bytes("^\r\n", 'utf-8'))
                time.sleep(0.1)
            if gesture[0].category_name == "Thumb_Down":
                ser.write(bytes("*\r\n", 'utf-8'))
                time.sleep(0.1)
        gesture_frames = 0

    # Loop over all detections and draw detection box if confidence is above minimum threshold and is person
    body_count = 0
    head_count = 0
    # print("found " + str(len(objs)) + " items")
    for obj in objs:
        bbox = obj.bbox
        # Make head red
        if labels.get(obj.id, obj.id) == "Head":
            #cv2.rectangle(disp_img, (int(bbox.xmin * d_width / width), int(bbox.ymin * d_height / height)),
            #              (int(bbox.xmax * d_width / width), int(bbox.ymax * d_height / height)), (0, 0, 255), 2)
            heads += str(int(bbox.xmin * 32.0 / width) - 1) + "," + str(int(bbox.xmax * 32.0 / width) + 1) + "?" + str(
                int(bbox.ymin * 8.0 / height) - 1) + "!" + str(int(bbox.ymax * 8.0 / height) + 1) + ":"
            head_count += 1
            prev_0_heads = 0
        # Make body blue
        else:
            #cv2.rectangle(disp_img, (int(bbox.xmin * d_width / width), int(bbox.ymin * d_height / height)),
            #              (int(bbox.xmax * d_width / width), int(bbox.ymax * d_height / height)), (0, 255, 0), 2)
            bodies += str(int(bbox.xmin * 32.0 / width)) + "," + str(int(bbox.xmax * 32.0 / width)) + "?" + str(
                int(bbox.ymin * 8.0 / height)) + "!" + str(int(bbox.ymax * 8.0 / height)) + ":"
            body_count += 1
            prev_0_bodies = 0

    # If no body is detected for 10 straight frames, turn off the lights
    # Otherwise, use the previous bodies to reduce flickering
    if body_count == 0:
        if prev_0_bodies < 10:
            bodies = prev_bodies
            prev_0_bodies = min(10, prev_0_bodies + 1)
        else:
            bodies = ""
    if head_count == 0:
        if prev_0_heads < 10:
            heads = prev_heads
            prev_0_heads = min(10, prev_0_heads + 1)
        else:
            heads = ""

    print("Heads: " + heads)
    print("Bodies: " + bodies)
    heads += "\r\n"
    print("massage to pi: " + bodies + "/" + heads)
    ser.write(bytes(bodies + "/" + heads, 'utf-8'))
    prev_bodies = bodies
    prev_heads = heads

    # All the results have been drawn on the frame, so it's time to display it.
    # cv2.imshow('Object detector', disp_img)
    gesture_frames += 1
    cv2.waitKey(1)
