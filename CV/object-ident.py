import cv2
from picamera2 import Picamera2
#thres = 0.45 # Threshold to detect object

classNames = []
classFile = "/home/pi/Desktop/Object_Detection_Files/coco.names"
with open(classFile,"rt") as f:
    classNames = f.read().rstrip("\n").split("\n")

configPath = "/home/pi/Desktop/Object_Detection_Files/ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt"
weightsPath = "/home/pi/Desktop/Object_Detection_Files/frozen_inference_graph.pb"

net = cv2.dnn_DetectionModel(weightsPath,configPath)
net.setInputSize(300,150)
net.setInputScale(1.0/ 127.5)
net.setInputMean((127.5, 127.5, 127.5))
net.setInputSwapRB(True)


def getObjects(img, thres, nms, draw=True, objects=[]):
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
                    # cv2.putText(img,classNames[classId-1].upper(),(box[0]+10,box[1]+30),
                    # cv2.FONT_HERSHEY_COMPLEX,1,(0,255,0),2)
                    # cv2.putText(img,str(round(confidence*100,2)),(box[0]+200,box[1]+30),
                    # cv2.FONT_HERSHEY_COMPLEX,1,(0,255,0),2)

    return img,objectInfo


#if __name__ == "__main__":

#cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
#cap.set(3,640)
#cap.set(4,480)
#cap.set(10,70)
#if not cap.isOpened():
#    print('error opening stream')
#    exit(0)
picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(main={"format": 'XRGB8888', "size": (300, 150)}))
picam2.start()

while True:
    #success, img = cap.read()
    img = picam2.capture_array()
    rgbImage = cv2.cvtColor(img, cv2.COLOR_RGBA2RGB)
    if True:
            result, objectInfo = getObjects(rgbImage,0.45,0.2,objects = ['person'])
    #print(objectInfo)
            cv2.imshow("Output",rgbImage)
    else:
            print('no frame')
            break
    cv2.waitKey(1)
