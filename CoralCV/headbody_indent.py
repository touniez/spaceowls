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
  # Set Model Parameters for TFLite
  labels = read_label_file("retrain-1000-headbody-labels.txt")
  interpreter = Interpreter("retrain-1000-headbody_edgetpu.tflite", experimental_delegates=[load_delegate('libedgetpu.so.1.0')])

  interpreter.allocate_tensors()
  input_details = interpreter.get_input_details()
  height = input_details[0]['shape'][1]
  width = input_details[0]['shape'][2]

  # Start Picam
  picam2 = Picamera2()
  x_dim = 2304
  y_dim = 1296
  picam2.configure(picam2.create_preview_configuration(main={"format": 'XRGB8888', "size": (x_dim, y_dim)}))
  picam2.start()

  while True:
    original_img = picam2.capture_array()
    resized_img = cv2.resize(original_img, (width, height))
    
    pil_img = Image.fromarray(cv2.cvtColor(resized_img, cv2.COLOR_BGR2RGB))
    _, scale = common.set_resized_input(
        interpreter, pil_img.size, lambda size: pil_img.resize(size, Image.ANTIALIAS))
    
    interpreter.invoke()
    objs = detect.get_objects(interpreter, score_threshold=0.4, image_scale=scale)

    # Loop over all detections and draw detection box if confidence is above minimum threshold and is person
    print("found " + str(len(objs)) + " items")
    for obj in objs:
      if obj.score > 0.4:
        bbox = obj.bbox
        print("found " + str(labels.get(obj.id, obj.id)) + " at: " + str(bbox.xmin) + ":" + str(bbox.ymin) + ":" + str(bbox.xmax) + ":" + str(bbox.ymax))
        if labels.get(obj.id, obj.id) == "Head":
          cv2.rectangle(resized_img, (bbox.xmin, bbox.ymin), (bbox.xmax, bbox.ymax), (0, 255, 0), 2)
        else:
          cv2.rectangle(resized_img, (bbox.xmin, bbox.ymin), (bbox.xmax, bbox.ymax), (0, 0, 255), 2)

    # All the results have been drawn on the frame, so it's time to display it.
    cv2.imshow('Object detector', resized_img)
    print("frame")
    cv2.waitKey(1)

if __name__ == '__main__':
  main()
