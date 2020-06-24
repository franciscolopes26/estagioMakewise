
from pyimagesearch.point import doIntersect, Point, onSegment, orientation


class TrackableObject:
    def __init__(self, objectID,centroid):
        # store the object ID, then initialize a list of centroids
        # using the current centroid
        self.objectID = objectID
        self.centroids = [centroid]
        self.last_side = None


    def update_position(self, new_position):
        if new_position[0] == self.centroids[-1][0] and new_position[1] == self.centroids[-1][1]:
            # in the same place nothing change
            return
        else:
            self.centroids.append(new_position)


    def is_crossing_line(self, point_a, point_b):
        # this function will check if the line segment form by connection
        # the two last centroids cross the line segment form by the points a and b
        # if centroids size is less that two we don't have a line segment so we will return false
        if len(self.centroids) < 2:
            return False

        current_point = self.centroids[-1]
        current_point = Point(current_point[0], current_point[1])
        prev_point = self.centroids[-2]
        prev_point = Point(prev_point[0], prev_point[1])

        point_a = Point(point_a[0], point_a[1])
        point_b = Point(point_b[0], point_b[1])
        oriten = orientation(point_a, point_b,current_point)
        if oriten == 0:
            return False
        elif oriten == 1:
            new_side = 'R'
        elif oriten == 2:
            new_side = 'L'

        if self.last_side is None:
            self.last_side = new_side
        elif new_side != self.last_side:
            self.last_side = new_side
            return doIntersect(
                       prev_point,
                       current_point,
                       point_a,
                       point_b
                   )

        self.last_side = new_side
        return False



# Small test code

if __name__ == '__main__':

    t = TrackableObject('1', (1, 1))
    a = (2, 0)
    b = (2, 2)

