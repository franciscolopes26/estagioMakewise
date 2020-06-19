import collections
import cv2

from pyimagesearch.point import doIntersect, Point, onSegment


class TrackableObject:
    def __init__(self, objectID,centroid):
        # store the object ID, then initialize a list of centroids
        # using the current centroid
        self.objectID = objectID
        self.centroids = [centroid]


    def update_position(self, new_position):
        if new_position != self.centroids[-1]:
            self.centroids.append(new_position)

    def is_crossing_line(self, point_a, point_b):
        # this function will check if the line segment form by connection
        # the two last centroids cross the line segment form by the points a and b
        # if centroids size is less that two we don't have a line segment so we will return false
        if len(self.centroids) < 2:
            return False
        else:
            current_point = self.centroids[-1]
            current_point = Point(current_point[0], current_point[1])
            prev_point = self.centroids[-2]
            prev_point = Point(prev_point[0], prev_point[1])

            point_a = Point(point_a[0], point_a[1])
            point_b = Point(point_b[0], point_b[1])
            return (not onSegment(point_a, current_point, point_b)) and\
                   doIntersect(
                       prev_point,
                       current_point,
                       point_a,
                       point_b
                   )

    def is_on_the_left_of_line(self, point_a, point_b):
        current_point = self.centroids[-1]
        v1 = (point_a[0] - point_b[0], point_a[1] - point_b[1])
        v2 = (point_b[0] - current_point[0], point_b[1] - current_point[1])
        cross_product = v1[0] * v2[1] - v1[1] * v2[0]
        if cross_product != 0:
            if cross_product > 0:
                return False
            else:
                return True
        else:
            return False


# Small test code

if __name__ == '__main__':

    t = TrackableObject('1', (1, 1))
    a = (2, 0)
    b = (2, 2)

    print("Test TrackableObject centroids with less than two")
    if t.is_crossing_line(a, b) == False:
        print("Test pass")
    else:
        print("Test fail")
    print("Test TrackableObject is_on_the_left_of_line crossing the line")
    if t.is_on_the_left_of_line(a, b) == False:
        print("Test pass")
    else:
        print("Test fail")

    print("Test TrackableObject at (0, 1) is  crossing the line")
    t.update_position((0, 1))  # move the other direction away from the line
    if t.is_crossing_line(a, b) == False:
        print("Test pass")
    else:
        print("Test fail")

    print("Test TrackableObject is_on_the_left_of_line crossing the line")
    if t.is_on_the_left_of_line(a, b) == False:
        print("Test pass")
    else:
        print("Test fail")

    print("Test TrackableObject at (2, 1) is not crossing the line")
    t.update_position((2, 1))  # move the other direction away from the line
    if t.is_crossing_line(a, b) == False:
        print("Test pass")
    else:
        print("Test fail")

    print("Test TrackableObject is_on_the_left_of_line crossing the line")
    if t.is_on_the_left_of_line(a, b) == False:
        print("Test pass")
    else:
        print("Test fail")

    print("Test TrackableObject at (3, 1) crossing the line")
    t.update_position((3, 1))
    if t.is_crossing_line(a, b) == True:
        print("Test pass")
    else:
        print("Test fail")

    print("Test TrackableObject is_on_the_left_of_line crossing the line")
    if t.is_on_the_left_of_line(a, b) == True:
        print("Test pass")
    else:
        print("Test fail")