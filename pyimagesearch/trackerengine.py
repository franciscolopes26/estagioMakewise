from pyimagesearch.centroidtracker import CentroidTracker
from pyimagesearch.trackableobject import TrackableObject

class TrackerEngine ():
    def __init__(self,lable,maxDisappeared=40, maxDistance=50):
        super().__init__()
        # instantiate our centroid tracker, then initialize a list to store
        # each of our dlib correlation trackers, followed by a dictionary to
        # map each unique object ID to a TrackableObject
        self.label = lable
        self.ct = CentroidTracker(maxDisappeared=maxDisappeared, maxDistance=maxDistance, remove_callback=self.remove_callback)
        self.trackers = []
        self.trackableObjects = {}
        self.rects = []
        self.total_right_AB = 0
        self.total_left_AB = 0

    def updateCentroids(self,point_a, point_b):
     

        # use the centroid tracker to associate the (1) old object
        # centroids with (2) the newly computed object centroids
        objects =  self.ct.update( self.rects)

        # loop over the tracked objects
        for (objectID, centroid) in objects.items():
            # check to see if a trackable object exists for the current
            # object ID
            to = self.trackableObjects.get(objectID, None)

            # if there is no existing trackable object, create one
            if to is None:
                to = TrackableObject(objectID, centroid,self.label)

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
                        self.total_left_AB += 1
                    elif to.last_side == 'R':
                        self.total_right_AB += 1

            # store the trackable object in our dictionary
            self.trackableObjects[objectID] = to
        self.rects = []

    def get_counting_message(self ):
        if self.total_right_AB> 0 or self.total_left_AB>0:
            return {'enter': self.total_left_AB, "exit": self.total_right_AB, "class": self.label}
        else:
            return None

    def remove_callback(self, objectID ):
        del self.trackableObjects[objectID]

    def reset_counter(self):
        self.total_right_AB = 0
        self.total_left_AB = 0
