import collections
import cv2

Params = collections.namedtuple('Params', ['a', 'b', 'c'])


class TrackableObject:
    def __init__(self, objectID, centroid):
        # store the object ID, then initialize a list of centroids
        # using the current centroid
        self.objectID = objectID
        self.centroids = [centroid]

        # initialize a boolean used to indicate if the object has
        # already been counted or not
        self.counted = False

    def is_crossing_line(self, point_a, point_b):
        # this function will check if the line segment form by connection
        # the two last centroids cross the line segment form by the points a and b
        # if centroids size is less that two we don't have a line segment so we will return false
        if len(self.centroids) < 2:
            return False
        else:
            current_point = self.centroids[-1]
            prev_point = self.centroids[-2]
            return doIntersect(
                Point(current_point[0], current_point[1]),
                Point(prev_point[0], prev_point[1]),
                Point(point_a[0], point_a[1]),
                Point(point_b[0], point_b[1])
            )


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

# Given three colinear points p, q, r, the function checks if


# point q lies on line segment 'pr'
def onSegment(p, q, r):
    if ((q.x <= max(p.x, r.x)) and (q.x >= min(p.x, r.x)) and
            (q.y <= max(p.y, r.y)) and (q.y >= min(p.y, r.y))):
        return True
    return False


def orientation(p, q, r):
    # to find the orientation of an ordered triplet (p,q,r)
    # function returns the following values:
    # 0 : Colinear points
    # 1 : Clockwise points
    # 2 : Counterclockwise

    # See https://www.geeksforgeeks.org/orientation-3-ordered-points/amp/
    # for details of below formula.

    val = (float(q.y - p.y) * (r.x - q.x)) - (float(q.x - p.x) * (r.y - q.y))
    if (val > 0):

        # Clockwise orientation
        return 1
    elif (val < 0):

        # Counterclockwise orientation
        return 2
    else:

        # Colinear orientation
        return 0


# The main function that returns true if
# the line segment 'p1q1' and 'p2q2' intersect.
def doIntersect(p1, q1, p2, q2):
    # Find the 4 orientations required for
    # the general and special cases
    o1 = orientation(p1, q1, p2)
    o2 = orientation(p1, q1, q2)
    o3 = orientation(p2, q2, p1)
    o4 = orientation(p2, q2, q1)

    # General case
    if ((o1 != o2) and (o3 != o4)):
        return True

    # Special Cases

    # p1 , q1 and p2 are colinear and p2 lies on segment p1q1
    if ((o1 == 0) and onSegment(p1, p2, q1)):
        return True

    # p1 , q1 and q2 are colinear and q2 lies on segment p1q1
    if ((o2 == 0) and onSegment(p1, q2, q1)):
        return True

    # p2 , q2 and p1 are colinear and p1 lies on segment p2q2
    if ((o3 == 0) and onSegment(p2, p1, q2)):
        return True

    # p2 , q2 and q1 are colinear and q1 lies on segment p2q2
    if ((o4 == 0) and onSegment(p2, q1, q2)):
        return True

    # If none of the cases
    return False



# Small test code

if __name__ == '__main__':

    t = TrackableObject('1', (1, 1))
    a = (2, 0)
    b = (2, 2)
    totalUp = t.centroids[-1]
    totalDown = t.centroids[0]

    print("Test TrackableObject centroids with less than two")
    if t.is_crossing_line(a, b) == False:
        print("Test pass")
    else:
        print("Test fail")

    print("Test TrackableObject not crossing the line")
    t.centroids.append((0, 1))  # move the other direction away from the line
    if t.is_crossing_line(a, b) == False:
        print("Test pass")
    else:
        print("Test fail")

    print("Test TrackableObject crossing the line")
    t.centroids.append((3, 1))
    if t.is_crossing_line(a, b) == True:
        print("Test pass")
    else:
        print("Test fail")
