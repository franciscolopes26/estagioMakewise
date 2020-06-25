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
ct = CentroidTracker(maxDisappeared=40, maxDistance=50)
trackers = []
trackableObjects = {}

# initialize the total number of frames processed thus far, along
# with the total number of objects that have moved either up or down
totalFrames = 0
total_right_AB = 0
total_left_AB = 0
last_communication_exit = 0
last_communication_enter = 0
totalA = 0
totalB = 0
# total_right_AB = 0
# total_left_AB = 0


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
    point_a = (W // 2, 0)
    point_b = (W // 2, H)

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
    rects = []

    # check to see if we should run a more computationally expensive
    # object detection method to aid our tracker
    if totalFrames % args["skip_frames"] == 0:
        # set the status and initialize our new set of object trackers
        status = "Detecting"
        trackers = []

        # convert the frame to a blob and pass the blob through the
        # network and obtain the detections
        class_ids, confidences, boxes = detection_model.detect(frame, args["confidence"])

        # loop over the detections
        for idx, confidence, box in zip(class_ids, confidences, boxes):

            # if the class label is not a person, ignore it
            if load_model.labels[idx.astype("int")[0]] != "person":
                continue

            # compute the (x, y)-coordinates of the bounding box
            (bx, by, bw, bh) = box.astype("int")

            # construct a dlib rectangle object from the bounding
            # box coordinates and then start the dlib correlation
            # tracker
            tracker = cv2.TrackerMedianFlow_create()
            # add the bounding box coordinates to the rectangles list

            tracker.init(rgb, (bx, by, bw, bh))
            rects.append((bx, by,bx + bw, by + bh))
            # add the tracker to our list of trackers so we can
            # utilize it during skip frames
            trackers.append(tracker)

    # otherwise, we should utilize our object *trackers* rather than
    # object *detectors* to obtain a higher frame processing throughput
    else:
        # loop over the trackers
        for tracker in trackers:
            # set the status of our system to be 'tracking' rather
            # than 'waiting' or 'detecting'
            status = "Tracking"

            # update the tracker and grab the updated position
            retval, boundingBox = tracker.update(rgb)

            (x, y, w, h) = [int(v) for v in boundingBox]

            # unpack the position object

            # +++ novo
            startX = x
            startY = y
            endX = x + w
            endY = y + h
            # +++

            # --- antigo
            # startX = int(pos.left())
            # startY = int(pos.top())
            # endX = int(pos.right())
            # endY = int(pos.bottom())
            # ---

            # add the bounding box coordinates to the rectangles list
            rects.append((startX, startY, endX, endY))

    # draw a horizontal line in the center of the frame -- once an
    # object crosses this line we will determine whether they were
    # moving to the left or to the right of AB'
    cv2.line(frame, point_a, point_b, (0, 255, 255), 2)

    # use the centroid tracker to associate the (1) old object
    # centroids with (2) the newly computed object centroids
    objects = ct.update(rects)

    # loop over the tracked objects
    for (objectID, centroid) in objects.items():
        # check to see if a trackable object exists for the current
        # object ID
        to = trackableObjects.get(objectID, None)

        # if there is no existing trackable object, create one
        if to is None:
            to = TrackableObject(objectID, centroid)

        # otherwise, there is a trackable object so we can utilize it
        # to determine direction
        else:
            # the difference between the y-coordinate of the *current*
            # centroid and the mean of *previous* centroids will tell
            # us in which direction the object is moving (negative for
            # 'up' and positive for 'down')
            to.update_position(centroid)

            # test if it cross the line
            if to.is_crossing_line(point_a, point_b):
                # test if te final position is on left or the right of the line

                if to.last_side == 'L':
                    total_left_AB += 1
                    #myobj = {'enter': 1, "exit": 0}
                elif to.last_side == 'R':
                    total_right_AB += 1
                    #myobj = {'enter': 0, "exit": 1}

                url = args["url"]
                try:
                    myobj = {'enter': totalA, "exit": totalB}
                    requests.post("http://127.0.0.1/", data=myobj, timeout=(1, 1))
                    last_communication_enter = total_left_AB
                    last_communication_exit = total_right_AB
                except:
                    totalA = total_left_AB - last_communication_enter
                    totalB = total_right_AB - last_communication_exit
                    print("Error sending counting")


                #requests.post(url, data=myobj, timeout=(1, 1))

        # store the trackable object in our dictionary
        trackableObjects[objectID] = to

        # draw both the ID of the object and the centroid of the
        # object on the output frame
        text = "ID {}".format(objectID)
        cv2.putText(frame, text, (centroid[0] - 10, centroid[1] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        cv2.circle(frame, (centroid[0], centroid[1]), 4, (0, 255, 0), -1)

    # construct a tuple of information we will be displaying on the
    # frame
    info = [
        ("Left of AB", total_left_AB),
        ("Right of AB", total_right_AB),
        ("Status", status),
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
