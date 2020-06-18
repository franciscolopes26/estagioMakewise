import collections
import cv2

from pyimagesearch.point import doIntersect, Point


class TrackableObject:
    def __init__(self, objectID, centroid):
        # store the object ID, then initialize a list of centroids
        # using the current centroid
        self.objectID = objectID
        self.centroids = [centroid]
        self.secure = None


    def is_crossing_line(self, point_a, point_b):
        # this function will check if the line segment form by connection
        # the two last centroids cross the line segment form by the points a and b
        # if centroids size is less that two we don't have a line segment so we will return false
        if len(self.centroids) < 2:
            return False
        else:
            current_point = self.centroids[-1]
            prev_point = self.centroids[-2]
            if self.secure == None \
                    and doIntersect(
                Point(current_point[0], current_point[1]),
                Point(prev_point[0], prev_point[1]),
                Point(point_a[0], point_a[1]),
                Point(point_b[0], point_b[1])
            ):  # Primeira vez, guarda o ultimo ponto antes da linha
                self.secure = (prev_point[0], prev_point[1])
                return False
            if (self.secure != None) \
                    and doIntersect(
                    Point(current_point[0], current_point[1]),
                    Point(self.secure[0], self.secure[1]),
                    Point(point_a[0], point_a[1]),
                    Point(point_b[0], point_b[1])
                ): #Segunda+ vez, verifica se cruzou do ultimo ponto antes da linha
                return True
            return False

    def is_on_the_left_of_line(self, point_a, point_b):
        current_point = self.centroids[-1]
        teste = ((current_point[0] - point_a[0]) * (point_b[1] - point_a[1]))\
                - ((current_point[1] - point_a[1]) * (point_b[0] - point_a[0]))

        # condicionar para quem pisar na linha e voltar para trás não contar

        if teste < 0:
            self.secure = None
            return True
        if teste == 0: # em cima da linha e anterior ter cruzado a linha
            return False
        self.secure = None
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

    print("Test TrackableObject not crossing the line")
    t.centroids.append((0, 1))  # move the other direction away from the line
    if t.is_crossing_line(a, b) == False:
        print("Test pass")
    else:
        print("Test fail")

    print("Test TrackableObject is_on_the_left_of_line crossing the line")
    if t.is_on_the_left_of_line(a, b) == False:
        print("Test pass")
    else:
        print("Test fail")

    print("Test TrackableObject crossing the line")
    t.centroids.append((3, 1))
    if t.is_crossing_line(a, b) == True:
        print("Test pass")
    else:
        print("Test fail")

    print("Test TrackableObject is_on_the_left_of_line crossing the line")
    if t.is_on_the_left_of_line(a, b) == True:
        print("Test pass")
    else:
        print("Test fail")
