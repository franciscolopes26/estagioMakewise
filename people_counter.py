# USAGE
# To read and write back out to video:
# python people_counter.py --prototxt mobilenet_ssd/MobileNetSSD_deploy.prototxt \
#	--model mobilenet_ssd/MobileNetSSD_deploy.caffemodel --input videos/example_01.mp4 \
#	--output output/output_01.avi
#

# To read from webcam and write back out to disk:
# python people_counter.py --prototxt mobilenet_ssd/MobileNetSSD_deploy.prototxt \
#	--model mobilenet_ssd/MobileNetSSD_deploy.caffemodel \
#	--output output/webcam_output.avi

# import the necessary packages
from _ast import Load

from load_model import LoadModel
from pyimagesearch.centroidtracker import CentroidTracker
from pyimagesearch.trackableobject import TrackableObject
from pyimagesearch.trackerengine import TrackerEngine
from imutils.video import VideoStream
from imutils.video import FPS
import numpy as np
import argparse
import imutils
import time
import cv2
import requests


# caffe
# python3 people_counter.py -m /home/guilherme/projetos/estagioMakewise/models/caffe/MobileNetSSD_deploy.json -i /home/guilherme/projetos/estagioMakewise/videos/example_01.mp4 -o /home/guilherme/projetos/estagioMakewise/output/output_03.avi

# tenserflow
# python3 people_counter.py -m /home/guilherme/projetos/estagioMakewise/models/tensorflow/ssd_mobilenet_v2_coco_2018_03_29.json -i /home/guilherme/projetos/estagioMakewise/videos/example_01.mp4 -o /home/guilherme/projetos/estagioMakewise/output/output_03.avi

# tenserflow ssdlite
# python3 people_counter.py -m /home/guilherme/projetos/estagioMakewise/models/tensorflow/ssdlite_mobilenet_v2_coco_2018_05_09.json -i 'rtsp://10.1.203.252:554/user=admin&password=&channel=1&stream=0.sdp' -o /home/guilherme/projetos/estagioMakewise/output/output_03.avi


# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-m", "--model", required=True,
                help="path to model_config")
ap.add_argument("-i", "--input", type=str,
                help="path to optional input video file")
ap.add_argument("-o", "--output", type=str,
                help="path to optional output video file")
ap.add_argument("-c", "--confidence", type=float, default=0.3,
                help="minimum probability to filter weak detections")
ap.add_argument("-s", "--skip-frames", type=int, default=7,
                help="# of skip frames between detections")
ap.add_argument("-u", "--url", type=str, default='http://127.0.0.1:5000/form/sensor1',
                help="server location, localhost:5000 by default")
args = vars(ap.parse_args())

# load our serialized model from disk
print("[INFO] loading model...")
load_model = LoadModel(args["model"])
detection_model = load_model.create()

# if a video path was not supplied, grab a reference to the webcam
if not args.get("input", False):
    print("[INFO] starting video stream...")
    vs = VideoStream(src=0).start()
    time.sleep(2.0)

# otherwise, grab a reference to the video file
else:
    print("[INFO] opening video file...")
    vs = cv2.VideoCapture(args["input"])

# initialize the video writer (we'll instantiate later if need be)
writer = None

# initialize the frame dimensions (we'll set them as soon as we read
# the first frame from the video)
W = None
H = None



# instantiate our centroid tracker, then initialize a list to store
# each of our dlib correlation trackers, followed by a dictionary to
# map each unique object ID to a TrackableObject
trackerEngines = {}
for s in ["person","chair", "car"]:
    trackerEngines[s] = TrackerEngine(s,maxDisappeared=40, maxDistance=50)

# initialize the total number of frames processed thus far, along
# with the total number of objects that have moved either up or down
totalFrames = 0



# start the frames per second throughput estimator
fps = FPS().start()

#Size of the net
net_input_size = load_model.get_net_input_size()

# loop over frames from the video stream
while True:
    # grab the next frame and handle if we are reading from either
    # VideoCapture or VideoStream
    frame = vs.read()
    frame = frame[1] if args.get("input", False) else frame

    # if we are viewing a video and we did not grab a frame then we
    # have reached the end of the video
    if args["input"] is not None and frame is None:
        break

    # resize the frame to have a maximum width of 500 pixels (the
    # less data we have, the faster we can process it), then convert
    # the frame from BGR to RGB for dlib

    frame = imutils.resize(frame, width=net_input_size[0], height=net_input_size[1])
    # if the frame dimensions are empty, set them
    if W is None or H is None:
        (H, W) = frame.shape[:2]


    # linha #line
    point_a = (0, H // 2)
    point_b = (400, H // 2)

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)



    # if we are supposed to be writing a video to disk, initialize
    # the writer
    if args["output"] is not None and writer is None:
        fourcc = cv2.VideoWriter_fourcc(*"MJPG")
        writer = cv2.VideoWriter(args["output"], fourcc, 30,
                                 (W, H), True)

    # initialize the current status along with our list of bounding
    # box rectangles returned by either (1) our object detector
    # (2) the correlation trackers
    status = "Waiting"
    
    for (label, trackerEngine) in trackerEngines.items():
        trackerEngine.rects = []


    # check to see if we should run a more computationally expensive
    # object detection method to aid our tracker
    if totalFrames % args["skip_frames"] == 0:
        for (label, trackerEngine) in trackerEngines.items():
            trackerEngine.trackers = []
        # set the status and initialize our new set of object trackers
        status = "Detecting"
        trackers = []

        # convert the frame to a blob and pass the blob through the
        # network and obtain the detections
        class_ids, confidences, boxes = detection_model.detect(frame, args["confidence"], 0.1)

        # loop over the detections
        for idx, confidence, box in zip(class_ids, confidences, boxes):

            label = load_model.get_label(idx.astype("int")[0])
            # if the class label is not a configure trakerengine, ignore it
            if label not in  trackerEngines:
                continue

            trackerEngine = trackerEngines[label]

            # compute the (x, y)-coordinates of the bounding box
            (bx, by, bw, bh) = box.astype("int")

            # construct a dlib rectangle object from the bounding
            # box coordinates and then start the dlib correlation
            # tracker
            tracker = cv2.TrackerMedianFlow_create()
            # add the bounding box coordinates to the rectangles list

            tracker.init(rgb, (bx, by, bw, bh))
            trackerEngine.rects.append((bx, by,bx + bw, by + bh))
            # add the tracker to our list of trackers so we can
            # utilize it during skip frames
            trackerEngine.trackers.append(tracker)

    # otherwise, we should utilize our object *trackers* rather than
    # object *detectors* to obtain a higher frame processing throughput
    else:
        for (label, trackerEngine) in trackerEngines.items():
        
            # loop over the trackers
            for tracker in trackerEngine.trackers:
                # set the status of our system to be 'tracking' rather
                # than 'waiting' or 'detecting'
                status = "Tracking"

                # update the tracker and grab the updated position
                retval, boundingBox = tracker.update(rgb)

                if retval:
                    (x, y, w, h) = [int(v) for v in boundingBox]

                    # unpack the position object
                    startX = x
                    startY = y
                    endX = x + w
                    endY = y + h

                    # add the bounding box coordinates to the rectangles list
                    trackerEngine.rects.append((startX, startY, endX, endY))

    # draw a horizontal line in the center of the frame -- once an
    # object crosses this line we will determine whether they were
    # moving to the left or to the right of AB'
    cv2.line(frame, point_a, point_b, (0, 255, 255), 2)

    for (label, trackerEngine) in trackerEngines.items():

        trackerEngine.updateCentroids(point_a,point_b)
        
        message = trackerEngine.get_counting_message()
        if message:
            try: #PLANO
                response = requests.post(args["url"], data=message, timeout=(1, 10))
                response.raise_for_status() #raise error on http error
                trackerEngine.reset_counter() #reset the counter if ok
            except:
                print("Error sending counting")

        for (objectID, trackableObject) in trackerEngine.trackableObjects.items():
            # draw both the ID of the object and the centroid of the
            # object on the output frame
            text = "%d %s" % (objectID ,label)
            centroid = trackableObject.get_last_position()
            cv2.putText(frame, text, (centroid[0] - 10, centroid[1] - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            cv2.circle(frame, (centroid[0], centroid[1]), 4, (0, 255, 0), -1)

   
    # construct a tuple of information we will be displaying on the
    # frame
    info = [       
        ("Status", status)
    ]

    # loop over the info tuples and draw them on our frame
    for (i, (k, v)) in enumerate(info):
        text = "{}: {}".format(k, v)
        cv2.putText(frame, text, (10, H - ((i * 20) + 20)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

    # check to see if we should write the frame to disk
    if writer is not None:
        writer.write(frame)

    # show the output frame
    cv2.imshow("Frame", frame)
    key = cv2.waitKey(1) & 0xFF

    # if the `q` key was pressed, break from the loop
    if key == ord("q"):
        break

    # increment the total number of frames processed thus far and
    # then update the FPS counter
    totalFrames += 1
    fps.update()

# stop the timer and display FPS information
fps.stop()
print("[INFO] elapsed time: {:.2f}".format(fps.elapsed()))
print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))

# check to see if we need to release the video writer pointer
if writer is not None:
    writer.release()

# if we are not using a video file, stop the camera video stream
if not args.get("input", False):
    vs.stop()

# otherwise, release the video file pointer
else:
    vs.release()

# close any open windows
cv2.destroyAllWindows()
