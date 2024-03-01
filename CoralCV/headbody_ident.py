from PIL import Image

from pycoral.adapters import common
from pycoral.adapters import detect
from pycoral.utils.dataset import read_label_file
from tflite_runtime.interpreter import load_delegate
from tflite_runtime.interpreter import Interpreter

import cv2
from picamera2 import Picamera2

def main():
    # Set Model Parameters for TFLite
    labels = read_label_file("retrain-1000-headbody-labels.txt")
    interpreter = Interpreter("retrain-1000-headbody_edgetpu.tflite",
                              experimental_delegates=[load_delegate('libedgetpu.so.1.0')])

    # Allocate tensors and get input details for image scaling
    interpreter.allocate_tensors()
    input_details = interpreter.get_input_details()
    height = input_details[0]['shape'][1]
    width = input_details[0]['shape'][2]

    # Set display frame dimensions
    d_height = 180
    d_width = 640

    # Start Picam
    picam2 = Picamera2()
    picam2.configure(picam2.create_preview_configuration(main={"format": 'XRGB8888', "size": (2304, 1296)}))
    picam2.start()

    while True:
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

        # Loop over all detections and draw detection box if confidence is above minimum threshold and is person
        print("found " + str(len(objs)) + " items")
        for obj in objs:
            bbox = obj.bbox
            print("found " + str(labels.get(obj.id, obj.id)) + " at: " + str(bbox.xmin) + ":" + str(
                bbox.ymin) + ":" + str(bbox.xmax) + ":" + str(bbox.ymax))
            # Make head red
            if labels.get(obj.id, obj.id) == "Head":
                cv2.rectangle(disp_img, (int(bbox.xmin * d_width/width), int(bbox.ymin * d_height/height)), (int(bbox.xmax * d_width/width), int(bbox.ymax * d_height/height)), (0, 0, 255), 2)
            # Make body blue
            else:
                cv2.rectangle(disp_img, (int(bbox.xmin * d_width/width), int(bbox.ymin * d_height/height)), (int(bbox.xmax * d_width/width), int(bbox.ymax * d_height/height)), (0, 255, 0), 2)

        # All the results have been drawn on the frame, so it's time to display it.
        cv2.imshow('Object detector', disp_img)
        cv2.waitKey(100)


if __name__ == '__main__':
    main()
