# import the necessary packages
from imutils.video import VideoStream
from imutils.video import FPS
import numpy as np
import argparse
import imutils
import datetime
import time
import cv2
import pyglet

frame_width=1200
accuracy=(300, 300)
song = pyglet.media.load("honk.mp3")

class buzzer:
    def warning() :
        print("\a")
        time.sleep(1.0)
    def stop() :
        for i in (0,4):
            print("\a")
            time.sleep(0.25)

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-p", "--prototxt", required=True,
    help="path to Caffe 'deploy' prototxt file")
ap.add_argument("-m", "--model", required=True,
    help="path to Caffe pre-trained model")
ap.add_argument("-c", "--confidence", type=float, default=0.2,
    help="minimum probability to filter weak detections")
args = vars(ap.parse_args())

# initialize the list of class labels MobileNet SSD was trained to
# detect, then generate a set of bounding box colors for each class
CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
    "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
    "dog", "horse", "motorbike", "person", "pottedplant", "sheep",
    "sofa", "train", "tvmonitor"]
COLORS = np.random.uniform(0, 255, size=(len(CLASSES), 3))

# load our serialized model from disk
print("[INFO] loading model...")
net = cv2.dnn.readNetFromCaffe(args["prototxt"], args["model"])

# initialize the video stream, allow the camera sensor to warm up,
# and initialize the FPS counter
print("[INFO] starting video stream...")
#vs = VideoStream("http://192.168.0.65:8090/?action=stream").start()
#vs = VideoStream("http://10.42.0.196:8090/?action=stream").start()
vs = VideoStream(src=2).start()
# vs = VideoStream(usePiCamera=True).start()
time.sleep(2.0)
fps = FPS().start()

# loop over the frames from the video stream
while True:
    # grab the frame from the threaded video stream and resize it
    # to have a maximum width of 400 pixels
    frame = vs.read()
    frame = imutils.resize(frame, width=frame_width)
    rect = cv2.rectangle(frame, (int(frame_width*0.35),0),(int(frame_width*0.65),int(frame_width*3/4)),(0,0,255), 1)
    cv2.putText(frame, "hotheadfactory", (int(frame_width-240),int(frame_width*3/4)-10),
    cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 1)
    # grab the frame dimensions and convert it to a blob
    (h, w) = frame.shape[:2]
    blob = cv2.dnn.blobFromImage(cv2.resize(frame, accuracy),
        0.007843, accuracy, 127.5)

    # pass the blob through the network and obtain the detections and
    # predictions
    net.setInput(blob)
    detections = net.forward()
    
    # loop over the detections
    for i in np.arange(0, detections.shape[2]):
        # extract the confidence (i.e., probability) associated with
        # the prediction
        confidence = detections[0, 0, i, 2]

        # filter out weak detections by ensuring the `confidence` is
        # greater than the minimum confidence
        if confidence > args["confidence"]:
            # extract the index of the class label from the
            # `detections`, then compute the (x, y)-coordinates of
            # the bounding box for the object
            idx = int(detections[0, 0, i, 1])
            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
            (startX, startY, endX, endY) = box.astype("int")

            # draw the prediction on the frame
            label = "{}: {:.2f}%".format(CLASSES[idx],
                confidence * 100)
            now = datetime.datetime.now()
            timeToString = ('%s-%s-%s %s:%s:%s' % (now.year, now.month, now.day, now.hour, now.minute, now.second))
            cv2.putText(frame, timeToString, (0,int(frame_width*3/4)-10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 1)
            if(CLASSES[idx] == "person" and confidence > 0.7):
                #print("["+timeToString+"] "+CLASSES[idx]+" "+str(int(confidence*10000)/100)+"%")
                if frame_width*0.35 < startX < frame_width*0.65 :
                    if 20000 < (endX-startX)*(endY-startY) < 40000:
                        print(timeToString+": Pedestrian Warning")
                        cv2.putText(frame, "Pedestrian", (10,60),
                            cv2.FONT_HERSHEY_SIMPLEX, 2, (0,0,255), 2)
                    if (endX-startX)*(endY-startY) >= 40000:
                        print(timeToString+": \aEmergency Stop!")
                        cv2.putText(frame, "STOP!!", (10,60),
                            cv2.FONT_HERSHEY_SIMPLEX, 2, (0,0,255), 2)
            if(CLASSES[idx] in ("car", "bus") and confidence > 0.7):
                if frame_width*0.35 < startX < frame_width*0.65 :
                    if 40000 < (endX-startX)*(endY-startY) < 60000:
                        print(timeToString+": \aCar Warning")
                        cv2.putText(frame, "Car", (10,60),
                            cv2.FONT_HERSHEY_SIMPLEX, 2, (0,0,255), 2)
                    elif (endX-startX)*(endY-startY) >= 60000:
                        print(timeToString+": \aEmergency Stop!") 
                        cv2.putText(frame, "STOP!!", (10,60),
                            cv2.FONT_HERSHEY_SIMPLEX, 2, (0,0,255), 2)
            cv2.rectangle(frame, (startX, startY), (endX, endY),
                COLORS[idx], 2)
            y = startY - 15 if startY - 15 > 15 else startY + 15
            cv2.putText(frame, label, (startX, y),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLORS[idx], 2)

    # show the output frame
    cv2.imshow("Frame", frame)
    key = cv2.waitKey(1) & 0xFF

    # if the `q` key was pressed, break from the loop
    if key == ord("q"):
        break

    # update the FPS counter
    fps.update()

# stop the timer and display FPS information
fps.stop()
print("[INFO] elapsed time: {:.2f}".format(fps.elapsed()))
print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))

# do a bit of cleanup
cv2.destroyAllWindows()
vs.stop()
