import cv2
from picamera2 import Picamera2
#thres = 0.45 # Threshold to detect object

classNames = []
classFile = "/home/pi/Desktop/Object_Detection_Files/coco.names"
with open(classFile,"rt") as f:
    classNames = f.read().rstrip("\n").split("\n")

configPath = "/home/pi/Desktop/Object_Detection_Files/ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt"
weightsPath = "/home/pi/Desktop/Object_Detection_Files/frozen_inference_graph.pb"

# x_dim = 1024
# y_dim = 200
x_dim = 2304
y_dim = 1296
net = cv2.dnn_DetectionModel(weightsPath,configPath)
net.setInputSize(320,90)
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
                item = objectInfo[0]
                box = item[0]
                x2 = box[0] // 32
                y2 = (box[0] + box[2]) // 32
                #    print("x2 = " + str(x2))
                print("y2 = " + str(y2))
    return img,objectInfo


picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(main={"format": 'XRGB8888', "size": (x_dim, y_dim)}))
picam2.set_controls({"FrameRate": 30})
picam2.start()

while True:
    #success, img = cap.read()
    img = picam2.capture_array()
    img = cv2.resize(img, (320,90))
    rgbImage = cv2.cvtColor(img, cv2.COLOR_RGBA2RGB)
    if True:
            result, objectInfo = getObjects(rgbImage,0.6,0.8,objects = ['person'])
    #print(objectInfo)
            diagram = [2 for i in range(32)]
            for item in objectInfo:
                poop = item[0][0]
                x1 = item[0][0] // 10
                x2 = (poop + item[0][2]) // 10
                for x in range(x1,x2):
                    diagram[x] = -1
            for i in range(32):
                cv2.rectangle(rgbImage, (i* 10, 80), ((i+1) * 10 - 1 , 90), color=(255,0,0), thickness=diagram[i])
            cv2.imshow("Output",rgbImage)
    else:
            print('no frame')
            break
    cv2.waitKey(1)
