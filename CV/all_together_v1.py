import serial
import time
import cv2
from picamera2 import Picamera2
#thres = 0.45 # Threshold to detect object

classNames = []
classFile = "/home/pi/Object_Detection_Files/coco.names"
with open(classFile,"rt") as f:
    classNames = f.read().rstrip("\n").split("\n")

configPath = "/home/pi/Object_Detection_Files/ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt"
weightsPath = "/home/pi/Object_Detection_Files/frozen_inference_graph.pb"

net = cv2.dnn_DetectionModel(weightsPath,configPath)
net.setInputSize(640,480)
net.setInputScale(1.0/ 127.5)
net.setInputMean((127.5, 127.5, 127.5))
net.setInputSwapRB(True)


if __name__ == '__main__':
    ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
    ser.reset_input_buffer()

mode = 'standby'
    while True:
	#Standby mode
	if mode == 'standby':
        	ser.write(b"Standby Mode\n")
        	status = ser.readline().decode('utf-8').rstrip()
        	if status = 'go active'
			mode = 'active' 
        	#time.sleep(1)

	if mode == 'active':
		ser.write(b"Active Mode\n")
		#Image acquisition
		img = picam2.capture_array()
    		rgbImage = cv2.cvtColor(img, cv2.COLOR_RGBA2RGB)
           	objectInfo = getObjects(rgbImage,0.45,0.2,objects = ['person'])

		for item in objectInfo:
			location = item[0]
			print(location)
			ser.write(location)
    		cv2.waitKey(1)

#CV Function
def getObjects(img, thres, nms, draw=False, objects=[]):
    classIds, confs, bbox = net.detect(img,confThreshold=thres,nmsThreshold=nms)
    #print(classIds,bbox)
    if len(objects) == 0: objects = classNames
    objectInfo =[]
    if len(classIds) != 0:
        for classId, confidence,box in zip(classIds.flatten(),confs.flatten(),bbox):
            className = classNames[classId - 1]
            if className in objects:
                objectInfo.append([box,className])
                if (draw):
                    cv2.rectangle(img,box,color=(0,255,0),thickness=2)
                    cv2.putText(img,classNames[classId-1].upper(),(box[0]+10,box[1]+30),
                    cv2.FONT_HERSHEY_COMPLEX,1,(0,255,0),2)
                    cv2.putText(img,str(round(confidence*100,2)),(box[0]+200,box[1]+30),
                    cv2.FONT_HERSHEY_COMPLEX,1,(0,255,0),2)

    return objectInfo
