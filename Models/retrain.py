import numpy as np
import os

from tflite_model_maker.config import ExportFormat
from tflite_model_maker import model_spec
from tflite_model_maker import object_detector

import tensorflow as tf
assert tf.__version__.startswith('2')

tf.get_logger().setLevel('ERROR')
from absl import logging
logging.set_verbosity(logging.ERROR)

train_data, validation_data, test_data = object_detector.DataLoader.from_csv('/Users/anthonyzheng/Desktop/datasets/jsonparse/labels200.csv')
print("training data size: " + str(len(train_data)))
print("validation data size: " + str(len(validation_data)))
print("test data size: " + str(len(test_data)))

spec = object_detector.EfficientDetLite0Spec()

model = object_detector.create(train_data=train_data,
                               model_spec=spec,
                               validation_data=validation_data,
                               epochs=10,
                               batch_size=10,
                               train_whole_model=True)

print("###### DONE TRAINING ######")
print("###### EVALUATING ######")
model.evaluate(test_data)

print("###### EXPORTING ######")
TFLITE_FILENAME = 'retrain.tflite'
LABELS_FILENAME = 'retrain-labels.txt'
model.export(export_dir='.', tflite_filename=TFLITE_FILENAME, label_filename=LABELS_FILENAME,
             export_format=[ExportFormat.TFLITE, ExportFormat.LABEL])
