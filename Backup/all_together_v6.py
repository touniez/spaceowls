# Lint as: python3
# Copyright 2019 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
r"""Example using PyCoral to detect objects in a given image.

To run this code, you must attach an Edge TPU attached to the host and
install the Edge TPU runtime (`libedgetpu.so`) and `tflite_runtime`. For
device setup instructions, see coral.ai/docs/setup.

Example usage:
```
bash examples/install_requirements.sh detect_image.py

python3 examples/detect_image.py \
  --model test_data/ssd_mobilenet_v2_coco_quant_postprocess_edgetpu.tflite \
  --labels test_data/coco_labels.txt \
  --input test_data/grace_hopper.bmp \
  --output ${HOME}/grace_hopper_processed.bmp
```
"""

import argparse
import time
import serial

from PIL import Image
from PIL import ImageDraw

from pycoral.adapters import common
from pycoral.adapters import detect
from pycoral.utils.dataset import read_label_file
from pycoral.utils.edgetpu import make_interpreter
from tflite_runtime.interpreter import load_delegate
from tflite_runtime.interpreter import Interpreter

import cv2
import numpy as np
from picamera2 import Picamera2

def main():
  # Start serial for arduino
  ser = serial.Serial('/dev/ttyACM0', 115200, timeout=1)
  ser.reset_input_buffer()
  
  # Set Model Parameters for TFLite
  labels = read_label_file("coco_labels.txt")
  interpreter = Interpreter("tf2_ssd_mobilenet_v2_coco17_ptq_edgetpu.tflite", experimental_delegates=[load_delegate('libedgetpu.so.1.0')])
  # interpreter = make_interpreter(model_path="tf2_ssd_mobilenet_v2_coco17_ptq_edgetpu.tflite")

  interpreter.allocate_tensors()
  input_details = interpreter.get_input_details()
  output_details = interpreter.get_output_details()
  height = input_details[0]['shape'][1]
  width = input_details[0]['shape'][2]
  floating_model = (input_details[0]['dtype'] == np.float32)
  input_mean = 127.5
  input_std = 127.5

  # Start Picam
  picam2 = Picamera2()
  x_dim = 2304
  y_dim = 1296
  picam2.configure(picam2.create_preview_configuration(main={"format": 'XRGB8888', "size": (x_dim, y_dim)}))
  # picam2.set_controls({"FrameRate": 30})
  picam2.start()
  disp_width = int(2304/4)
  disp_height = int(1296/4)
  

  while True:
    location = ""
    original_img = picam2.capture_array()
    #img = cv2.resize(img, (320, 90))
    img_data = cv2.resize(original_img, (width, height))
    img_display = cv2.resize(original_img, (disp_width, disp_height))
    img = cv2.cvtColor(img_data, cv2.COLOR_RGBA2RGB)
    img = np.expand_dims(img, axis=0)
    if floating_model:
      img = (np.float32(img) - input_mean) / input_std
    interpreter.set_tensor(input_details[0]['index'], img)
    interpreter.invoke()
    boxes_idx, classes_idx, scores_idx = 1, 3, 0 # for tf2 model
    boxes = interpreter.get_tensor(output_details[boxes_idx]['index'])[0]  # Bounding box coordinates of detected objects
    scores = interpreter.get_tensor(output_details[scores_idx]['index'])[0]  # Confidence of detected objects
    classes = interpreter.get_tensor(output_details[classes_idx]['index'])[0] # Class index of detected objects

    # Loop over all detections and draw detection box if confidence is above minimum threshold and is person
    for i in range(len(scores)):
      if ((scores[i] > 0.6) and (scores[i] <= 1.0)):
        # only show boxes for people
        if labels[int(classes[i])] == "person":
          ymin = int(max(0, (boxes[i][0] * disp_height)))
          xmin = int(max(0, (boxes[i][1] * disp_width)))
          ymax = int(min(disp_height, (boxes[i][2] * disp_height)))
          xmax = int(min(disp_width, (boxes[i][3] * disp_width)))
          print("found person at: (" + str(xmin) + ", " + str(ymin) + ") to (" + str(xmax) + ", " + str(ymax) + ")")
          # cv2.rectangle(img_display, (xmin, ymin), (xmax, ymax), (0, 255, 0), 2)
          location += str(int(xmin * 32.0/disp_width))+","+str(int(xmax * 32.0/disp_width))+"?"+str(int(ymin * 8.0/disp_height))+"!"+str(int(ymax * 8.0/disp_height))+":"
    location += "\r\n"
    print("massage to pi: " + location)
    ser.write(bytes(location,'utf-8'))

	
    # All the results have been drawn on the frame, so it's time to display it.
    # cv2.imshow('Object detector', img_display)
    cv2.waitKey(10)

if __name__ == '__main__':
  main()
