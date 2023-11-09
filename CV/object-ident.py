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

x_dim = 2304
y_dim = 1296
model_x = 320
model_y = 90

picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(main={"format": 'XRGB8888', "size": (x_dim, y_dim)}))
picam2.set_controls({"FrameRate": 30})
picam2.start()
net = cv2.dnn_DetectionModel(weightsPath,configPath)
net.setInputSize(model_x,model_y)
net.setInputScale(1.0/ 127.5)
net.setInputMean((127.5, 127.5, 127.5))
net.setInputSwapRB(True)


#CV Function
def getObjects(img, thres, nms, objects=[]):
	classIds, confs, bbox = net.detect(img,confThreshold=thres,nmsThreshold=nms)
	#print(classIds,bbox)
	if len(objects) == 0: 
		objects = classNames
	objectInfo =[]
	if len(classIds) != 0:
		for classId, confidence,box in zip(classIds.flatten(),confs.flatten(),bbox):
			className = classNames[classId - 1]
			if className in objects:
				objectInfo.append([box,className])
				cv2.rectangle(img,box,color=(0,255,0),thickness=2)
	return objectInfo


if __name__ == '__main__':
	ser = serial.Serial('/dev/ttyACM0', 115200, timeout=1)
	ser.reset_input_buffer()
	#ser.close()
	#ser.open()

mode = 'standby'
cv2.startWindowThread()
cv2.namedWindow("Output")

while True:
	#Standby mode
	#if mode == 'standby':
	#	ser.write(b"standby\n")
	#	print("fuck")
	#	status = ser.readline().decode('utf-8').rstrip()
	#	if status == 'go active':
	#		mode = 'active'
	#		print("I just went active")
        	#time.sleep(1)

	#if mode == 'active':
		#Image acquisition
		img = picam2.capture_array()
		img = cv2.resize(img, (model_x, model_y))
		rgbImage = cv2.cvtColor(img, cv2.COLOR_RGBA2RGB)
		objectInfo = getObjects(rgbImage,0.45,0.8,objects = ['person'])
		# cv2.imshow("Output",rgbImage)

		for item in objectInfo:
			poop = item[0][0]
			x1 = item[0][0] // 10
			x2 = (poop + item[0][2]) // 10
			location = str(x1)+","+str(x2)+"\r\n"
			print(location)
			ser.write(bytes(location,'utf-8'))
			time.sleep(0.25)
			received = False  
			#while received == False:
			#	status = ser.readline().decode('utf-8').rstrip()
			#	print(status)
			#	if status == "R":
			#		received = True
		if objectInfo == []:
	#		mode = 'standby'
			print("Going standby")
		cv2.waitKey(1)

